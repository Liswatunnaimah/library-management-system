# Library Management System – Architecture & Design

## 1. Project Overview
Project ini adalah **aplikasi Command Line Interface (CLI)** untuk mengelola data katalog perpustakaan kecil hingga menengah.  
Tujuan utamanya:
- Menyediakan **alat sederhana** bagi user non-teknis untuk menambah, memperbarui, menghapus, meminjam, atau mengembalikan buku.
- Memberikan **laporan ringkas** kondisi koleksi (tersedia vs dipinjam).
- Menyediakan **analitik dasar** (Top-N penulis, penerbit, judul) berdasarkan frekuensi peminjaman.
- Menghasilkan **export otomatis** (CSV/XLSX/PNG chart) sebagai bukti dan dokumentasi.

Dengan desain ini, project dapat digunakan baik untuk **latihan manajemen data** maupun sebagai **mini tool praktis** di perpustakaan sederhana (misalnya sekolah, komunitas, atau pribadi).

---

## 2. High-Level Design
Arsitektur sistem terdiri dari beberapa komponen inti:

- **Data Layer (`data/`)**
  - `books.json`: menyimpan katalog utama (data aktif).
  - `deleted_books.json`: menyimpan arsip buku yang dihapus.
  - Format **JSON** dipilih karena sederhana, mudah dibaca manusia, dan portable.

- **Application Layer (`src/library_manager/`)**
  - `cli.py`: entrypoint, menampilkan menu/sub-menu, mengatur alur interaksi user.
  - `services.py`: core logic (CRUD, borrowing/returning, report, analytics, export).
  - `utils.py`: helper untuk validasi input & menjaga konsistensi UX.
  - `__init__.py`: marker package, mendefinisikan versi & modul publik.

- **Output Layer (`outputs/`)**
  - Menyimpan hasil laporan & analitik: CSV, XLSX, dan chart PNG.
  - Semua file diberi timestamp agar traceable dan tidak saling timpa.

- **Supporting Files**
  - `pyproject.toml`: metadata project, dependency (`tabulate`, `matplotlib`, `openpyxl`), dan entrypoint `library-cli`.
  - `.gitignore`: menghindari commit file sampah/venv/output.
  - (opsional) `tests/` untuk smoke test dan `docs/` untuk dokumentasi.

---

## 3. Data Model
Struktur data setiap buku di `books.json`:

```json
{
  "id": 118,
  "judul": "Rich Dad Poor Dad",
  "penulis": "Robert T. Kiyosaki",
  "penerbit": "Warner Books",
  "tahun": 1997,
  "dipinjam": 8,
  "status": "borrowed",
  "tanggal_pinjam": "2025-09-17",
  "tanggal_kembali": "2025-09-24"
}

Field penting:

* `id`: unik per buku.
* `judul`, `penulis`, `penerbit`, `tahun`: metadata utama.
* `dipinjam`: counter total berapa kali buku pernah dipinjam.
* `status`: `available` atau `borrowed`.
* `tanggal_pinjam` & `tanggal_kembali`: rentang peminjaman aktif.

File `deleted_books.json` menyimpan arsip buku yang sudah dihapus beserta timestamp kapan dihapus.

---

## 4. Fitur Utama

1. **CRUD Koleksi Buku**

   * Tambah buku baru (dengan validasi tahun ≥1450 & ≤ tahun berjalan).
   * Update field tertentu (judul, penulis, penerbit, tahun).
   * Hapus buku (dengan proteksi: tidak bisa menghapus buku yang masih dipinjam).
   * Cari buku berdasarkan ID, exact field, atau keyword.

2. **Borrowing & Returning**

   * Pinjam: set status `borrowed`, isi tanggal pinjam & kembali (+7 hari default), increment counter `dipinjam`.
   * Kembalikan: reset status ke `available`, kosongkan tanggal.

3. **Reporting**

   * Ringkasan katalog: total buku aktif, jumlah tersedia, jumlah dipinjam.
   * Daftar detail buku yang sedang dipinjam.
   * Export ringkasan → CSV + chart (komposisi status).

4. **Analytics**

   * Top-N penulis, penerbit, judul berdasarkan total `dipinjam`.
   * Export hasil → CSV + XLSX + chart PNG (berwarna, dengan label angka di tiap batang).

5. **Export Management**

   * Semua export disimpan di folder `outputs/` dengan nama file bertimestamp (misal: `top_authors_20250918_150000.csv`).
   * Memisahkan **data sumber** (tetap rapi di `data/`) dari **artefak turunan**.

---

## 5. Teknologi & Dependency

* **Bahasa**: Python 3.10+
* **Library utama**:

  * `tabulate`: menampilkan tabel rapi di terminal.
  * `matplotlib`: membuat chart (menggunakan backend `Agg` → simpan PNG tanpa GUI).
  * `openpyxl`: export data ke Excel (.xlsx).
* **Struktur project**:

  * `src/` menggunakan layout “src package” (best practice Python modern).
  * `pyproject.toml` digunakan sebagai standar modern packaging (lebih baik daripada `requirements.txt`).

---

## 6. Alur Interaksi

1. User menjalankan program via `library-cli` atau `python -m library_manager.cli`.
2. CLI menampilkan menu utama.
3. User memilih opsi (Read, Create, Update, Delete, Borrowing, Report, Analytics).
4. CLI memanggil fungsi di `services.py` sesuai pilihan.
5. Services membaca/menulis data ke `data/books.json` dan bila perlu membuat file di `outputs/`.
6. CLI menampilkan hasil/konfirmasi di terminal (tabel `tabulate` atau pesan status).

---

## 7. Nilai Tambah Project

* **Praktis & portabel**: hanya butuh Python, data dalam JSON, tidak perlu database.
* **UX ramah**: re-prompt & batal cepat meminimalkan frustasi user.
* **Analitik dasar**: memberi insight sederhana (mis. penulis mana paling populer).
* **Export multi-format**: mendukung CSV, Excel, dan chart PNG → mudah dishare ke stakeholder non-teknis.
* **Struktur rapi**: mengikuti best practice Python (`src/` layout, pyproject.toml, .gitignore, docs, tests).

---

## 8. Use Cases

* **Mini perpustakaan sekolah**: melacak peminjaman tanpa sistem rumit.
* **Komunitas/club**: mengelola koleksi buku bersama.
* **Demo portfolio**: menunjukkan skill Python, data handling, CLI design, reporting, dan basic analytics.
* **Learning project**: latihan CRUD, file I/O, data aggregation, export, visualisasi, packaging Python.

---

## 9. Batasan & Future Work

**Batasan:**

* Tidak ada log transaksi historis (counter `dipinjam` hanya agregat per buku).
* Tidak ada autentikasi user/role.
* Peminjaman hanya fixed 7 hari.

**Future Work:**

* Tambah log transaksi detail.
* Tambah filter analytics (misal per tahun terbit).
* Export PDF laporan.
* Antarmuka GUI atau Web sederhana.

```
