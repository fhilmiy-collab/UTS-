"""Analisis data: status, filter, pengelompokan, rekapitulasi (fungsi murni, tanpa print/input)."""

STATUS_WARNING = "Peringatan Kehadiran"
STATUS_HONORS = "Lulus dengan Pujian"
STATUS_PASS = "Lulus"
STATUS_REMEDIAL = "Remedial"
STATUS_FAIL = "Tidak Lulus"
STATUSES = (STATUS_WARNING, STATUS_HONORS, STATUS_PASS, STATUS_REMEDIAL, STATUS_FAIL)
PASSING = frozenset({STATUS_PASS, STATUS_HONORS})


def determine_status(score, attendance):
    """Tentukan status. Urutan prioritas penting (kehadiran diperiksa pertama).

    Args: score (int 0-100), attendance (int 0-100).
    Returns: salah satu dari STATUSES.
    """
    if attendance < 75:
        return STATUS_WARNING
    if score >= 90 and attendance >= 90:
        return STATUS_HONORS
    if score >= 80:
        return STATUS_PASS
    if score >= 60:
        return STATUS_REMEDIAL
    return STATUS_FAIL


def with_status(students):
    """List baru berisi salinan tiap mahasiswa + kunci 'status' (data asli tidak diubah)."""
    return [{**s, "status": determine_status(s["score"], s["attendance"])} for s in students]


def filter_by_status(students, status):
    """Mahasiswa (dengan status) yang statusnya == status."""
    return [s for s in with_status(students) if s["status"] == status]


def unique_programs(students):
    """Set program studi unik (set comprehension)."""
    return {s["program"] for s in students}


def group_by_program(students):
    """Dict {program: [mahasiswa, ...]} (pengelompokan)."""
    groups = {}
    for student in students:
        groups.setdefault(student["program"], []).append(student)
    return groups


def summarize(students):
    """Rekap: jumlah, rata-rata, min, max, jumlah lulus, ada nilai >= 90.

    List kosong aman: tidak ada pembagian dengan nol (nilai None).
    """
    if not students:
        return {"jumlah": 0, "rata_rata": None, "minimum": None, "maksimum": None,
                "lulus": 0, "ada_nilai_90": False}
    scores = [s["score"] for s in students]
    return {
        "jumlah": len(scores),
        "rata_rata": sum(scores) / len(scores),
        "minimum": min(scores),
        "maksimum": max(scores),
        "lulus": sum(1 for s in students if determine_status(s["score"], s["attendance"]) in PASSING),
        "ada_nilai_90": any(score >= 90 for score in scores),
    }


def recap_per_program(students):
    """Dict {program: summarize(kelompok)} (dictionary comprehension)."""
    return {program: summarize(group) for program, group in group_by_program(students).items()}
