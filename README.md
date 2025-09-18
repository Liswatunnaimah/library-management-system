![CI](https://github.com/Liswatunnaimah/library-management-system/actions/workflows/ci.yml/badge.svg)

# Library Management System (CLI)

Aplikasi Command Line Interface (CLI) untuk mengelola katalog perpustakaan.
Proyek ini dirancang untuk melatih keterampilan Python, data handling, reporting, serta praktik software engineering modern.
Selain sebagai latihan teknis, aplikasi ini juga dapat digunakan untuk mini perpustakaan sederhana (sekolah, komunitas, atau pribadi).

---

## Fitur Utama

* **Manajemen Buku (CRUD)**

  * Tambah buku baru dengan validasi tahun terbit.
  * Update informasi spesifik (judul, penulis, penerbit, tahun).
  * Hapus buku dengan proteksi: tidak dapat menghapus buku yang sedang dipinjam. Data buku yang dihapus diarsipkan ke `deleted_books.json`.
  * Pencarian berdasarkan ID, field tertentu, atau keyword.

* **Borrowing dan Returning**

  * Pinjam: status berubah menjadi `borrowed`, tanggal pinjam dan kembali otomatis tercatat (default 7 hari), counter jumlah peminjaman bertambah.
  * Kembalikan: status kembali ke `available`, tanggal pinjam dan kembali dikosongkan.

* **Reporting**

  * Ringkasan katalog (total, available, borrowed).
  * Daftar buku yang sedang dipinjam.
  * Export laporan ke CSV dan visualisasi chart PNG.

* **Analytics**

  * Top-N penulis, penerbit, dan judul berdasarkan frekuensi peminjaman.
  * Export hasil analitik ke CSV, Excel (.xlsx), dan chart PNG dengan label angka.

* **Export Management**

  * Semua hasil export disimpan di folder `outputs/` dengan nama file bertimestamp sehingga mudah dilacak dan tidak menimpa file sebelumnya.

---

## Arsitektur Sistem

Mengacu pada dokumentasi desain:

* **Data Layer (`data/`)**

  * `books.json` menyimpan katalog aktif.
  * `deleted_books.json` menyimpan arsip buku yang dihapus dalam format JSON Lines.

* **Application Layer (`src/library_manager/`)**

  * `cli.py` berisi navigasi menu CLI.
  * `services.py` berisi logika utama (CRUD, borrowing, reporting, analytics, export).
  * `utils.py` menyediakan helper input dan validasi.
  * `__init__.py` menandai package.

* **Output Layer (`outputs/`)**

  * Menyimpan seluruh hasil laporan dan analitik (CSV, Excel, PNG).

* **Supporting Files**

  * `pyproject.toml` untuk metadata dan dependency.
  * `.gitignore` untuk pengecualian venv, cache, outputs.
  * `docs/` untuk arsitektur dan flowchart program.

---

## Struktur Project

```
library-management-system/
├─ data/
│  ├─ books.json
│  └─ deleted_books.json
├─ outputs/
├─ docs/
│  ├─ architecture.md
│  ├─ flow.md
│  └─ program-flow.png
├─ src/
│  └─ library_manager/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ services.py
│     └─ utils.py
├─ tests/
│  ├─ test_smoke.py
│  ├─ test_cli.py
│  └─ test_export.py
├─ pyproject.toml
└─ .gitignore
```

---

## Technology Stack

* Python 3.10+
* tabulate → menampilkan tabel di terminal
* matplotlib (backend Agg) → export chart PNG
* openpyxl → export data ke Excel (.xlsx)
* pytest → unit test dan end-to-end smoke test
* pyproject.toml (PEP 621) → dependency management dan packaging

---

## Cara Menjalankan

### Windows (PowerShell)

```
cd path\to\library-management-system

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -e .
```

Jalankan aplikasi:

```
library-cli
# atau
python -m library_manager.cli
```

### macOS / Linux

```
cd path/to/library-management-system

python3 -m venv .venv
source .venv/bin/activate

pip install -e .

library-cli
```

Jika PowerShell memblokir script:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Testing

Proyek ini mencakup beberapa test berbasis pytest:

* `test_smoke.py` → memastikan modul utama dapat diimport dan file data valid.
* `test_cli.py` → end-to-end smoke test CLI dengan mock input.
* `test_export.py` → memastikan fungsi export menghasilkan file CSV di direktori sementara tanpa menimpa folder asli.

Jalankan:

```
pytest -q
```

Hasil yang diharapkan:

```
........                                                                 [100%]
8 passed in 3.5s
```

---

## Flow dan Dokumentasi

* Arsitektur dan catatan desain: `docs/architecture.md`
* Flowchart interaksi CLI: `docs/flow.md` dan `docs/program-flow.png`

---

## Contoh Output

Ringkasan katalog:

```
Total buku aktif : 48
Tersedia         : 33
Sedang dipinjam  : 15
```

Top-5 penulis:

```
+---------------+------------------+----------------+
| penulis       |   total_dipinjam |   jumlah_judul |
+===============+==================+================+
| Tere Liye     |               21 |              4 |
| Dan Brown     |               19 |              3 |
| Andrea Hirata |               15 |              2 |
| John Green    |               15 |              2 |
| Pidi Baiq     |               15 |              2 |
+---------------+------------------+----------------+
```

---

