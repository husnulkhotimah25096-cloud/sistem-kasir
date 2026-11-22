"""Unit test class Pelanggan."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from exceptions import PelangganTidakDitemukanError
from pelanggan import Pelanggan


class TestPelanggan(unittest.TestCase):
    def setUp(self):
        self.daftar = []
        self.pelanggan = Pelanggan("P001", "Budi", "081234567890", "Pekalongan")

    def test_getter(self):
        self.assertEqual(self.pelanggan.get_id_pelanggan(), "P001")
        self.assertEqual(self.pelanggan.get_nama(), "Budi")
        self.assertEqual(self.pelanggan.get_nomor_hp(), "081234567890")
        self.assertEqual(self.pelanggan.get_alamat(), "Pekalongan")

    def test_alamat_opsional(self):
        self.assertEqual(Pelanggan("P2", "Ani", "0812").get_alamat(), "")

    def test_nama_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            Pelanggan("P2", "  ", "0812")

    def test_nomor_hp_bukan_angka_ditolak(self):
        with self.assertRaises(ValueError):
            Pelanggan("P2", "Ani", "08ab12")

    def test_tambah_pelanggan(self):
        self.pelanggan.tambah_pelanggan(self.daftar)
        self.assertEqual(self.daftar, [self.pelanggan])

    def test_tambah_pelanggan_id_kembar_ditolak(self):
        self.pelanggan.tambah_pelanggan(self.daftar)
        with self.assertRaises(ValueError):
            Pelanggan("P001", "Lain", "0812").tambah_pelanggan(self.daftar)

    def test_edit_data_pelanggan(self):
        self.pelanggan.edit_nama_pelanggan("Budi Santoso")
        self.pelanggan.edit_nomor_hp("0899")
        self.pelanggan.edit_alamat("Semarang")
        self.assertEqual(self.pelanggan.get_nama(), "Budi Santoso")
        self.assertEqual(self.pelanggan.get_nomor_hp(), "0899")
        self.assertEqual(self.pelanggan.get_alamat(), "Semarang")

    def test_edit_nomor_hp_tidak_valid_ditolak(self):
        with self.assertRaises(ValueError):
            self.pelanggan.edit_nomor_hp("abc")
        self.assertEqual(self.pelanggan.get_nomor_hp(), "081234567890")  # tidak berubah

    def test_hapus_pelanggan(self):
        self.pelanggan.tambah_pelanggan(self.daftar)
        self.pelanggan.hapus_pelanggan(self.daftar)
        self.assertEqual(self.daftar, [])

    def test_hapus_pelanggan_tidak_ditemukan(self):
        with self.assertRaises(PelangganTidakDitemukanError):
            self.pelanggan.hapus_pelanggan(self.daftar)

    def test_cari_pelanggan(self):
        self.pelanggan.tambah_pelanggan(self.daftar)
        self.assertIs(Pelanggan.cari_pelanggan(self.daftar, "P001"), self.pelanggan)

    def test_cari_pelanggan_tidak_ditemukan(self):
        with self.assertRaises(PelangganTidakDitemukanError):
            Pelanggan.cari_pelanggan(self.daftar, "P999")

    def test_tampilkan_pelanggan(self):
        self.pelanggan.tambah_pelanggan(self.daftar)
        hasil = Pelanggan.tampilkan_pelanggan(self.daftar)
        self.assertEqual(len(hasil), 1)
        self.assertIn("Budi", hasil[0])

    def test_riwayat_pembelian_awal_kosong(self):
        self.assertEqual(self.pelanggan.lihat_riwayat_pembelian(), [])

    def test_tambah_riwayat_pembelian(self):
        self.pelanggan.tambah_riwayat_pembelian({"id_transaksi": "T001"})
        self.pelanggan.tambah_riwayat_pembelian({"id_transaksi": "T002"})
        riwayat = self.pelanggan.lihat_riwayat_pembelian()
        self.assertEqual([r["id_transaksi"] for r in riwayat], ["T001", "T002"])

    def test_riwayat_tidak_bisa_diubah_dari_luar(self):
        self.pelanggan.tambah_riwayat_pembelian({"id_transaksi": "T001"})
        self.pelanggan.lihat_riwayat_pembelian().clear()
        self.assertEqual(len(self.pelanggan.lihat_riwayat_pembelian()), 1)


    def test_isi_riwayat_tidak_bisa_diubah_dari_luar(self):
        self.pelanggan.tambah_riwayat_pembelian({"id_transaksi": "T001", "total": 85000})
        self.pelanggan.lihat_riwayat_pembelian()[0]["total"] = 0
        self.assertEqual(self.pelanggan.lihat_riwayat_pembelian()[0]["total"], 85000)


if __name__ == "__main__":
    unittest.main()
