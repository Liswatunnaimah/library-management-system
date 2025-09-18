# src/library_manager/services.py
"""
Layanan inti untuk Library Manager (tanpa transaksi/periode).

Menyediakan:
- IO data JSON (load/save).
- Query: list semua, cari by id, filter exact, search keyword.
- Mutasi: tambah/update/hapus, pinjam/kembalikan (status + counter `dipinjam`).
- Report ringkas (katalog saat ini) + export CSV.
- Analytics Top-N (penulis/penerbit/judul) + export CSV/XLSX + chart.

Catatan arsitektur:
- Sumber data: data/books.json (tetap)  → kompatibel dengan data kamu sekarang.  # noqa
- Artefak/report: outputs/ (di-root) → mudah di-gitignore & bersih dari data sumber.

UX konsisten:
- Semua sub-flow re-prompt sampai valid.
- Selalu sediakan batal cepat: input "0" mengembalikan None ke caller.
"""

from __future__ import annotations
import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Sequence

# Matplotlib diset non-GUI (menyimpan ke file)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tabulate import tabulate

from .utils import (  # helper input/validator buatanmu
    ask_choice, ask_int, ask_int_range, ask_str, ask_yes_no,
    validate_year, current_year, MIN_YEAR,
)

# ---------- Lokasi data & output ----------
# File ini berada di: src/library_manager/
# BASE_DIR = root repo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "books.json")       # sumber data (tetap)  :contentReference[oaicite:3]{index=3}
EXPORT_DIR = os.path.join(BASE_DIR, "outputs")          # artefak/report (baru)

DATE_FMT = "%Y-%m-%d"
BORROW_DAYS = 7  # lama pinjam default (hari)

# ---------- Util export/chart ----------
def _nowstamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _export_rows_to_csv(rows: list[dict], path: str) -> None:
    """Simpan list[dict] ke CSV; header diambil dari union key."""
    _ensure_dir(os.path.dirname(path))
    if not rows:
        open(path, "w", encoding="utf-8").close()
        return
    # tentukan urutan header dari urutan kemunculan key
    fieldnames, seen = [], set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k); fieldnames.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def _export_rows_to_xlsx(rows: list[dict], path: str, sheet: str) -> None:
    """Export sederhana ke .xlsx (opsional; butuh openpyxl)."""
    try:
        from openpyxl import Workbook  # import lokal supaya dependency opsional
    except ImportError:
        print("Info: 'openpyxl' belum terpasang → lewati export .xlsx.")
        return
    _ensure_dir(os.path.dirname(path))
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    if rows:
        headers = list({k for r in rows for k in r.keys()})
        ws.append(headers)
        for r in rows:
            ws.append([r.get(h) for h in headers])
    wb.save(path)

def _palette(n: int) -> Sequence:
    """Palet warna (tab20), siklik jika n>20."""
    cmap = plt.get_cmap("tab20")
    return [cmap(i % 20) for i in range(n)]

def _save_bar(labels: list[str], values: list[int], title: str, fname: str,
              xlabel: str = "", ylabel: str = "Jumlah") -> str:
    """
    Simpan bar chart berwarna + label angka.
    Menggunakan palet tab20 agar kontras dan konsisten.
    """
    _ensure_dir(EXPORT_DIR)
    plt.figure(figsize=(10, 6))
    colors = _palette(len(labels))
    bars = plt.bar(labels, values, color=colors, edgecolor="black", linewidth=0.5)
    plt.title(title)
    if xlabel: plt.xlabel(xlabel)
    if ylabel: plt.ylabel(ylabel)
    plt.xticks(rotation=20, ha="right")
    # label angka di atas batang
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width()/2, h, f"{int(h)}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    path = os.path.join(EXPORT_DIR, fname)
    plt.savefig(path, dpi=150)
    plt.close()
    return path

