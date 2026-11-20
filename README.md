# Student Data Analyzer 

**command line** berbasis Python untuk mengolah data
mahasiswa: memuat CSV/JSON, memvalidasi, menentukan status, mencari, memfilter, merekap,
lalu menyimpan hasil ke JSON dan CSV.

- Nama / NIM / Kelas : Fauzi Hilmiy Ahmad
- Dosen pengampu     : Muhammad Koprawi, S.Kom., M.Eng
- Repository         : (https://github.com/fhilmiy-collab/UTS-.git)

## 1. Persyaratan & Dependency
- Python **3.10+** (diuji dengan 3.12). Cek: `python --version` (atau `python3 --version`).
- **Tanpa package eksternal.** `requirements.txt` hanya berisi komentar.
  Modul yang dipakai: `csv`, `json`, `logging`, `argparse`, `pathlib`, `unittest`.
- Virtual environment bersifat opsional (folder `.venv/` jangan dikumpulkan):
  ```bash
  python -m venv .venv
  source .venv/bin/activate        # macOS/Linux
  .venv\Scripts\activate           # Windows
  python -m pip install -r requirements.txt   # tidak memasang apa pun
  ```

## 2. Cara Menjalankan (dari folder proyek)
```bash
# a) Mode menu interaktif (berulang sampai memilih 9. Keluar)
python main.py

# b) Mode batch: baca -> validasi -> analisis -> simpan, tanpa menu
python main.py --batch --input data/mahasiswa_input.csv  --output output
python main.py --batch --input data/mahasiswa_input.json --output output/json

# c) Unit test (20 test)
python -m unittest discover -s tests -v

# d) Skenario debugging (bug 1 = traceback, bug 2 = bug logika)
python debug/debug_scenario.py 1
python debug/debug_scenario.py 2
```
Opsi: `--debug` mengaktifkan log level DEBUG. Log ditulis ke `logs/app.log`.

Menu: `1` muat file, `2` tambah mahasiswa, `3` daftar, `4` cari NIM, `5` filter status,
`6` rekap per prodi, `7` ringkasan, `8` simpan hasil, `9` keluar.

## 3. Struktur Program
```
student-data-analyzer/
├── main.py                  # titik masuk (argparse -> mode menu / batch)
├── requirements.txt
├── README.md
├── studentapp/              # PACKAGE buatan sendiri
│   ├── __init__.py          # API publik package
│   ├── exceptions.py        # StudentError, ValidationError, DuplicateNimError, DataFileError
│   ├── validation.py        # aturan validasi (guard clause)
│   ├── analysis.py          # status, filter, group, ringkasan (fungsi murni)
│   ├── records.py           # tambah (tanpa mutasi), cari, hapus duplikat
│   ├── storage.py           # baca/tulis CSV & JSON
│   ├── pipeline.py          # orkestrasi bersihkan -> analisis -> simpan
│   ├── report.py            # format teks (return string)
│   ├── cli.py               # menu interaktif (satu-satunya yang memakai input())
│   └── logging_setup.py     # konfigurasi logging ke file
├── data/                    # contoh INPUT (normal + edge case)
├── output/                  # contoh OUTPUT (hasil_mahasiswa.csv/json, ditolak.csv)
├── contoh_output/           # tangkapan keluaran terminal & log
├── tests/test_app.py        # unit test
├── debug/debug_scenario.py  # skenario debugging
└── docs/                    # lembar jawaban PDF
```
**Alur dependensi** (tanpa siklus): `main -> cli -> pipeline -> (records, analysis, storage, report) -> validation -> exceptions`.

## 4. Format Data
**Input CSV** (header wajib): `nim,name,program,score,attendance`
**Input JSON**: list objek dengan kunci yang sama (atau `{"students": [...]}`).
**Output**: `hasil_mahasiswa.csv` (+ kolom `status`), `hasil_mahasiswa.json`
(`ringkasan`, `rekap_per_prodi`, `mahasiswa`), `ditolak.csv` (nomor record + alasan).

## 5. Aturan Validasi
- NIM, nama, prodi: teks tidak kosong setelah spasi di tepi dihapus.
- Nilai & kehadiran: bilangan bulat **0-100**. `0` sah; `None`, string kosong, `True`, `101`, `-1`, `abc` ditolak.
- NIM tidak boleh duplikat (kemunculan pertama dipertahankan).

## 6. Aturan Status (urutan prioritas)
| Kondisi | Status |
|---|---|
| kehadiran < 75 | Peringatan Kehadiran |
| nilai >= 90 **dan** kehadiran >= 90 | Lulus dengan Pujian |
| nilai >= 80 | Lulus |
| nilai >= 60 | Remedial |
| lainnya | Tidak Lulus |

## 7. Penanganan Error
| Kondisi | Penanganan |
|---|---|
| File tidak ada / format salah / JSON rusak / kolom CSV kurang | `DataFileError` -> pesan jelas, exit code 1 (batch) atau kembali ke menu |
| Record tidak valid | `ValidationError` -> record ditolak, dicatat di `ditolak.csv` + log WARNING, proses lanjut |
| NIM duplikat | `DuplicateNimError` -> ditolak |
| Input menu/angka salah | diminta ulang (loop), program tetap hidup |
| Daftar kosong | "Belum ada data." tanpa pembagian dengan nol |
| `Ctrl+C` / akhir input (EOF) | keluar dengan rapi |

## 8. Sumber Referensi, Library, dan Bantuan AI
- Modul Praktikum 1-7 TK091 (Muhammad Koprawi), dokumentasi Python https://docs.python.org/3/ , PEP 8.
- Library: hanya standard library Python (tidak ada dependency eksternal).
- Bantuan AI: kerangka kode, dokumentasi, dan contoh uji dibuat dengan bantuan **Claude (Anthropic)**,
  kemudian dijalankan, diuji, dan dipelajari oleh penulis.
