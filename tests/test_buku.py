"""Unit test class Buku, BukuFiksi, dan BukuNonFiksi."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buku import Buku, BukuFiksi, BukuNonFiksi
from exceptions import BukuTidakDitemukanError, StokTidakCukupError
from kategori import Kategori


class TestBuku(unittest.TestCase):
    def setUp(self):
        self.kategori = Kategori("K01", "Novel", "Buku cerita")
        self.buku = BukuFiksi("B001", "Laskar Pelangi", "Andrea Hirata",
                              85000, 10, self.kategori, "Drama")
        self.daftar = []

    # ---- Encapsulation dan validasi ----
    def test_getter(self):
        self.assertEqual(self.buku.get_kode_buku(), "B001")
        self.assertEqual(self.buku.get_judul(), "Laskar Pelangi")
        self.assertEqual(self.buku.get_penulis(), "Andrea Hirata")
        self.assertEqual(self.buku.get_harga(), 85000)
        self.assertEqual(self.buku.get_stok(), 10)
        self.assertIs(self.buku.get_kategori(), self.kategori)

    def test_harga_negatif_ditolak(self):
        with self.assertRaises(ValueError):
            BukuFiksi("B2", "J", "P", -1, 1, self.kategori, "g")

    def test_stok_negatif_ditolak(self):
        with self.assertRaises(ValueError):
            BukuFiksi("B2", "J", "P", 1000, -1, self.kategori, "g")

    def test_judul_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            BukuFiksi("B2", "  ", "P", 1000, 1, self.kategori, "g")

    def test_kategori_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            BukuFiksi("B2", "J", "P", 1000, 1, None, "g")

    # ---- Abstraction, inheritance, polymorphism ----
    def test_buku_abstract_tidak_bisa_dibuat(self):
        with self.assertRaises(TypeError):
            Buku("B9", "J", "P", 1000, 1, self.kategori)

    def test_turunan_adalah_buku(self):
        self.assertIsInstance(self.buku, Buku)
        self.assertIsInstance(BukuNonFiksi("B3", "J", "P", 1, 1, self.kategori, "Sains"), Buku)

    def test_polymorphism_tampilkan_info(self):
        nonfiksi = BukuNonFiksi("B2", "Atomic Habits", "James Clear",
                                110000, 5, self.kategori, "Psikologi")
        info_fiksi = self.buku.tampilkan_info()
        info_nonfiksi = nonfiksi.tampilkan_info()
        self.assertIn("Fiksi", info_fiksi)
        self.assertIn("Drama", info_fiksi)
        self.assertIn("Non-Fiksi", info_nonfiksi)
        self.assertIn("Psikologi", info_nonfiksi)
        self.assertIn("Novel", info_fiksi)

    # ---- Stok ----
    def test_tambah_stok(self):
        self.buku.tambah_stok(5)
        self.assertEqual(self.buku.get_stok(), 15)

    def test_tambah_stok_nol_ditolak(self):
        with self.assertRaises(ValueError):
            self.buku.tambah_stok(0)

    def test_kurangi_stok(self):
        self.buku.kurangi_stok(4)
        self.assertEqual(self.buku.get_stok(), 6)

    def test_kurangi_stok_melebihi_stok(self):
        with self.assertRaises(StokTidakCukupError) as ctx:
            self.buku.kurangi_stok(11)
        self.assertEqual(ctx.exception.diminta, 11)
        self.assertEqual(ctx.exception.tersedia, 10)
        self.assertEqual(self.buku.get_stok(), 10)  # stok tidak berubah

    def test_kurangi_stok_nol_ditolak(self):
        with self.assertRaises(ValueError):
            self.buku.kurangi_stok(0)

    # ---- Data buku ----
    def test_tambah_buku(self):
        self.buku.tambah_buku(self.daftar)
        self.assertEqual(self.daftar, [self.buku])

    def test_tambah_buku_kode_kembar_ditolak(self):
        self.buku.tambah_buku(self.daftar)
        kembar = BukuFiksi("B001", "Lain", "P", 1000, 1, self.kategori, "g")
        with self.assertRaises(ValueError):
            kembar.tambah_buku(self.daftar)

    def test_edit_buku(self):
        self.buku.edit_buku(judul="Judul Baru", harga=90000)
        self.assertEqual(self.buku.get_judul(), "Judul Baru")
        self.assertEqual(self.buku.get_harga(), 90000)
        self.assertEqual(self.buku.get_penulis(), "Andrea Hirata")  # tidak berubah

    def test_edit_buku_stok_negatif_ditolak(self):
        with self.assertRaises(ValueError):
            self.buku.edit_buku(stok=-5)

    def test_hapus_buku(self):
        self.buku.tambah_buku(self.daftar)
        self.buku.hapus_buku(self.daftar)
        self.assertEqual(self.daftar, [])

    def test_hapus_buku_tidak_ditemukan(self):
        with self.assertRaises(BukuTidakDitemukanError):
            self.buku.hapus_buku(self.daftar)

    def test_cari_buku_berdasarkan_judul(self):
        self.buku.tambah_buku(self.daftar)
        hasil = Buku.cari_buku(self.daftar, "LASKAR")  # tidak peka huruf besar/kecil
        self.assertEqual(hasil, [self.buku])

    def test_cari_buku_berdasarkan_kode(self):
        self.buku.tambah_buku(self.daftar)
        self.assertEqual(Buku.cari_buku(self.daftar, "b001"), [self.buku])

    def test_cari_buku_tidak_ada_hasil(self):
        self.buku.tambah_buku(self.daftar)
        self.assertEqual(Buku.cari_buku(self.daftar, "tidak ada"), [])


if __name__ == "__main__":
    unittest.main()
