"""Format teks laporan. Hanya mengembalikan string (print dilakukan pemanggil)."""

EMPTY_MESSAGE = "Belum ada data."


def format_row(number, student):
    """'3. 2301003 | Citra | Teknik Komputer | 92 | Lulus dengan Pujian'."""
    return (f"{number}. {student['nim']} | {student['name']} | {student['program']} | "
            f"{student['score']} | {student['status']}")


def format_table(students_with_status):
    """Daftar bernomor; list kosong -> pesan 'Belum ada data.'."""
    if not students_with_status:
        return EMPTY_MESSAGE
    return "\n".join(format_row(n, s) for n, s in enumerate(students_with_status, start=1))


def format_detail(student):
    """Detail satu mahasiswa (multi-baris)."""
    return (f"NIM       : {student['nim']}\nNama      : {student['name']}\n"
            f"Prodi     : {student['program']}\nNilai     : {student['score']}\n"
            f"Kehadiran : {student['attendance']}%\nStatus    : {student['status']}")


def format_summary(summary):
    """Teks ringkasan dari dict summarize(); kosong -> 'Belum ada data.'."""
    if summary["jumlah"] == 0:
        return EMPTY_MESSAGE
    return (f"Jumlah: {summary['jumlah']}\n"
            f"Rata-rata: {summary['rata_rata']:.2f}\n"
            f"Minimum: {summary['minimum']} | Maksimum: {summary['maksimum']}\n"
            f"Lulus: {summary['lulus']}\n"
            f"Ada nilai >= 90: {summary['ada_nilai_90']}")


def format_recap(recap):
    """Rekap per program studi dari dict recap_per_program()."""
    if not recap:
        return EMPTY_MESSAGE
    lines = ["Rekap per program studi:"]
    for program in sorted(recap):
        info = recap[program]
        lines.append(f"- {program}: {info['jumlah']} mahasiswa, "
                     f"rata-rata {info['rata_rata']:.2f}, lulus {info['lulus']}")
    return "\n".join(lines)
