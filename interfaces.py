"""Interface proyek Litera House.

Python tidak punya kata kunci `interface`. Bentuknya adalah class abstract yang
hanya berisi method abstract: class yang mewarisinya WAJIB mengimplementasikan
semua method tersebut, kalau tidak objeknya tidak bisa dibuat.
"""
from abc import ABC, abstractmethod


class DapatDitampilkan(ABC):
    """Kontrak untuk semua objek yang dapat menampilkan informasinya sebagai teks."""

    @abstractmethod
    def tampilkan_info(self):
        """Mengembalikan teks informasi objek."""
