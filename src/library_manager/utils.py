# src/library_manager/utils.py
"""
Utility/UX helpers untuk CLI.

Tujuan file ini:
- Menyediakan helper input yang KONSISTEN untuk semua sub-menu.
- Selalu ada opsi batal cepat: ketik "0" → return None ke caller.
- Menyederhanakan validasi angka/string/tahun agar alur tidak “mental” ke menu awal.

Catatan domain:
- Data utama disimpan di data/books.json (tetap). Helper di sini tidak menyentuh I/O.  # lihat services.py yang mengakses data
"""

from __future__ import annotations
from datetime import datetime
from typing import Iterable

# --- Domain rules untuk validasi tahun buku ---
MIN_YEAR = 1450  # perkiraan awal era buku modern (Gutenberg)

def current_year() -> int:
    """Tahun berjalan (untuk validasi tahun terbit)."""
    return datetime.today().year

def validate_year(year: int) -> tuple[bool, str]:
    """
    Validasi tahun domain.
    Return (ok, message). Jika ok=False → message berisi alasan singkat.
    """
    if year < MIN_YEAR:
        return False, f"Tahun terlalu kecil. Minimal {MIN_YEAR}."
    if year > current_year():
        return False, f"Tahun tidak boleh melebihi {current_year()}."
    return True, "OK"

# -----------------------------
# Prompt helpers (seragam)
# -----------------------------
def ask_yes_no(prompt: str = "Lanjutkan?") -> bool | None:
    """
    Konfirmasi biner + batal cepat:
      - y/yes → True
      - n/no  → False
      - 0     → None (batalkan sub-flow saat ini)
    Selalu re-prompt sampai input valid/batal.
    """
    while True:
        s = input(f"{prompt} (y/n, 0 batal): ").strip().lower()
        if s in {"y", "yes"}:
            return True
        if s in {"n", "no"}:
            return False
        if s == "0":
            return None
        print("Masukkan 'y' atau 'n' (atau 0 untuk batal).")

def ask_choice(options: Iterable[str], prompt: str = "Masukkan pilihan: ") -> str | None:
    """
    Pilihan dari sekumpulan opsi string (mis. {'1','2','3'}).
    - Input '0' → batal (return None).
    - Re-prompt hingga valid/batal.
    """
    valid = {str(o) for o in options}
    while True:
        s = input(f"{prompt} (0 batal): ").strip()
        if s == "0":
            return None
        if s in valid:
            return s
        print(f"Pilihan tidak valid. Pilih salah satu: {sorted(valid)} atau 0 untuk batal.")

def ask_int(prompt: str = "Masukkan angka", allow_zero_cancel: bool = True) -> int | None:
    """
    Minta integer generic.
    - Jika allow_zero_cancel=True: input 0 → batal (return None).
    - Re-prompt sampai valid/batal.
    """
    while True:
        s = input(f"{prompt}{' (0 batal)' if allow_zero_cancel else ''}: ").strip()
        try:
            v = int(s)
        except ValueError:
            print("Input harus berupa angka bulat. Coba lagi.")
            continue
        if allow_zero_cancel and v == 0:
            return None
        return v

def ask_int_range(
    prompt: str, min_val: int, max_val: int, allow_zero_cancel: bool = True
) -> int | None:
    """
    Integer dengan batas bawah/atas (inklusif).
    - 0 → batal (jika allow_zero_cancel=True).
    - Re-prompt sampai berada di rentang.
    """
    while True:
        v = ask_int(prompt, allow_zero_cancel=allow_zero_cancel)
        if v is None:
            return None
        if v < min_val or v > max_val:
            print(f"Masukkan angka antara {min_val}–{max_val}.")
            continue
        return v

def ask_str(prompt: str = "Masukkan teks", allow_empty: bool = False) -> str | None:
    """
    Input string strip() dengan aturan:
    - Ketik tepat '0' → batal (return None).
    - allow_empty=False (default) → tidak boleh kosong.
    """
    while True:
        s = input(f"{prompt} (0 batal): ").strip()
        if s == "0":
            return None
        if not allow_empty and s == "":
            print("Input tidak boleh kosong. Coba lagi.")
            continue
        return s
