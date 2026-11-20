"""Orkestrasi: bersihkan data mentah -> analisis -> simpan hasil."""

import logging
from pathlib import Path

from . import analysis, records, report, storage
from .exceptions import ValidationError
from .validation import validate_student

logger = logging.getLogger("studentapp.pipeline")


def clean_records(raw_records):
    """Validasi + hapus duplikat NIM.

    Returns: (valid, rejected) ; rejected = [{"record": no, "reason": str}, ...] urut nomor.
    """
    pairs, rejected = [], []
    for number, raw in enumerate(raw_records, start=1):
        try:
            pairs.append((number, validate_student(raw)))
        except ValidationError as error:
            logger.warning("Record %d ditolak: %s", number, error)
            rejected.append({"record": number, "reason": str(error)})
    unique, duplicates = records.remove_duplicates(pairs, key=lambda pair: pair[1]["nim"])
    for number, student in duplicates:
        logger.warning("Record %d ditolak: NIM duplikat", number)
        rejected.append({"record": number, "reason": f"NIM {student['nim']} duplikat"})
    rejected.sort(key=lambda item: item["record"])
    return [student for _, student in unique], rejected


def save_results(students, output_dir):
    """Simpan hasil (dengan status + ringkasan) ke JSON dan CSV. Return list path."""
    output_dir = Path(output_dir)
    rows = analysis.with_status(students)
    payload = {
        "ringkasan": analysis.summarize(students),
        "rekap_per_prodi": analysis.recap_per_program(students),
        "mahasiswa": rows,
    }
    return [
        storage.write_json(output_dir / "hasil_mahasiswa.json", payload),
        storage.write_csv(output_dir / "hasil_mahasiswa.csv", rows, storage.OUTPUT_FIELDS),
    ]


def run_batch(input_path, output_dir):
    """Mode non-interaktif: baca -> bersihkan -> analisis -> cetak -> simpan. Return 0."""
    raw = storage.read_records(input_path)
    valid, rejected = clean_records(raw)
    print(f"Dibaca: {len(raw)} record | Valid: {len(valid)} | Ditolak: {len(rejected)}")
    for item in rejected:
        print(f"  - record {item['record']}: {item['reason']}")
    print()
    print(report.format_table(analysis.with_status(valid)))
    print()
    print(report.format_summary(analysis.summarize(valid)))
    print()
    print(report.format_recap(analysis.recap_per_program(valid)))
    paths = save_results(valid, output_dir)
    rejected_path = storage.write_csv(Path(output_dir) / "ditolak.csv", rejected, ["record", "reason"])
    print()
    for path in [*paths, rejected_path]:
        print(f"Tersimpan: {path}")
    logger.info("Batch selesai: %d valid, %d ditolak", len(valid), len(rejected))
    return 0
