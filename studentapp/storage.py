"""Pemrosesan file CSV/JSON (baca & tulis). Hanya I/O: tidak ada validasi bisnis."""

import csv
import json
import logging
from pathlib import Path

from .exceptions import DataFileError

logger = logging.getLogger("studentapp.storage")
REQUIRED_COLUMNS = {"nim", "name", "program", "score", "attendance"}
OUTPUT_FIELDS = ["nim", "name", "program", "score", "attendance", "status"]


def read_records(path):
    """Baca file .csv atau .json -> list dict mentah (belum divalidasi).

    Raises: DataFileError jika file tidak ada, rusak, kolom kurang, atau format tidak didukung.
    """
    path = Path(path)
    if not path.is_file():
        raise DataFileError(f"File tidak ditemukan: {path}")
    suffix = path.suffix.lower()
    if suffix not in {".csv", ".json"}:
        raise DataFileError(f"Format '{suffix}' tidak didukung (gunakan .csv atau .json)")
    try:
        records = _read_csv(path) if suffix == ".csv" else _read_json(path)
    except json.JSONDecodeError as error:
        raise DataFileError(f"JSON tidak valid di {path.name}: {error}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise DataFileError(f"Gagal membaca {path.name}: {error}") from error
    logger.info("Membaca %d record dari %s", len(records), path.name)
    return records


def _read_csv(path):
    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise DataFileError(f"Kolom CSV kurang: {', '.join(sorted(missing))}")
        return list(reader)


def _read_json(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if isinstance(data, dict) and isinstance(data.get("students"), list):
        data = data["students"]
    if not isinstance(data, list):
        raise DataFileError("JSON harus berupa list (atau objek dengan kunci 'students')")
    return data


def write_json(path, data):
    """Simpan data ke JSON (indent=2, UTF-8). Folder dibuat otomatis."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except OSError as error:
        raise DataFileError(f"Gagal menulis {path}: {error}") from error
    logger.info("Menulis JSON: %s", path)
    return path


def write_csv(path, rows, fieldnames):
    """Simpan list dict ke CSV dengan header."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
    except OSError as error:
        raise DataFileError(f"Gagal menulis {path}: {error}") from error
    logger.info("Menulis CSV: %s", path)
    return path
