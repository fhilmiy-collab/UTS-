"""Antarmuka command line: menu interaktif yang berulang sampai pengguna keluar."""

import logging

from . import analysis, pipeline, records, report, storage
from .exceptions import DuplicateNimError, StudentError, ValidationError
from .validation import validate_number_field, validate_text_field

logger = logging.getLogger("studentapp.cli")
DEFAULT_INPUT = "data/mahasiswa_input.csv"
DEFAULT_OUTPUT_DIR = "output"

MENU = """
=== STUDENT DATA ANALYZER ===
1. Muat data dari file (CSV/JSON)
2. Tambah mahasiswa
3. Tampilkan daftar
4. Cari berdasarkan NIM
5. Filter berdasarkan status
6. Rekap per program studi
7. Ringkasan
8. Simpan hasil (JSON + CSV)
9. Keluar"""


def read_text(prompt, label):
    """Ulangi input sampai teks tidak kosong."""
    while True:
        try:
            return validate_text_field(input(prompt), label)
        except ValidationError as error:
            logger.warning("Input ditolak: %s", error)
            print(f"Input salah: {error}")


def read_number(prompt, label):
    """Ulangi input sampai bilangan bulat 0-100 (0 diterima)."""
    while True:
        try:
            return validate_number_field(input(prompt), label)
        except ValidationError as error:
            logger.warning("Input ditolak: %s", error)
            print(f"Input salah: {error}")


def action_load(students):
    path = input(f"Path file [{DEFAULT_INPUT}]: ").strip() or DEFAULT_INPUT
    valid, rejected = pipeline.clean_records(storage.read_records(path))
    print(f"{len(valid)} data valid, {len(rejected)} ditolak.")
    for item in rejected:
        print(f"  - record {item['record']}: {item['reason']}")
    return valid


def action_add(students):
    raw = {
        "nim": read_text("NIM: ", "NIM"),
        "name": read_text("Nama: ", "Nama"),
        "program": read_text("Program studi: ", "Program studi"),
        "score": read_number("Nilai (0-100): ", "Nilai"),
        "attendance": read_number("Kehadiran (0-100): ", "Kehadiran"),
    }
    updated = records.add_student(students, raw)
    print("Data ditambahkan.")
    return updated


def action_list(students):
    print(report.format_table(analysis.with_status(students)))
    return students


def action_search(students):
    nim = input("NIM yang dicari: ").strip()
    if not nim:
        print("NIM tidak boleh kosong.")
        return students
    found = records.find_by_nim(students, nim)
    if found is None:
        print("Mahasiswa tidak ditemukan.")
    else:
        print(report.format_detail(analysis.with_status([found])[0]))
    return students


def action_filter(students):
    for number, status in enumerate(analysis.STATUSES, start=1):
        print(f"{number}. {status}")
    choice = input("Pilih status: ").strip()
    if not (choice.isdigit() and 1 <= int(choice) <= len(analysis.STATUSES)):
        logger.warning("Pilihan status tidak valid")
        print("Pilihan status tidak valid.")
        return students
    status = analysis.STATUSES[int(choice) - 1]
    result = analysis.filter_by_status(students, status)
    print(report.format_table(result) if result else f"Tidak ada mahasiswa berstatus {status}.")
    return students


def action_recap(students):
    print(report.format_recap(analysis.recap_per_program(students)))
    return students


def action_summary(students):
    print(report.format_summary(analysis.summarize(students)))
    return students


def action_save(students):
    if not students:
        print("Belum ada data untuk disimpan.")
        return students
    for path in pipeline.save_results(students, DEFAULT_OUTPUT_DIR):
        print(f"Tersimpan: {path}")
    return students


ACTIONS = {"1": action_load, "2": action_add, "3": action_list, "4": action_search,
           "5": action_filter, "6": action_recap, "7": action_summary, "8": action_save}


def run_menu():
    """Loop menu utama. Error yang dapat dipulihkan tidak menghentikan program."""
    students = []
    logger.info("Menu dibuka")
    while True:
        print(MENU)
        try:
            choice = input("Pilihan: ").strip()
        except EOFError:
            print("\nInput berakhir. Selesai.")
            break
        if choice == "9":
            print("Selesai.")
            break
        action = ACTIONS.get(choice)
        if action is None:
            logger.warning("Pilihan menu tidak tersedia")
            print("Pilihan tidak tersedia.")
            continue
        try:
            students = action(students)
        except DuplicateNimError as error:
            logger.warning("%s", error)
            print(f"Ditolak: {error}")
        except StudentError as error:
            logger.error("%s: %s", type(error).__name__, error)
            print(f"Gagal: {error}")
        except EOFError:
            print("\nInput berakhir. Selesai.")
            break
    logger.info("Program selesai")
    return 0
