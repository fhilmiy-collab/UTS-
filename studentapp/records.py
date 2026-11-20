"""Manipulasi koleksi mahasiswa: tambah, cari, indeks, hapus duplikat (tanpa mutasi input)."""

import logging

from .exceptions import DuplicateNimError
from .validation import validate_student

logger = logging.getLogger("studentapp.records")


def add_student(students, raw):
    """Kembalikan list BARU berisi mahasiswa lama + yang baru (list asli tidak diubah).

    Raises: ValidationError (data tidak sah), DuplicateNimError (NIM sudah ada).
    """
    clean = validate_student(raw)
    if clean["nim"] in {s["nim"] for s in students}:
        raise DuplicateNimError(f"NIM {clean['nim']} sudah terdaftar")
    logger.info("Mahasiswa ditambahkan")
    return [*students, clean]


def build_index(students):
    """Dict {nim: mahasiswa} untuk pencarian cepat."""
    return {s["nim"]: s for s in students}


def find_by_nim(students, nim):
    """Cari mahasiswa dengan NIM tertentu; None jika tidak ada.

    Memakai continue (lewati NIM kosong), break (ketemu), dan for-else (tidak ketemu).
    """
    target = nim.strip() if isinstance(nim, str) else ""
    found = None
    for student in students:
        if not student.get("nim"):
            continue
        if student["nim"] == target:
            found = student
            break
    else:
        logger.debug("NIM tidak ditemukan")
    return found


def remove_duplicates(items, key):
    """Pisahkan item unik (kemunculan pertama) dan duplikat berdasarkan key(item).

    Returns: (unique, duplicates). Memakai set untuk melacak kunci yang sudah terlihat.
    """
    seen = set()
    unique, duplicates = [], []
    for item in items:
        identity = key(item)
        (duplicates if identity in seen else unique).append(item)
        seen.add(identity)
    return unique, duplicates
