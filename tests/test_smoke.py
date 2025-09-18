# tests/test_smoke.py
"""
Smoke tests: memastikan paket bisa di-import, API ada, dan data JSON valid.
Tidak menjalankan CLI interaktif (tidak memanggil input()).
"""

from pathlib import Path
import json
import importlib


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
BOOKS_JSON = DATA_DIR / "books.json"
DELETED_JSON = DATA_DIR / "deleted_books.json"


def test_package_importable_and_has_version():
    pkg = importlib.import_module("library_manager")
    assert hasattr(pkg, "__version__"), "library_manager.__version__ harus ada"


def test_cli_importable_and_has_main():
    cli = importlib.import_module("library_manager.cli")
    assert hasattr(cli, "main") and callable(cli.main), "cli.main harus callable"


def test_services_api_surface_matches_cli_imports():
    """
    Pastikan nama-nama fungsi yang dipakai CLI tersedia di services.
    (Daftarnya diambil dari import di cli.py)
    """
    services = importlib.import_module("library_manager.services")
    required_funcs = {
        # Query
        "get_all_books", "find_book_by_id", "filter_books_by_field", "search_books_keyword",
        # Mutasi
        "add_book", "update_book", "delete_book", "borrow_book", "return_book",
        # Report & Analytics
        "report_summary", "report_export_to_csv",
        "analytics_top_authors", "analytics_top_publishers", "analytics_top_titles",
        "export_top_authors", "export_top_publishers", "export_top_titles",
    }
    missing = [fn for fn in required_funcs if not hasattr(services, fn)]
    assert not missing, f"Fungsi berikut belum ada di services.py: {missing}"


def test_data_files_exist():
    assert BOOKS_JSON.exists(), "data/books.json tidak ditemukan"
    assert DELETED_JSON.exists(), "data/deleted_books.json tidak ditemukan"


def test_books_json_is_valid_and_has_expected_fields():
    data = json.loads(BOOKS_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, list), "books.json harus berupa list of dict"
    assert len(data) > 0, "books.json seharusnya tidak kosong untuk smoke test"

    required_keys = {
        "id", "judul", "penulis", "penerbit", "tahun",
        "dipinjam", "status", "tanggal_pinjam", "tanggal_kembali",
    }
    missing_keys = required_keys - set(data[0].keys())
    assert not missing_keys, f"Field wajib hilang di item pertama: {missing_keys}"


def test_deleted_books_json_is_valid_json_lines():
    """
    File arsip diisi per-baris (JSON Lines). Baris boleh kosong.
    """
    text = DELETED_JSON.read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Baris {i} di deleted_books.json bukan JSON valid: {e}") from e
