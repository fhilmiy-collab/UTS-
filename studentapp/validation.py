"""Validasi data mahasiswa (defensive programming).

Aturan: NIM/nama/prodi = teks tidak kosong (setelah strip);
nilai & kehadiran = bilangan bulat 0-100. Angka 0 SAH; None, "", True, 101 TIDAK sah.
"""

from .exceptions import ValidationError

MIN_VALUE = 0
MAX_VALUE = 100
TEXT_FIELDS = {"nim": "NIM", "name": "Nama", "program": "Program studi"}
NUMBER_FIELDS = {"score": "Nilai", "attendance": "Kehadiran"}


def is_valid_text(value):
    """True jika value berupa str yang tidak kosong setelah strip()."""
    return isinstance(value, str) and bool(value.strip())


def is_valid_number(value):
    """True jika value bertipe int (bukan bool) dalam rentang 0-100.

    type(value) is int menolak True; perbandingan rentang menerima 0.
    """
    return type(value) is int and MIN_VALUE <= value <= MAX_VALUE


def parse_int(value, label):
    """Ubah teks (mis. dari CSV/input) menjadi int; nilai non-teks dikembalikan apa adanya.

    Raises: ValidationError jika teks kosong atau bukan bilangan bulat.
    """
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        raise ValidationError(f"{label} wajib diisi")
    try:
        return int(text)
    except ValueError:
        raise ValidationError(f"{label} harus bilangan bulat, diterima '{text}'") from None


def validate_text_field(value, label):
    """Kembalikan teks yang sudah di-strip atau raise ValidationError."""
    if not is_valid_text(value):
        raise ValidationError(f"{label} wajib berupa teks tidak kosong")
    return value.strip()


def validate_number_field(value, label):
    """Kembalikan int 0-100 atau raise ValidationError."""
    number = parse_int(value, label)
    if not is_valid_number(number):
        raise ValidationError(f"{label} harus bilangan bulat {MIN_VALUE}-{MAX_VALUE}")
    return number


def validate_student(raw):
    """Validasi satu record mentah -> dict bersih {nim,name,program,score,attendance}.

    Guard clause: data bukan dict langsung ditolak.
    """
    if not isinstance(raw, dict):
        raise ValidationError("Data harus berupa dictionary/baris dengan kolom lengkap")
    clean = {key: validate_text_field(raw.get(key), label) for key, label in TEXT_FIELDS.items()}
    clean.update(
        {key: validate_number_field(raw.get(key), label) for key, label in NUMBER_FIELDS.items()}
    )
    return clean
