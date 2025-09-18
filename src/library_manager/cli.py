# src/library_manager/cli.py
"""
CLI utama untuk Library Manager.

Tanggung jawab file ini:
- Menampilkan menu & sub-menu.
- Memanggil layanan di services.py.
- Konsisten dengan UX: re-prompt lokal & batal cepat (0).
"""

from tabulate import tabulate
from .utils import ask_choice, ask_int, ask_str
from .services import (
    # Query
    get_all_books, find_book_by_id, filter_books_by_field, search_books_keyword,
    # Mutasi
    add_book, update_book, delete_book, borrow_book, return_book,
    # Report & Analytics
    report_summary, report_export_to_csv,
    analytics_top_authors, analytics_top_publishers, analytics_top_titles,
    export_top_authors, export_top_publishers, export_top_titles,
)

def submenu_read() -> None:
    while True:
        print("\nSUB-MENU: Koleksi Buku (Read)")
        print("1. Tampilkan Semua Buku")
        print("2. Cari Buku by ID (exact)")
        print("3. Filter Exact (judul/penulis/penerbit/tahun/status)")
        print("4. Cari Keyword (judul/penulis/penerbit)")
        print("0. Kembali")
        c = ask_choice({"1", "2", "3", "4"})
        if c is None:
            return
        if c == "1":
            rows = get_all_books()
            print(tabulate(rows, headers="keys", tablefmt="grid") if rows else "Belum ada data buku.")
        elif c == "2":
            while True:
                bid = ask_int("Masukkan ID buku")
                if bid is None:  # batal cepat
                    break
                b = find_book_by_id(bid)
                if b:
                    print(tabulate([b], headers="keys", tablefmt="grid")); break
                print("ID tidak ditemukan. Coba lagi atau 0 untuk batal.")
        elif c == "3":
            while True:
                field = ask_str("Kolom (judul/penulis/penerbit/tahun/status)")
                if field is None: break
                field = field.lower()
                if field not in {"judul", "penulis", "penerbit", "tahun", "status"}:
                    print("Kolom tidak valid."); continue
                val = ask_str(f"Nilai exact untuk '{field}'")
                if val is None: break
                rows = filter_books_by_field(field, val)
                print(tabulate(rows, headers="keys", tablefmt="grid") if rows else "Tidak ada hasil.")
                break
        elif c == "4":
            while True:
                kw = ask_str("Keyword (contains)")
                if kw is None: break
                rows = search_books_keyword(kw)
                if rows:
                    print(tabulate(rows, headers="keys", tablefmt="grid")); break
                print("Tidak ada hasil. Coba keyword lain atau 0 untuk batal.")

def submenu_create() -> None:
    while True:
        print("\nSUB-MENU: Create (Tambah Buku)")
        print("1. Tambah Buku")
        print("0. Kembali")
        c = ask_choice({"1"})
        if c is None: return
        add_book()

def submenu_update() -> None:
    while True:
        print("\nSUB-MENU: Update Data")
        print("1. Update Buku")
        print("0. Kembali")
        c = ask_choice({"1"})
        if c is None: return
        update_book()

def submenu_delete() -> None:
    while True:
        print("\nSUB-MENU: Delete Data")
        print("1. Hapus Buku")
        print("0. Kembali")
        c = ask_choice({"1"})
        if c is None: return
        delete_book()

def submenu_borrowing() -> None:
    while True:
        print("\nSUB-MENU: Peminjaman")
        print("1. Pinjam Buku")
        print("2. Kembalikan Buku")
        print("0. Kembali")
        c = ask_choice({"1", "2"})
        if c is None: return
        borrow_book() if c == "1" else return_book()

def submenu_report() -> None:
    while True:
        print("\nSUB-MENU: Report (katalog saat ini)")
        print("1. Tampilkan Ringkasan")
        print("2. Export Ringkasan → CSV + Chart")
        print("3. Export Analytics Top-N → CSV/XLSX + Chart")
        print("0. Kembali")
        c = ask_choice({"1", "2", "3"})
        if c is None: return
        if c == "1":
            report_summary()
        elif c == "2":
            report_export_to_csv()
        else:
            kind = ask_choice({"1", "2", "3"}, "Pilih: 1.Penulis 2.Penerbit 3.Judul")
            if kind is None:  # batal internal
                continue
            while True:
                n = ask_int("Masukkan N (contoh 5)")
                if n is None: break
                if n <= 0:
                    print("N harus > 0."); continue
                if kind == "1": export_top_authors(n)
                elif kind == "2": export_top_publishers(n)
                else: export_top_titles(n)
                break

def submenu_analytics() -> None:
    while True:
        print("\nSUB-MENU: Analytics (katalog)")
        print("1. Top-N Penulis (sum 'dipinjam')")
        print("2. Top-N Penerbit (sum 'dipinjam')")
        print("3. Top-N Judul (sum 'dipinjam')")
        print("0. Kembali")
        c = ask_choice({"1", "2", "3"})
        if c is None: return
        while True:
            n = ask_int("Masukkan N (contoh 5)")
            if n is None: break
            if n <= 0: print("N harus > 0."); continue
            if c == "1": analytics_top_authors(n)
            elif c == "2": analytics_top_publishers(n)
            else: analytics_top_titles(n)
            break

def main() -> None:
    while True:
        print("\nSISTEM MANAJEMEN PERPUSTAKAAN")
        print("=" * 40)
        print("1. Read Data")
        print("2. Create Data")
        print("3. Update Data")
        print("4. Delete Data")
        print("5. Peminjaman/Pengembalian")
        print("6. Report")
        print("7. Analytics")
        print("0. Exit")
        print("=" * 40)
        c = ask_choice({"1","2","3","4","5","6","7"})
        if c is None:
            print("Sampai jumpa!"); break
        if c == "1": submenu_read()
        elif c == "2": submenu_create()
        elif c == "3": submenu_update()
        elif c == "4": submenu_delete()
        elif c == "5": submenu_borrowing()
        elif c == "6": submenu_report()
        elif c == "7": submenu_analytics()

if __name__ == "__main__":
    main()
