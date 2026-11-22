"""Unit test class Penjualan."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from buku import BukuFiksi
from kategori import Kategori
from pelanggan import Pelanggan
from penjualan import Penjualan
from transaksi import Transaksi


class TestPenjualan(unittest.TestCase):
    def setUp(self):
        kategori = Kategori("K01", "Umum")
        self.laskar = BukuFiksi("B001", "Laskar Pelangi", "Andrea", 85000, 20, kategori, "Drama")
        self.dilan = BukuFiksi("B002", "Dilan", "Pidi Baiq", 70000, 20, kategori, "Roman")
        self.penjualan = Penjualan()

    def _transaksi_selesai(self, id_transaksi, buku, jumlah, pelanggan=None):
        trx = Transaksi.buat_transaksi(id_transaksi, pelanggan)
        trx.tambah_detail_transaksi(buku, jumlah)
        trx.proses_pembayaran(10000000)
        return trx

    def test_penjualan_awal_kosong(self):
        self.assertEqual(self.penjualan.hitung_jumlah_transaksi(), 0)
        self.assertEqual(self.penjualan.hitung_total_pendapatan(), 0)
        self.assertEqual(self.penjualan.tampilkan_riwayat_penjualan(), [])

    def test_simpan_transaksi(self):
        trx = self._transaksi_selesai("T001", self.laskar, 2)
        self.penjualan.simpan_transaksi(trx)
        self.assertEqual(self.penjualan.hitung_jumlah_transaksi(), 1)
        self.assertEqual(self.penjualan.get_daftar_penjualan(), [trx])

    def test_simpan_transaksi_belum_dibayar_ditolak(self):
        trx = Transaksi.buat_transaksi("T001")
        trx.tambah_detail_transaksi(self.laskar, 1)
        with self.assertRaises(ValueError):
            self.penjualan.simpan_transaksi(trx)

    def test_simpan_transaksi_dibatalkan_ditolak(self):
        trx = Transaksi.buat_transaksi("T001")
        trx.tambah_detail_transaksi(self.laskar, 1)
        trx.batalkan_transaksi()
        with self.assertRaises(ValueError):
            self.penjualan.simpan_transaksi(trx)

    def test_simpan_transaksi_kembar_ditolak(self):
        trx = self._transaksi_selesai("T001", self.laskar, 1)
        self.penjualan.simpan_transaksi(trx)
        with self.assertRaises(ValueError):
            self.penjualan.simpan_transaksi(trx)
        self.assertEqual(self.penjualan.hitung_jumlah_transaksi(), 1)

    def test_hitung_total_pendapatan(self):
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T001", self.laskar, 2))  # 170.000
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T002", self.dilan, 1))   # 70.000
        self.assertEqual(self.penjualan.hitung_total_pendapatan(), 240000)
        self.assertEqual(self.penjualan.get_total_pendapatan(), 240000)

    def test_hitung_jumlah_transaksi(self):
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T001", self.laskar, 1))
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T002", self.dilan, 1))
        self.assertEqual(self.penjualan.hitung_jumlah_transaksi(), 2)

    def test_tampilkan_riwayat_penjualan(self):
        pelanggan = Pelanggan("P001", "Budi", "0812")
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T001", self.laskar, 1, pelanggan))
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T002", self.dilan, 1))
        riwayat = self.penjualan.tampilkan_riwayat_penjualan()
        self.assertEqual(len(riwayat), 2)
        self.assertIn("Budi", riwayat[0])
        self.assertIn("Umum", riwayat[1])  # tanpa pelanggan tercatat "Umum"

    def test_buat_laporan_penjualan(self):
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T001", self.laskar, 2))
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T002", self.laskar, 1))
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T003", self.dilan, 3))
        laporan = self.penjualan.buat_laporan_penjualan()
        self.assertEqual(laporan["jumlah_transaksi"], 3)
        self.assertEqual(laporan["total_pendapatan"], 3 * 85000 + 3 * 70000)
        self.assertEqual(laporan["buku_terjual"], {"Laskar Pelangi": 3, "Dilan": 3})

    def test_cetak_laporan(self):
        self.penjualan.simpan_transaksi(self._transaksi_selesai("T001", self.laskar, 2))
        teks = self.penjualan.cetak_laporan()
        self.assertIn("LAPORAN PENJUALAN", teks)
        self.assertIn("170,000", teks)
        self.assertIn("Laskar Pelangi", teks)


if __name__ == "__main__":
    unittest.main()
