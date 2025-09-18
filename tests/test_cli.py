# tests/test_cli.py
"""
E2E smoke test untuk CLI.
Tidak benar-benar menambah/menghapus data,
hanya memastikan menu bisa muncul & keluar dengan input "0".
"""

import builtins
from library_manager import cli

def test_cli_menu_exits_cleanly(monkeypatch):
    # Monkeypatch input() supaya CLI langsung dapat "0"
    monkeypatch.setattr(builtins, "input", lambda *a, **k: "0")
    cli.main()  # harus exit tanpa error
