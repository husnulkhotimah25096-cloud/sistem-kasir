# Litera House – Bookstore POS

Sistem kasir toko buku berbasis Python (Pemrograman Berorientasi Objek).

## Menjalankan
```
python ui.py              # aplikasi kasir (antarmuka Tkinter)
python main.py            # demo alur kasir di terminal
python demo_memori.py     # demonstrasi memory management
python -m unittest discover -s tests -v   # unit test
```

## Struktur
| File | Isi |
|---|---|
| `ui.py` | Antarmuka grafis Tkinter (tab Kasir, Buku, Kategori, Pelanggan, Laporan) |
| `interfaces.py` | Interface `DapatDitampilkan` |
| `kategori.py` | `Kategori` |
| `buku.py` | `Buku` (abstract), `BukuFiksi`, `BukuNonFiksi` |
| `pelanggan.py` | `Pelanggan` |
| `detail_transaksi.py` | `DetailTransaksi` |
| `transaksi.py` | `Transaksi` |
| `penjualan.py` | `Penjualan` |
| `exceptions.py` | Custom exception |
| `tests/` | Unit test (`unittest`), satu file per class |

## Penerapan tujuh materi PBO
| Materi | Penerapan |
|---|---|
| 1. Class, object, memory management | 8 class utama dan banyak objek; `demo_memori.py` (referensi, reference count, `del`, garbage collector, shallow/deep copy) |
| 2. Encapsulation | Atribut privat `__`, getter/setter dengan validasi, method protected `_info_dasar()` |
| 3. Inheritance | `BukuFiksi` dan `BukuNonFiksi` mewarisi `Buku`; semua exception mewarisi `LiteraHouseError` |
| 4. Polymorphism | `tampilkan_info()` berbeda di tiap class, dipanggil lewat satu loop di `main.py` |
| 5. Abstraction dan interface | `Buku` abstract (`ABC`, `@abstractmethod`); interface `DapatDitampilkan` diimplementasikan `Buku`, `Kategori`, `Pelanggan` |
| 6. Collection dan iterasi | `list` (daftar, keranjang), `dict` (laporan), `tuple` (`STATUS_VALID`, `buku_terlaris`), `set` (`pelanggan_unik`), `for`, `enumerate`, `sorted`, comprehension |
| 7. Exception handling | 6 custom exception, `raise` di semua class, `try/except/else/finally` dan beberapa `except` di `main.py` |

## Fitur aplikasi (`ui.py`)
- **Kasir:** pilih pelanggan (atau Umum), pilih buku, atur jumlah, ubah/hapus item keranjang, lihat total dan kembalian langsung, bayar, cetak struk, atau batalkan transaksi.
- **Buku:** tambah, ubah, hapus, cari, dan tambah stok. Buku berstok 0 ditandai merah.
- **Kategori** dan **Pelanggan:** tambah, ubah, hapus; pelanggan juga memiliki riwayat pembelian.
- **Laporan:** jumlah transaksi, total pendapatan, pelanggan unik, buku terlaris, dan riwayat penjualan (klik dua kali untuk melihat struk).

Catatan: data hanya disimpan di memori. Saat aplikasi ditutup, data kembali ke data contoh.