# ---------- IO rendah ----------
def load_books() -> list[dict]:
    """Baca seluruh buku dari JSON; aman jika file belum ada/korup."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Peringatan: data/books.json tidak valid.")
        return []

def save_books(books: list[dict]) -> None:
    """Tulis seluruh buku ke JSON (indent 2, UTF-8)."""
    _ensure_dir(DATA_DIR)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)

# ---------- Query ----------
def get_all_books() -> list[dict]:
    return load_books()

def find_book_by_id(book_id: int) -> dict | None:
    for b in load_books():
        if b.get("id") == book_id:
            return b
    return None

def filter_books_by_field(field: str, value) -> list[dict]:
    """Exact match by field; `tahun` dibandingkan numerik, lainnya case-insensitive."""
    books = load_books()
    if field == "tahun":
        try:
            v = int(value)
        except ValueError:
            return []
        return [b for b in books if int(b.get("tahun", 0)) == v]
    v = str(value).lower()
    return [b for b in books if str(b.get(field, "")).lower() == v]

def search_books_keyword(keyword: str) -> list[dict]:
    """Cari `keyword` (contains) pada judul/penulis/penerbit (case-insensitive)."""
    kw = keyword.strip().lower()
    if not kw:
        return []
    fields = ("judul", "penulis", "penerbit")
    out = []
    for b in load_books():
        if any(kw in str(b.get(f, "")).lower() for f in fields):
            out.append(b)
    return out

# ---------- Mutasi (dengan re-prompt & batal cepat) ----------
def add_book() -> None:
    books = load_books()

    # ID unik
    while True:
        new_id = ask_int("Masukkan ID Buku", allow_zero_cancel=True)
        if new_id is None:
            print("Dibatalkan."); return
        if any(b.get("id") == new_id for b in books):
            print("ID sudah dipakai. Gunakan ID lain."); continue
        break

    judul = ask_str("Judul buku")
    if judul is None: print("Dibatalkan."); return
    penulis = ask_str("Penulis")
    if penulis is None: print("Dibatalkan."); return
    penerbit = ask_str("Penerbit")
    if penerbit is None: print("Dibatalkan."); return

    # validasi tahun domain
    while True:
        tahun = ask_int(f"Tahun terbit (>= {MIN_YEAR}, <= {current_year()})", allow_zero_cancel=True)
        if tahun is None: print("Dibatalkan."); return
        ok, msg = validate_year(tahun)
        if ok: break
        print(msg)

    new_book = {
        "id": new_id,
        "judul": judul,
        "penulis": penulis,
        "penerbit": penerbit,
        "tahun": tahun,
        "dipinjam": 0,
        "status": "available",
        "tanggal_pinjam": None,
        "tanggal_kembali": None,
    }

    print("\nPratinjau:")
    print(tabulate([new_book], headers="keys", tablefmt="grid"))
    yn = ask_yes_no("Simpan buku ini?")
    if yn is None or yn is False:
        print("Batal simpan."); return

    books.append(new_book)
    save_books(books)
    print("Buku berhasil ditambahkan.")

def update_book() -> None:
    books = load_books()

    # cari id (re-prompt)
    book = None
    while True:
        bid = ask_int("ID buku yang diupdate", allow_zero_cancel=True)
        if bid is None: print("Dibatalkan."); return
        book = find_book_by_id(bid)
        if book: break
        print("ID tidak ditemukan. Coba lagi atau 0 untuk batal.")

    print("\nData sekarang:")
    print(tabulate([book], headers="keys", tablefmt="grid"))

    # pilih field
    field_map = {"1": "judul", "2": "penulis", "3": "penerbit", "4": "tahun"}
    while True:
        print("\nField: 1.Judul  2.Penulis  3.Penerbit  4.Tahun  0.Batal")
        ch = ask_choice({"1", "2", "3", "4"})
        if ch is None: print("Dibatalkan."); return
        field = field_map.get(ch)
        if field: break

    # nilai baru
    if field == "tahun":
        while True:
            new_val = ask_int(f"Tahun baru (>= {MIN_YEAR}, <= {current_year()})", allow_zero_cancel=True)
            if new_val is None: print("Dibatalkan."); return
            ok, msg = validate_year(new_val)
            if ok: break
            print(msg)
    else:
        new_val = ask_str(f"Nilai baru untuk {field}")
        if new_val is None: print("Dibatalkan."); return

    preview = book.copy(); preview[field] = new_val
    print("\nPratinjau perubahan:")
    print(tabulate([preview], headers="keys", tablefmt="grid"))
    yn = ask_yes_no("Lanjut update?")
    if yn is None or yn is False:
        print("Batal update."); return

    for b in books:
        if b.get("id") == book["id"]:
            b[field] = new_val; break
    save_books(books)
    print("Buku berhasil diperbarui.")

def delete_book() -> None:
    books = load_books()

    # cari id (re-prompt)
    book = None
    while True:
        bid = ask_int("ID buku yang dihapus", allow_zero_cancel=True)
        if bid is None: print("Dibatalkan."); return
        book = find_book_by_id(bid)
        if book: break
        print("ID tidak ditemukan. Coba lagi atau 0 untuk batal.")

    if book.get("status") == "borrowed":
        print("Buku sedang dipinjam. Kembalikan dulu sebelum dihapus."); return

    print("\nAkan dihapus:")
    print(tabulate([book], headers="keys", tablefmt="grid"))
    yn = ask_yes_no("Yakin hapus buku ini?")
    if yn is None or yn is False:
        print("Batal hapus."); return

    books = [b for b in books if b.get("id") != book["id"]]
    save_books(books)
    print(f"ID {book['id']} terhapus.")

def borrow_book() -> None:
    books = load_books()

    # pilih id yang available
    book = None
    while True:
        bid = ask_int("ID buku yang dipinjam", allow_zero_cancel=True)
        if bid is None: print("Dibatalkan."); return
        book = find_book_by_id(bid)
        if not book:
            print("ID tidak ditemukan. Coba lagi atau 0 untuk batal."); continue
        if book.get("status") != "available":
            print("Buku tidak tersedia (status bukan 'available')."); continue
        break

    print("\nAkan dipinjam:")
    print(tabulate([book], headers="keys", tablefmt="grid"))
    yn = ask_yes_no("Konfirmasi pinjam?")
    if yn is None or yn is False:
        print("Batal pinjam."); return

    today = datetime.today().date()
    book["status"] = "borrowed"
    book["tanggal_pinjam"] = today.strftime(DATE_FMT)
    book["tanggal_kembali"] = (today + timedelta(days=BORROW_DAYS)).strftime(DATE_FMT)
    book["dipinjam"] = int(book.get("dipinjam", 0)) + 1

    bs = load_books()
    for b in bs:
        if b.get("id") == book["id"]:
            b.update(book); break
    save_books(bs)
    print(f"Berhasil dipinjam. Deadline {book['tanggal_kembali']}.")

def return_book() -> None:
    books = load_books()

    book = None
    while True:
        bid = ask_int("ID buku yang dikembalikan", allow_zero_cancel=True)
        if bid is None: print("Dibatalkan."); return
        book = find_book_by_id(bid)
        if not book:
            print("ID tidak ditemukan. Coba lagi atau 0 untuk batal."); continue
        if book.get("status") != "borrowed":
            print("Buku ini tidak berstatus 'borrowed'."); continue
        break

    print("\nAkan dikembalikan:")
    print(tabulate([book], headers="keys", tablefmt="grid"))
    yn = ask_yes_no("Konfirmasi pengembalian?")
    if yn is None or yn is False:
        print("Batal pengembalian."); return

    book["status"] = "available"
    book["tanggal_pinjam"] = None
    book["tanggal_kembali"] = None

    bs = load_books()
    for b in bs:
        if b.get("id") == book["id"]:
            b.update(book); break
    save_books(bs)
    print("Pengembalian selesai.")

# ---------- Report (katalog saat ini) ----------
def report_summary() -> None:
    """Cetak ringkasan katalog saat ini ke terminal."""
    books = load_books()
    total = len(books)
    borrowed_now = [b for b in books if b.get("status") == "borrowed"]
    borrowed = len(borrowed_now)
    available = total - borrowed

    print("\n=== Ringkasan Katalog ===")
    print(f"Total buku aktif : {total}")
    print(f"Tersedia         : {available}")
    print(f"Sedang dipinjam  : {borrowed}")

    if borrowed_now:
        print("\nBuku yang sedang dipinjam:")
        print(tabulate(borrowed_now, headers="keys", tablefmt="grid"))

def report_export_to_csv() -> None:
    """
    Export ringkasan + daftar sedang dipinjam ke CSV
    dan chart komposisi status (berwarna + label angka).
    """
    books = load_books()
    t = _nowstamp()
    borrowed_now = [b for b in books if b.get("status") == "borrowed"]
    summary = [{
        "total_buku_aktif": len(books),
        "buku_tersedia": len(books) - len(borrowed_now),
        "buku_dipinjam": len(borrowed_now),
    }]

    _export_rows_to_csv(summary, os.path.join(EXPORT_DIR, f"report_summary_{t}.csv"))
    _export_rows_to_csv(borrowed_now, os.path.join(EXPORT_DIR, f"report_borrowed_{t}.csv"))
    _save_bar(["Available", "Borrowed"], [len(books)-len(borrowed_now), len(borrowed_now)],
              "Komposisi Status Katalog", f"chart_status_{t}.png", xlabel="Status")
    print("Report ringkasan telah diekspor ke folder 'outputs/'.")

# ---------- Analytics Top-N ----------
def _top_by(field: str, top_n: int) -> list[dict]:
    """
    Agregasi katalog saat ini:
    - field: 'penulis' | 'penerbit' | 'judul'
    - metrik: total_dipinjam (sum dari field `dipinjam` di katalog).
    """
    if field == "judul":
        rows = [{"judul": b.get("judul"), "total_dipinjam": int(b.get("dipinjam", 0))}
                for b in load_books()]
        rows.sort(key=lambda r: (-r["total_dipinjam"], r["judul"].lower()))
        return rows[:max(1, top_n)]

    agg = defaultdict(int)
    extra = defaultdict(int)  # jumlah judul per author/publisher
    for b in load_books():
        k = (b.get(field) or "").strip() or "(Tidak diketahui)"
        agg[k] += int(b.get("dipinjam", 0))
        if field in {"penulis", "penerbit"}:
            extra[k] += 1
    rows = []
    for k, v in agg.items():
        r = {field: k, "total_dipinjam": v}
        if field in {"penulis", "penerbit"}:
            r["jumlah_judul"] = extra[k]
        rows.append(r)
    rows.sort(key=lambda r: (-r["total_dipinjam"], -(r.get("jumlah_judul") or 0), str(r)))
    return rows[:max(1, top_n)]

def analytics_top_authors(n: int) -> None:
    rows = _top_by("penulis", n)
    if not rows: print("Belum ada data."); return
    print(f"\nTop {n} Penulis (total 'dipinjam' katalog):")
    print(tabulate(rows, headers="keys", tablefmt="grid"))
    _save_bar([r["penulis"] for r in rows], [r["total_dipinjam"] for r in rows],
              "Top Penulis (Katalog)", f"chart_top_authors_{_nowstamp()}.png", xlabel="Penulis")

def analytics_top_publishers(n: int) -> None:
    rows = _top_by("penerbit", n)
    if not rows: print("Belum ada data."); return
    print(f"\nTop {n} Penerbit (total 'dipinjam' katalog):")
    print(tabulate(rows, headers="keys", tablefmt="grid"))
    _save_bar([r["penerbit"] for r in rows], [r["total_dipinjam"] for r in rows],
              "Top Penerbit (Katalog)", f"chart_top_publishers_{_nowstamp()}.png", xlabel="Penerbit")

def analytics_top_titles(n: int) -> None:
    rows = _top_by("judul", n)
    if not rows: print("Belum ada data."); return
    print(f"\nTop {n} Judul (total 'dipinjam' katalog):")
    print(tabulate(rows, headers="keys", tablefmt="grid"))
    _save_bar([r["judul"] for r in rows], [r["total_dipinjam"] for r in rows],
              "Top Judul (Katalog)", f"chart_top_titles_{_nowstamp()}.png", xlabel="Judul")

# ---------- Analytics Exporters (CSV+XLSX+Chart) ----------
def export_top_authors(n: int) -> None:
    rows = _top_by("penulis", n); t = _nowstamp()
    _export_rows_to_csv(rows, os.path.join(EXPORT_DIR, f"top_authors_{t}.csv"))
    _export_rows_to_xlsx(rows, os.path.join(EXPORT_DIR, f"top_authors_{t}.xlsx"), "TopAuthors")
    _save_bar([r["penulis"] for r in rows], [r["total_dipinjam"] for r in rows],
              f"Top {n} Penulis (Katalog)", f"chart_top_authors_{t}.png", xlabel="Penulis")
    print("Export Top Penulis → CSV/XLSX + chart di 'outputs/'.")

def export_top_publishers(n: int) -> None:
    rows = _top_by("penerbit", n); t = _nowstamp()
    _export_rows_to_csv(rows, os.path.join(EXPORT_DIR, f"top_publishers_{t}.csv"))
    _export_rows_to_xlsx(rows, os.path.join(EXPORT_DIR, f"top_publishers_{t}.xlsx"), "TopPublishers")
    _save_bar([r["penerbit"] for r in rows], [r["total_dipinjam"] for r in rows],
              f"Top {n} Penerbit (Katalog)", f"chart_top_publishers_{t}.png", xlabel="Penerbit")
    print("Export Top Penerbit → CSV/XLSX + chart di 'outputs/'.")

def export_top_titles(n: int) -> None:
    rows = _top_by("judul", n); t = _nowstamp()
    _export_rows_to_csv(rows, os.path.join(EXPORT_DIR, f"top_titles_{t}.csv"))
    _export_rows_to_xlsx(rows, os.path.join(EXPORT_DIR, f"top_titles_{t}.xlsx"), "TopTitles")
    _save_bar([r["judul"] for r in rows], [r["total_dipinjam"] for r in rows],
              f"Top {n} Judul (Katalog)", f"chart_top_titles_{t}.png", xlabel="Judul")
    print("Export Top Judul → CSV/XLSX + chart di 'outputs/'.")
