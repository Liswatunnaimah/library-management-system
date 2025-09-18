# tests/test_export.py
"""
Test fungsi export agar tidak menimpa folder asli outputs/.
Menggunakan tmp_path pytest untuk menyimpan hasil sementara.
"""

import importlib
from pathlib import Path

def test_report_export_to_csv(tmp_path, monkeypatch):
    # Import services
    services = importlib.import_module("library_manager.services")

    # ==== Opsi A (direkomendasikan): services.py punya konstanta OUTPUT_DIR ====
    # Jika di services.py ada sesuatu seperti:
    #   OUTPUT_DIR = Path("outputs")
    # maka kita cukup monkeypatch ke folder sementara:
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(services, "OUTPUT_DIR"):
        monkeypatch.setattr(services, "OUTPUT_DIR", outputs_dir)

    # Jalankan export → seharusnya membuat minimal satu file CSV di outputs_dir
    services.report_export_to_csv()

    # Cek hasil
    files = list(Path(outputs_dir).glob("*.csv")) if outputs_dir.exists() else []
    assert files, "Export CSV gagal, tidak ada file di lokasi output."
