# src/library_manager/__init__.py
"""
Library Manager (package marker).

Ekspos modul publik dan versi paket.
Dipakai oleh pyproject entry-point (`library-cli`) untuk menjalankan CLI.
"""
__all__ = ["cli", "services", "utils"]
__version__ = "0.1.0"
