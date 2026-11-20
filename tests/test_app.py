"""Unit test (unittest, standard library). Jalankan: python -m unittest discover -s tests -v"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from studentapp import analysis, pipeline, records, report, storage
from studentapp.exceptions import DataFileError, DuplicateNimError, ValidationError
from studentapp.validation import is_valid_number, validate_student

OK = {"nim": "1", "name": "Andi", "program": "TK", "score": 80, "attendance": 90}


def student(nim="1", score=80, attendance=90, program="TK"):
    return {"nim": nim, "name": "N" + nim, "program": program, "score": score, "attendance": attendance}


class TestStatus(unittest.TestCase):
    def test_batas_nilai(self):
        # kehadiran 80: bukan peringatan, bukan pujian
        cases = {59: "Tidak Lulus", 60: "Remedial", 79: "Remedial", 80: "Lulus", 89: "Lulus", 90: "Lulus"}
        for score, expected in cases.items():
            with self.subTest(score=score):
                self.assertEqual(analysis.determine_status(score, 80), expected)

    def test_batas_kehadiran(self):
        self.assertEqual(analysis.determine_status(95, 74), "Peringatan Kehadiran")
        self.assertEqual(analysis.determine_status(95, 75), "Lulus")
        self.assertEqual(analysis.determine_status(95, 89), "Lulus")
        self.assertEqual(analysis.determine_status(95, 90), "Lulus dengan Pujian")

    def test_prioritas_dewi(self):
        self.assertEqual(analysis.determine_status(88, 70), "Peringatan Kehadiran")

    def test_nol_bukan_data_hilang(self):
        self.assertEqual(analysis.determine_status(0, 80), "Tidak Lulus")


class TestValidation(unittest.TestCase):
    def test_angka(self):
        self.assertTrue(is_valid_number(0))
        self.assertTrue(is_valid_number(100))
        for bad in (None, "", -1, 101, True, 80.5, "80"):
            with self.subTest(bad=bad):
                self.assertFalse(is_valid_number(bad))

    def test_student_valid_dan_strip(self):
        raw = {"nim": " 1 ", "name": " Andi ", "program": " TK ", "score": "0", "attendance": "100"}
        self.assertEqual(validate_student(raw),
                         {"nim": "1", "name": "Andi", "program": "TK", "score": 0, "attendance": 100})

    def test_student_tidak_valid(self):
        bad_inputs = [
            None, {**OK, "name": "   "}, {**OK, "nim": None}, {**OK, "score": 101},
            {**OK, "score": True}, {**OK, "score": ""}, {**OK, "score": "abc"}, {**OK, "attendance": -1},
        ]
        for raw in bad_inputs:
            with self.subTest(raw=raw):
                with self.assertRaises(ValidationError):
                    validate_student(raw)


class TestRecords(unittest.TestCase):
    def test_add_tanpa_mutasi(self):
        original = [OK]
        updated = records.add_student(original, {**OK, "nim": "2"})
        self.assertEqual(len(original), 1)
        self.assertEqual(len(updated), 2)

    def test_nim_duplikat(self):
        with self.assertRaises(DuplicateNimError):
            records.add_student([OK], dict(OK))

    def test_cari(self):
        data = [{"nim": "", "name": "Rusak"}, OK]
        self.assertEqual(records.find_by_nim(data, "1")["name"], "Andi")
        self.assertIsNone(records.find_by_nim(data, "9999999"))
        self.assertIsNone(records.find_by_nim(data, ""))

    def test_remove_duplicates(self):
        unique, dups = records.remove_duplicates([1, 2, 1, 3, 2], key=lambda x: x)
        self.assertEqual((unique, dups), ([1, 2, 3], [1, 2]))


class TestAnalysis(unittest.TestCase):
    def test_ringkasan_kosong_tanpa_bagi_nol(self):
        self.assertEqual(report.format_summary(analysis.summarize([])), "Belum ada data.")

    def test_ringkasan_lima_data_awal(self):
        data = [student("1", 85, 92), student("2", 72, 81), student("3", 92, 95),
                student("4", 88, 70), student("5", 0, 80)]
        text = report.format_summary(analysis.summarize(data))
        self.assertEqual(text, "Jumlah: 5\nRata-rata: 67.40\nMinimum: 0 | Maksimum: 92\n"
                               "Lulus: 2\nAda nilai >= 90: True")

    def test_filter_dan_group(self):
        data = [student("1", 85, 92, "A"), student("2", 50, 92, "B"), student("3", 70, 92, "A")]
        self.assertEqual([s["nim"] for s in analysis.filter_by_status(data, "Lulus")], ["1"])
        self.assertEqual({k: len(v) for k, v in analysis.group_by_program(data).items()}, {"A": 2, "B": 1})
        self.assertEqual(analysis.unique_programs(data), {"A", "B"})

    def test_with_status_tidak_mengubah_asli(self):
        data = [student()]
        analysis.with_status(data)
        self.assertNotIn("status", data[0])


class TestFiles(unittest.TestCase):
    def test_file_tidak_ada(self):
        with self.assertRaises(DataFileError):
            storage.read_records("tidak_ada.csv")

    def test_format_tidak_didukung(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "a.txt")
            path.write_text("x")
            with self.assertRaises(DataFileError):
                storage.read_records(path)

    def test_json_rusak_dan_kolom_kurang(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_json = Path(tmp, "a.json")
            bad_json.write_text('{"students": [')
            with self.assertRaises(DataFileError):
                storage.read_records(bad_json)
            bad_csv = Path(tmp, "a.csv")
            bad_csv.write_text("nim,name\n1,A\n")
            with self.assertRaises(DataFileError):
                storage.read_records(bad_csv)

    def test_pipeline_csv_contoh(self):
        root = Path(__file__).resolve().parent.parent
        valid, rejected = pipeline.clean_records(storage.read_records(root / "data/mahasiswa_input.csv"))
        self.assertEqual(len(valid), 10)
        self.assertEqual(len(rejected), 5)

    def test_simpan_dan_baca_ulang(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline.save_results([student()], tmp)
            data = json.loads(Path(tmp, "hasil_mahasiswa.json").read_text(encoding="utf-8"))
            self.assertEqual(data["mahasiswa"][0]["status"], "Lulus")
            self.assertTrue(Path(tmp, "hasil_mahasiswa.csv").read_text().startswith("nim,name"))


if __name__ == "__main__":
    unittest.main()
