"""Unit test interface DapatDitampilkan dan implementasinya."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buku import BukuFiksi, BukuNonFiksi
from interfaces import DapatDitampilkan
from kategori import Kategori
from pelanggan import Pelanggan


class TestInterface(unittest.TestCase):
    def setUp(self):
        self.kategori = Kategori("K01", "Novel", "Buku cerita")
        self.fiksi = BukuFiksi("B1", "Laskar Pelangi", "Andrea", 85000, 5, self.kategori, "Drama")
        self.nonfiksi = BukuNonFiksi("B2", "Atomic Habits", "James Clear", 110000, 5,
                                     self.kategori, "Psikologi")
        self.pelanggan = Pelanggan("P1", "Budi", "0812", "Pekalongan")
        self.semua = [self.fiksi, self.nonfiksi, self.kategori, self.pelanggan]

    def test_interface_tidak_bisa_dibuat_langsung(self):
        with self.assertRaises(TypeError):
            DapatDitampilkan()

    def test_class_tanpa_implementasi_tidak_bisa_dibuat(self):
        class Rusak(DapatDitampilkan):
            pass

        with self.assertRaises(TypeError):
            Rusak()

    def test_semua_class_mengimplementasikan_interface(self):
        for objek in self.semua:
            self.assertIsInstance(objek, DapatDitampilkan)

    def test_polymorphism_antar_class_berbeda(self):
        for objek in self.semua:
            info = objek.tampilkan_info()
            self.assertIsInstance(info, str)
            self.assertTrue(info)

    def test_isi_info_sesuai_jenis_objek(self):
        self.assertIn("Laskar Pelangi", self.fiksi.tampilkan_info())
        self.assertIn("Novel", self.kategori.tampilkan_info())
        self.assertIn("Budi", self.pelanggan.tampilkan_info())


if __name__ == "__main__":
    unittest.main()
