"""Exception khusus aplikasi (Praktikum 5)."""


class StudentError(Exception):
    """Induk semua error aplikasi ini."""


class ValidationError(StudentError, ValueError):
    """Data mahasiswa tidak memenuhi aturan validasi."""


class DuplicateNimError(ValidationError):
    """NIM sudah terdaftar."""


class DataFileError(StudentError):
    """File input/output tidak ada, rusak, atau formatnya tidak didukung."""
