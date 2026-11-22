"""Unit test class Kategori."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buku import BukuFiksi
from exceptions import KategoriTidakDitemukanError
from kategori import Kategori


class TestKategori(unittest.TestCase):
    def setUp(self):
        self.daftar = []
        self.kategori = Kategori("K01", "Novel", "Buku cerita")

    def test_atribut_awal(self):
        self.assertEqual(self.kategori.get_id_kategori(), "K01")
        self.assertEqual(self.kategori.get_nama_kategori(), "Novel")
        self.assertEqual(self.kategori.get_deskripsi(), "Buku cerita")

    def test_deskripsi_opsional(self):
        self.assertEqual(Kategori("K02", "Komik").get_deskripsi(), "")

    def test_nama_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            Kategori("K03", "   ")

    def test_tambah_kategori(self):
        self.kategori.tambah_kategori(self.daftar)
        self.assertEqual(self.daftar, [self.kategori])

    def test_tambah_kategori_id_kembar_ditolak(self):
        self.kategori.tambah_kategori(self.daftar)
        with self.assertRaises(ValueError):
            Kategori("K01", "Lain").tambah_kategori(self.daftar)

    def test_edit_kategori_penuh(self):
        self.kategori.edit_kategori("Sastra", "Karya sastra")
        self.assertEqual(self.kategori.get_nama_kategori(), "Sastra")
        self.assertEqual(self.kategori.get_deskripsi(), "Karya sastra")

    def test_edit_kategori_sebagian(self):
        self.kategori.edit_kategori(deskripsi_baru="Baru")
        self.assertEqual(self.kategori.get_nama_kategori(), "Novel")
        self.assertEqual(self.kategori.get_deskripsi(), "Baru")

    def test_edit_nama_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            self.kategori.edit_kategori(nama_baru="")

    def test_hapus_kategori(self):
        self.kategori.tambah_kategori(self.daftar)
        self.kategori.hapus_kategori(self.daftar)
        self.assertEqual(self.daftar, [])

    def test_hapus_kategori_tidak_ditemukan(self):
        with self.assertRaises(KategoriTidakDitemukanError):
            self.kategori.hapus_kategori(self.daftar)

    def test_hapus_kategori_yang_dipakai_buku_ditolak(self):
        self.kategori.tambah_kategori(self.daftar)
        buku = BukuFiksi("B1", "Judul", "Penulis", 1000, 1, self.kategori, "Drama")
        with self.assertRaises(ValueError):
            self.kategori.hapus_kategori(self.daftar, [buku])
        self.assertIn(self.kategori, self.daftar)

    def test_tampilkan_kategori(self):
        teks = self.kategori.tampilkan_kategori()
        self.assertIn("K01", teks)
        self.assertIn("Novel", teks)


if __name__ == "__main__":
    unittest.main()
