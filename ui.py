"""Antarmuka grafis (Tkinter) Litera House - Bookstore POS.

Jalankan: python ui.py

UI hanya menjembatani pengguna dengan class yang sudah ada (Buku, Kategori,
Pelanggan, Transaksi, Penjualan). Semua aturan bisnis (validasi stok, pembayaran,
dan seterusnya) tetap berada di class-class tersebut.
"""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, simpledialog, ttk

from buku import Buku, BukuFiksi, BukuNonFiksi
from exceptions import (BukuTidakDitemukanError, KategoriTidakDitemukanError,
                        LiteraHouseError, PembayaranKurangError)
from kategori import Kategori
from pelanggan import Pelanggan
from penjualan import Penjualan
from transaksi import Transaksi

WARNA_JUDUL = "#1f3a5f"
WARNA_HABIS = "#b00020"


# ---------------------------------------------------------------- fungsi bantu
def rupiah(angka):
    return f"Rp{angka:,.0f}"


def jenis_buku(buku):
    return "Fiksi" if isinstance(buku, BukuFiksi) else "Non-Fiksi"


def detail_jenis(buku):
    """Genre untuk buku fiksi, bidang untuk buku non-fiksi."""
    return buku.get_genre() if isinstance(buku, BukuFiksi) else buku.get_bidang()


def parse_angka(teks, nama):
    """Mengubah teks seperti '85000', '85.000', atau 'Rp 85,000' menjadi int."""
    bersih = (teks.strip().lower().replace("rp", "")
              .replace(".", "").replace(",", "").replace(" ", ""))
    if not bersih.isdigit():
        raise ValueError(f"{nama} harus berupa angka bulat (contoh: 85000).")
    return int(bersih)


def wajib(teks, nama):
    teks = teks.strip()
    if not teks:
        raise ValueError(f"{nama} tidak boleh kosong.")
    return teks


def buat_tabel(parent, kolom, tinggi=10):
    """kolom: list of (judul, lebar, rata). Mengembalikan (bingkai, treeview)."""
    bingkai = ttk.Frame(parent)
    tabel = ttk.Treeview(bingkai, columns=[k[0] for k in kolom], show="headings",
                         height=tinggi, selectmode="browse")
    for judul, lebar, rata in kolom:
        tabel.heading(judul, text=judul)
        tabel.column(judul, width=lebar, anchor=rata, stretch=True)
    gulir = ttk.Scrollbar(bingkai, orient="vertical", command=tabel.yview)
    tabel.configure(yscrollcommand=gulir.set)
    tabel.pack(side="left", fill="both", expand=True)
    gulir.pack(side="right", fill="y")
    tabel.tag_configure("habis", foreground=WARNA_HABIS)
    return bingkai, tabel


def kosongkan(tabel):
    tabel.delete(*tabel.get_children())


def isi_form(grid_parent, baris_label, mulai_baris=0):
    """Membuat pasangan label + entry. Mengembalikan list StringVar dan Entry."""
    variabel, entri = [], []
    for i, teks in enumerate(baris_label):
        ttk.Label(grid_parent, text=teks).grid(row=mulai_baris + i, column=0, sticky="w",
                                               padx=(0, 8), pady=3)
        v = tk.StringVar()
        e = ttk.Entry(grid_parent, textvariable=v, width=40)
        e.grid(row=mulai_baris + i, column=1, sticky="w", pady=3)
        variabel.append(v)
        entri.append(e)
    return variabel, entri


# ------------------------------------------------------------------ tab dasar
class TabDasar(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app

    def refresh(self):
        """Dipanggil saat tab dibuka atau data berubah."""


# ------------------------------------------------------------------- Kategori
class TabKategori(TabDasar):
    def __init__(self, master, app):
        super().__init__(master, app)
        form = ttk.LabelFrame(self, text="Data Kategori", padding=10)
        form.pack(fill="x")
        (self.v_id, self.v_nama, self.v_desk), (self.e_id, _, _) = isi_form(
            form, ["ID Kategori", "Nama Kategori", "Deskripsi"])

        tombol = ttk.Frame(form)
        tombol.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(tombol, text="Tambah", command=self.tambah).pack(side="left", padx=(0, 6))
        ttk.Button(tombol, text="Ubah", command=self.ubah).pack(side="left", padx=(0, 6))
        ttk.Button(tombol, text="Hapus", command=self.hapus).pack(side="left", padx=(0, 6))
        ttk.Button(tombol, text="Bersihkan", command=self.bersihkan).pack(side="left")

        bingkai, self.tabel = buat_tabel(
            self, [("ID", 90, "w"), ("Nama", 220, "w"), ("Deskripsi", 450, "w")], tinggi=14)
        bingkai.pack(fill="both", expand=True, pady=(10, 0))
        self.tabel.bind("<<TreeviewSelect>>", self.pilih)

    def refresh(self):
        kosongkan(self.tabel)
        for k in self.app.daftar_kategori:
            self.tabel.insert("", "end", iid=k.get_id_kategori(),
                              values=(k.get_id_kategori(), k.get_nama_kategori(), k.get_deskripsi()))

    def terpilih(self):
        pilihan = self.tabel.selection()
        if not pilihan:
            raise ValueError("Pilih dulu kategori dari tabel.")
        return self.app.cari_kategori(pilihan[0])

    def pilih(self, _event=None):
        pilihan = self.tabel.selection()
        if not pilihan:
            return
        k = self.app.cari_kategori(pilihan[0])
        self.v_id.set(k.get_id_kategori())
        self.v_nama.set(k.get_nama_kategori())
        self.v_desk.set(k.get_deskripsi())
        self.e_id.state(["disabled"])  # ID tidak boleh diubah

    def bersihkan(self):
        for v in (self.v_id, self.v_nama, self.v_desk):
            v.set("")
        self.e_id.state(["!disabled"])
        self.tabel.selection_remove(*self.tabel.selection())

    def tambah(self):
        def aksi():
            Kategori(wajib(self.v_id.get(), "ID kategori"), self.v_nama.get(),
                     self.v_desk.get()).tambah_kategori(self.app.daftar_kategori)
        if self.app.coba(aksi):
            self.bersihkan()
            self.app.refresh_semua()
            self.app.status("Kategori ditambahkan.")

    def ubah(self):
        def aksi():
            self.terpilih().edit_kategori(self.v_nama.get(), self.v_desk.get())
        if self.app.coba(aksi):
            self.app.refresh_semua()
            self.app.status("Kategori diperbarui.")

    def hapus(self):
        try:
            k = self.terpilih()
        except ValueError as e:
            messagebox.showinfo("Pilih data", str(e))
            return
        if not messagebox.askyesno("Hapus kategori", f"Hapus kategori '{k.get_nama_kategori()}'?"):
            return
        if self.app.coba(lambda: k.hapus_kategori(self.app.daftar_kategori, self.app.daftar_buku)):
            self.bersihkan()
            self.app.refresh_semua()
            self.app.status("Kategori dihapus.")


# ----------------------------------------------------------------------- Buku
class TabBuku(TabDasar):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.peta_kategori = {}

        form = ttk.LabelFrame(self, text="Data Buku", padding=10)
        form.pack(fill="x")
        (self.v_kode, self.v_judul, self.v_penulis, self.v_harga, self.v_stok), \
            (self.e_kode, _, _, _, _) = isi_form(
                form, ["Kode Buku", "Judul", "Penulis", "Harga (Rp)", "Stok"])

        ttk.Label(form, text="Kategori").grid(row=5, column=0, sticky="w", padx=(0, 8), pady=3)
        self.v_kategori = tk.StringVar()
        self.cb_kategori = ttk.Combobox(form, textvariable=self.v_kategori, state="readonly", width=37)
        self.cb_kategori.grid(row=5, column=1, sticky="w", pady=3)

        ttk.Label(form, text="Jenis").grid(row=6, column=0, sticky="w", padx=(0, 8), pady=3)
        self.v_jenis = tk.StringVar(value="Fiksi")
        self.cb_jenis = ttk.Combobox(form, textvariable=self.v_jenis, state="readonly",
                                     values=["Fiksi", "Non-Fiksi"], width=37)
        self.cb_jenis.grid(row=6, column=1, sticky="w", pady=3)
        self.cb_jenis.bind("<<ComboboxSelected>>", lambda _e: self.perbarui_label_jenis())

        self.lbl_extra = ttk.Label(form, text="Genre")
        self.lbl_extra.grid(row=7, column=0, sticky="w", padx=(0, 8), pady=3)
        self.v_extra = tk.StringVar()
        self.e_extra = ttk.Entry(form, textvariable=self.v_extra, width=40)
        self.e_extra.grid(row=7, column=1, sticky="w", pady=3)

        tombol = ttk.Frame(form)
        tombol.grid(row=8, column=0, columnspan=2, sticky="w", pady=(8, 0))
        for teks, perintah in (("Tambah", self.tambah), ("Ubah", self.ubah), ("Hapus", self.hapus),
                               ("+ Stok", self.tambah_stok), ("Bersihkan", self.bersihkan)):
            ttk.Button(tombol, text=teks, command=perintah).pack(side="left", padx=(0, 6))

        cari = ttk.Frame(self)
        cari.pack(fill="x", pady=(10, 4))
        ttk.Label(cari, text="Cari (judul / kode):").pack(side="left")
        self.v_cari = tk.StringVar()
        ttk.Entry(cari, textvariable=self.v_cari, width=30).pack(side="left", padx=6)
        self.v_cari.trace_add("write", lambda *_: self.refresh_tabel())
        ttk.Label(cari, text="(baris merah = stok habis)", foreground=WARNA_HABIS).pack(side="left", padx=10)

        bingkai, self.tabel = buat_tabel(self, [
            ("Kode", 70, "w"), ("Judul", 220, "w"), ("Penulis", 150, "w"), ("Jenis", 80, "w"),
            ("Kategori", 130, "w"), ("Harga", 90, "e"), ("Stok", 60, "e")], tinggi=10)
        bingkai.pack(fill="both", expand=True)
        self.tabel.bind("<<TreeviewSelect>>", self.pilih)

    def perbarui_label_jenis(self):
        self.lbl_extra.config(text="Genre" if self.v_jenis.get() == "Fiksi" else "Bidang")

    def refresh(self):
        self.peta_kategori = {
            f"{k.get_id_kategori()} - {k.get_nama_kategori()}": k for k in self.app.daftar_kategori}
        self.cb_kategori.config(values=list(self.peta_kategori))
        if self.v_kategori.get() not in self.peta_kategori:
            self.v_kategori.set("")
        self.refresh_tabel()

    def refresh_tabel(self):
        kosongkan(self.tabel)
        kata = self.v_cari.get().strip()
        data = Buku.cari_buku(self.app.daftar_buku, kata) if kata else self.app.daftar_buku
        for b in data:
            self.tabel.insert("", "end", iid=b.get_kode_buku(),
                              tags=("habis",) if b.get_stok() == 0 else (),
                              values=(b.get_kode_buku(), b.get_judul(), b.get_penulis(), jenis_buku(b),
                                      b.get_kategori().get_nama_kategori(),
                                      rupiah(b.get_harga()), b.get_stok()))

    def buku_terpilih(self):
        pilihan = self.tabel.selection()
        if not pilihan:
            raise ValueError("Pilih dulu buku dari tabel.")
        return self.app.cari_buku_kode(pilihan[0])

    def kategori_terpilih(self):
        label = self.v_kategori.get()
        if label not in self.peta_kategori:
            raise ValueError("Pilih kategori buku. Tambahkan dulu di tab Kategori bila belum ada.")
        return self.peta_kategori[label]

    def pilih(self, _event=None):
        pilihan = self.tabel.selection()
        if not pilihan:
            return
        b = self.app.cari_buku_kode(pilihan[0])
        self.v_kode.set(b.get_kode_buku())
        self.v_judul.set(b.get_judul())
        self.v_penulis.set(b.get_penulis())
        self.v_harga.set(f"{b.get_harga():.0f}")
        self.v_stok.set(str(b.get_stok()))
        k = b.get_kategori()
        self.v_kategori.set(f"{k.get_id_kategori()} - {k.get_nama_kategori()}")
        self.v_jenis.set(jenis_buku(b))
        self.perbarui_label_jenis()
        self.v_extra.set(detail_jenis(b))
        # Kode, jenis, dan genre/bidang tidak dapat diubah setelah buku dibuat
        self.e_kode.state(["disabled"])
        self.cb_jenis.state(["disabled"])
        self.e_extra.state(["disabled"])

    def bersihkan(self):
        for v in (self.v_kode, self.v_judul, self.v_penulis, self.v_harga, self.v_stok,
                  self.v_kategori, self.v_extra):
            v.set("")
        self.v_jenis.set("Fiksi")
        self.perbarui_label_jenis()
        self.e_kode.state(["!disabled"])
        self.cb_jenis.state(["!disabled"])
        self.e_extra.state(["!disabled"])
        self.tabel.selection_remove(*self.tabel.selection())

    def tambah(self):
        def aksi():
            kode = wajib(self.v_kode.get(), "Kode buku")
            harga = parse_angka(self.v_harga.get(), "Harga")
            stok = parse_angka(self.v_stok.get(), "Stok")
            kategori = self.kategori_terpilih()
            extra = wajib(self.v_extra.get(), self.lbl_extra.cget("text"))
            kelas = BukuFiksi if self.v_jenis.get() == "Fiksi" else BukuNonFiksi
            kelas(kode, self.v_judul.get(), self.v_penulis.get(), harga, stok,
                  kategori, extra).tambah_buku(self.app.daftar_buku)
        if self.app.coba(aksi):
            self.bersihkan()
            self.app.refresh_semua()
            self.app.status("Buku ditambahkan.")

    def ubah(self):
        def aksi():
            buku = self.buku_terpilih()
            harga = parse_angka(self.v_harga.get(), "Harga")
            stok = parse_angka(self.v_stok.get(), "Stok")
            kategori = self.kategori_terpilih()
            # Validasi dulu lewat objek sementara agar tidak terjadi perubahan setengah jalan
            BukuFiksi(buku.get_kode_buku(), self.v_judul.get(), self.v_penulis.get(),
                      harga, stok, kategori, "-")
            buku.edit_buku(judul=self.v_judul.get(), penulis=self.v_penulis.get(),
                           harga=harga, stok=stok, kategori=kategori)
        if self.app.coba(aksi):
            self.app.refresh_semua()
            self.app.status("Buku diperbarui.")

    def hapus(self):
        try:
            buku = self.buku_terpilih()
        except ValueError as e:
            messagebox.showinfo("Pilih data", str(e))
            return
        if not messagebox.askyesno("Hapus buku", f"Hapus buku '{buku.get_judul()}'?"):
            return
        if self.app.coba(lambda: buku.hapus_buku(self.app.daftar_buku)):
            self.bersihkan()
            self.app.refresh_semua()
            self.app.status("Buku dihapus.")

    def tambah_stok(self):
        try:
            buku = self.buku_terpilih()
        except ValueError as e:
            messagebox.showinfo("Pilih data", str(e))
            return
        jumlah = simpledialog.askinteger("Tambah stok", f"Jumlah stok '{buku.get_judul()}' yang ditambah:",
                                         parent=self, minvalue=1)
        if jumlah is None:
            return
        if self.app.coba(lambda: buku.tambah_stok(jumlah)):
            self.app.refresh_semua()
            self.pilih()
            self.app.status(f"Stok '{buku.get_judul()}' bertambah {jumlah}.")


# ------------------------------------------------------------------ Pelanggan
class TabPelanggan(TabDasar):
    def __init__(self, master, app):
        super().__init__(master, app)
        form = ttk.LabelFrame(self, text="Data Pelanggan", padding=10)
        form.pack(fill="x")
        (self.v_id, self.v_nama, self.v_hp, self.v_alamat), (self.e_id, _, _, _) = isi_form(
            form, ["ID Pelanggan", "Nama", "Nomor HP", "Alamat"])

        tombol = ttk.Frame(form)
        tombol.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        for teks, perintah in (("Tambah", self.tambah), ("Ubah", self.ubah), ("Hapus", self.hapus),
                               ("Riwayat Pembelian", self.lihat_riwayat), ("Bersihkan", self.bersihkan)):
            ttk.Button(tombol, text=teks, command=perintah).pack(side="left", padx=(0, 6))

        bingkai, self.tabel = buat_tabel(self, [
            ("ID", 90, "w"), ("Nama", 200, "w"), ("Nomor HP", 140, "w"),
            ("Alamat", 300, "w"), ("Transaksi", 80, "e")], tinggi=14)
        bingkai.pack(fill="both", expand=True, pady=(10, 0))
        self.tabel.bind("<<TreeviewSelect>>", self.pilih)

    def refresh(self):
        kosongkan(self.tabel)
        for p in self.app.daftar_pelanggan:
            self.tabel.insert("", "end", iid=p.get_id_pelanggan(), values=(
                p.get_id_pelanggan(), p.get_nama(), p.get_nomor_hp(), p.get_alamat(),
                len(p.lihat_riwayat_pembelian())))

    def terpilih(self):
        pilihan = self.tabel.selection()
        if not pilihan:
            raise ValueError("Pilih dulu pelanggan dari tabel.")
        return Pelanggan.cari_pelanggan(self.app.daftar_pelanggan, pilihan[0])

    def pilih(self, _event=None):
        pilihan = self.tabel.selection()
        if not pilihan:
            return
        p = Pelanggan.cari_pelanggan(self.app.daftar_pelanggan, pilihan[0])
        self.v_id.set(p.get_id_pelanggan())
        self.v_nama.set(p.get_nama())
        self.v_hp.set(p.get_nomor_hp())
        self.v_alamat.set(p.get_alamat())
        self.e_id.state(["disabled"])

    def bersihkan(self):
        for v in (self.v_id, self.v_nama, self.v_hp, self.v_alamat):
            v.set("")
        self.e_id.state(["!disabled"])
        self.tabel.selection_remove(*self.tabel.selection())

    def tambah(self):
        def aksi():
            Pelanggan(wajib(self.v_id.get(), "ID pelanggan"), self.v_nama.get(), self.v_hp.get(),
                      self.v_alamat.get()).tambah_pelanggan(self.app.daftar_pelanggan)
        if self.app.coba(aksi):
            self.bersihkan()
            self.app.refresh_semua()
            self.app.status("Pelanggan ditambahkan.")

    def ubah(self):
        def aksi():
            p = self.terpilih()
            # Validasi dulu lewat objek sementara agar tidak terjadi perubahan setengah jalan
            Pelanggan(p.get_id_pelanggan(), self.v_nama.get(), self.v_hp.get(), self.v_alamat.get())
            p.edit_nama_pelanggan(self.v_nama.get())
            p.edit_nomor_hp(self.v_hp.get())
            p.edit_alamat(self.v_alamat.get())
        if self.app.coba(aksi):
            self.app.refresh_semua()
            self.app.status("Data pelanggan diperbarui.")

    def hapus(self):
        try:
            p = self.terpilih()
        except ValueError as e:
            messagebox.showinfo("Pilih data", str(e))
            return
        if not messagebox.askyesno("Hapus pelanggan", f"Hapus pelanggan '{p.get_nama()}'?"):
            return
        if self.app.coba(lambda: p.hapus_pelanggan(self.app.daftar_pelanggan)):
            self.bersihkan()
            self.app.refresh_semua()
            self.app.status("Pelanggan dihapus.")

    def lihat_riwayat(self):
        try:
            p = self.terpilih()
        except ValueError as e:
            messagebox.showinfo("Pilih data", str(e))
            return
        riwayat = p.lihat_riwayat_pembelian()
        baris = [f"Riwayat pembelian {p.get_nama()}", "=" * 44]
        if not riwayat:
            baris.append("Belum ada riwayat pembelian.")
        for r in riwayat:
            baris.append(f"{r['id_transaksi']} | {r['waktu']} | {rupiah(r['total'])}")
            for item in r["item"]:
                baris.append(f"    - {item['judul']} x{item['jumlah']}")
        self.app.tampilkan_teks(f"Riwayat - {p.get_nama()}", "\n".join(baris))


# ---------------------------------------------------------------------- Kasir
class TabKasir(TabDasar):
    def __init__(self, master, app):
        super().__init__(master, app)
        self.trx = None
        self.peta_pelanggan = {}
        self.id_pelanggan = None  # ID pelanggan yang sedang dipilih (None = umum)

        kiri = ttk.Frame(self)
        kiri.pack(side="left", fill="both", expand=True, padx=(0, 8))
        kanan = ttk.Frame(self)
        kanan.pack(side="left", fill="both", expand=True)

        # --- kiri: pelanggan dan pilih buku
        bp = ttk.LabelFrame(kiri, text="Pelanggan", padding=8)
        bp.pack(fill="x")
        self.v_pelanggan = tk.StringVar(value="Umum")
        self.cb_pelanggan = ttk.Combobox(bp, textvariable=self.v_pelanggan, state="readonly")
        self.cb_pelanggan.pack(fill="x")
        self.cb_pelanggan.bind("<<ComboboxSelected>>", self.pilih_pelanggan)

        bb = ttk.LabelFrame(kiri, text="Pilih Buku", padding=8)
        bb.pack(fill="both", expand=True, pady=(8, 0))
        cari = ttk.Frame(bb)
        cari.pack(fill="x", pady=(0, 6))
        ttk.Label(cari, text="Cari:").pack(side="left")
        self.v_cari = tk.StringVar()
        ttk.Entry(cari, textvariable=self.v_cari).pack(side="left", fill="x", expand=True, padx=6)
        self.v_cari.trace_add("write", lambda *_: self.refresh_buku())

        bingkai, self.tabel_buku = buat_tabel(bb, [
            ("Kode", 60, "w"), ("Judul", 190, "w"), ("Harga", 85, "e"), ("Stok", 50, "e")], tinggi=12)
        bingkai.pack(fill="both", expand=True)
        self.tabel_buku.bind("<Double-1>", lambda _e: self.tambah_ke_keranjang())

        baris = ttk.Frame(bb)
        baris.pack(fill="x", pady=(8, 0))
        ttk.Label(baris, text="Jumlah:").pack(side="left")
        self.v_jumlah = tk.StringVar(value="1")
        ttk.Spinbox(baris, from_=1, to=999, textvariable=self.v_jumlah, width=6).pack(side="left", padx=6)
        ttk.Button(baris, text="Tambah ke Keranjang  >>", command=self.tambah_ke_keranjang
                   ).pack(side="right")

        # --- kanan: keranjang dan pembayaran
        bk = ttk.LabelFrame(kanan, text="Keranjang", padding=8)
        bk.pack(fill="both", expand=True)
        self.lbl_trx = ttk.Label(bk, text="", foreground=WARNA_JUDUL)
        self.lbl_trx.pack(anchor="w", pady=(0, 4))
        bingkai, self.tabel_keranjang = buat_tabel(bk, [
            ("Judul", 180, "w"), ("Jumlah", 60, "e"), ("Harga", 85, "e"), ("Subtotal", 95, "e")], tinggi=9)
        bingkai.pack(fill="both", expand=True)
        aksi = ttk.Frame(bk)
        aksi.pack(fill="x", pady=(6, 0))
        ttk.Button(aksi, text="Ubah Jumlah", command=self.ubah_jumlah).pack(side="left", padx=(0, 6))
        ttk.Button(aksi, text="Hapus Item", command=self.hapus_item).pack(side="left")

        bbay = ttk.LabelFrame(kanan, text="Pembayaran", padding=8)
        bbay.pack(fill="x", pady=(8, 0))
        self.lbl_total = ttk.Label(bbay, text="Total: Rp0", font=("TkDefaultFont", 16, "bold"),
                                   foreground=WARNA_JUDUL)
        self.lbl_total.pack(anchor="w")
        baris = ttk.Frame(bbay)
        baris.pack(fill="x", pady=(8, 0))
        ttk.Label(baris, text="Uang bayar (Rp):").pack(side="left")
        self.v_uang = tk.StringVar()
        ttk.Entry(baris, textvariable=self.v_uang, width=18).pack(side="left", padx=6)
        self.v_uang.trace_add("write", lambda *_: self.perbarui_kembalian())
        self.lbl_kembalian = ttk.Label(bbay, text="")
        self.lbl_kembalian.pack(anchor="w", pady=(4, 0))
        tombol = ttk.Frame(bbay)
        tombol.pack(fill="x", pady=(8, 0))
        ttk.Button(tombol, text="BAYAR", command=self.bayar).pack(side="left", padx=(0, 6))
        ttk.Button(tombol, text="Batalkan Transaksi", command=self.batalkan).pack(side="left")

        self.mulai_transaksi()

    # ---- siklus transaksi
    def mulai_transaksi(self):
        self.trx = Transaksi.buat_transaksi(self.app.id_transaksi_berikut())
        self.id_pelanggan = None
        self.v_pelanggan.set("Umum")
        self.v_uang.set("")
        self.v_jumlah.set("1")
        self.refresh_keranjang()

    def refresh(self):
        self.peta_pelanggan = {"Umum": None}
        for p in self.app.daftar_pelanggan:
            self.peta_pelanggan[f"{p.get_id_pelanggan()} - {p.get_nama()}"] = p
        self.cb_pelanggan.config(values=list(self.peta_pelanggan))
        # pertahankan pilihan pelanggan bila masih ada (nama bisa saja berubah)
        label = "Umum"
        for teks, p in self.peta_pelanggan.items():
            if p is not None and p.get_id_pelanggan() == self.id_pelanggan:
                label = teks
        self.v_pelanggan.set(label)
        if label == "Umum":
            self.id_pelanggan = None
            self.trx.pilih_pelanggan(None)
        self.refresh_buku()
        self.refresh_keranjang()

    def refresh_buku(self):
        kosongkan(self.tabel_buku)
        kata = self.v_cari.get().strip()
        data = Buku.cari_buku(self.app.daftar_buku, kata) if kata else self.app.daftar_buku
        for b in data:
            self.tabel_buku.insert("", "end", iid=b.get_kode_buku(),
                                   tags=("habis",) if b.get_stok() == 0 else (),
                                   values=(b.get_kode_buku(), b.get_judul(),
                                           rupiah(b.get_harga()), b.get_stok()))

    def refresh_keranjang(self):
        kosongkan(self.tabel_keranjang)
        for d in self.trx.get_daftar_detail():
            self.tabel_keranjang.insert("", "end", iid=d.get_buku().get_kode_buku(), values=(
                d.get_buku().get_judul(), d.get_jumlah(),
                rupiah(d.get_harga_satuan()), rupiah(d.get_subtotal())))
        self.lbl_trx.config(text=f"Transaksi {self.trx.get_id_transaksi()}  |  Status: {self.trx.get_status()}")
        self.lbl_total.config(text=f"Total: {rupiah(self.trx.hitung_total())}")
        self.perbarui_kembalian()

    def perbarui_kembalian(self):
        teks = self.v_uang.get().strip()
        if not teks:
            self.lbl_kembalian.config(text="", foreground="")
            return
        try:
            uang = parse_angka(teks, "Uang bayar")
            self.lbl_kembalian.config(
                text=f"Kembalian: {rupiah(self.trx.hitung_kembalian(uang))}", foreground="#1b5e20")
        except PembayaranKurangError as e:
            self.lbl_kembalian.config(text=f"Kurang: {rupiah(e.total - e.dibayar)}",
                                      foreground=WARNA_HABIS)
        except ValueError:
            self.lbl_kembalian.config(text="Uang bayar harus berupa angka.", foreground=WARNA_HABIS)

    # ---- aksi
    def pilih_pelanggan(self, _event=None):
        pelanggan = self.peta_pelanggan.get(self.v_pelanggan.get())
        self.trx.pilih_pelanggan(pelanggan)
        self.id_pelanggan = pelanggan.get_id_pelanggan() if pelanggan else None

    def tambah_ke_keranjang(self):
        pilihan = self.tabel_buku.selection()
        if not pilihan:
            messagebox.showinfo("Pilih buku", "Pilih dulu buku dari daftar di kiri.")
            return

        def aksi():
            buku = self.app.cari_buku_kode(pilihan[0])
            self.trx.tambah_detail_transaksi(buku, parse_angka(self.v_jumlah.get(), "Jumlah"))
        if self.app.coba(aksi):
            self.v_jumlah.set("1")
            self.refresh_keranjang()

    def item_terpilih(self):
        pilihan = self.tabel_keranjang.selection()
        if not pilihan:
            messagebox.showinfo("Pilih item", "Pilih dulu item di keranjang.")
            return None
        return self.app.cari_buku_kode(pilihan[0])

    def ubah_jumlah(self):
        buku = self.item_terpilih()
        if buku is None:
            return
        jumlah = simpledialog.askinteger("Ubah jumlah", f"Jumlah baru '{buku.get_judul()}':",
                                         parent=self, minvalue=1)
        if jumlah is not None and self.app.coba(lambda: self.trx.ubah_jumlah_detail(buku, jumlah)):
            self.refresh_keranjang()

    def hapus_item(self):
        buku = self.item_terpilih()
        if buku is not None and self.app.coba(lambda: self.trx.hapus_detail_transaksi(buku)):
            self.refresh_keranjang()

    def bayar(self):
        trx = self.trx

        def aksi():
            trx.proses_pembayaran(parse_angka(self.v_uang.get(), "Uang bayar"))
            trx.simpan_transaksi(self.app.penjualan)
        if self.app.coba(aksi):
            self.app.tampilkan_struk(trx)
            self.app.status(f"Transaksi {trx.get_id_transaksi()} selesai. "
                            f"Kembalian {rupiah(trx.get_kembalian())}.")
            self.mulai_transaksi()
            self.app.refresh_semua()

    def batalkan(self):
        if not self.trx.get_daftar_detail():
            self.mulai_transaksi()
            return
        if not messagebox.askyesno("Batalkan transaksi", "Batalkan transaksi ini?"):
            return
        if self.app.coba(self.trx.batalkan_transaksi):
            self.app.status(f"Transaksi {self.trx.get_id_transaksi()} dibatalkan.")
            self.mulai_transaksi()


# -------------------------------------------------------------------- Laporan
class TabLaporan(TabDasar):
    def __init__(self, master, app):
        super().__init__(master, app)
        kartu = ttk.Frame(self)
        kartu.pack(fill="x")
        self.label_kartu = {}
        for kunci, judul in (("transaksi", "Jumlah Transaksi"), ("pendapatan", "Total Pendapatan"),
                             ("pelanggan", "Pelanggan Unik"), ("terlaris", "Buku Terlaris")):
            kotak = ttk.LabelFrame(kartu, text=judul, padding=10)
            kotak.pack(side="left", fill="x", expand=True, padx=(0, 8))
            lbl = ttk.Label(kotak, text="-", font=("TkDefaultFont", 13, "bold"), foreground=WARNA_JUDUL)
            lbl.pack(anchor="w")
            self.label_kartu[kunci] = lbl

        isi = ttk.Frame(self)
        isi.pack(fill="both", expand=True, pady=(10, 0))
        kiri = ttk.LabelFrame(isi, text="Laporan Penjualan", padding=8)
        kiri.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.teks = tk.Text(kiri, width=42, height=16, font=("Courier New", 10), state="disabled")
        self.teks.pack(fill="both", expand=True)

        kanan = ttk.LabelFrame(isi, text="Riwayat Penjualan (klik dua kali untuk melihat struk)", padding=8)
        kanan.pack(side="left", fill="both", expand=True)
        self.daftar = tk.Listbox(kanan, font=("Courier New", 10), activestyle="none")
        self.daftar.pack(fill="both", expand=True)
        self.daftar.bind("<Double-1>", self.buka_struk)
        ttk.Button(self, text="Segarkan", command=self.refresh).pack(anchor="e", pady=(8, 0))

    def refresh(self):
        pj = self.app.penjualan
        laporan = pj.buat_laporan_penjualan()
        self.label_kartu["transaksi"].config(text=str(laporan["jumlah_transaksi"]))
        self.label_kartu["pendapatan"].config(text=rupiah(laporan["total_pendapatan"]))
        self.label_kartu["pelanggan"].config(text=str(laporan["jumlah_pelanggan_unik"]))
        terlaris = pj.buku_terlaris()  # tuple (judul, jumlah) atau None
        self.label_kartu["terlaris"].config(text=f"{terlaris[0]} ({terlaris[1]})" if terlaris else "-")
        self.teks.config(state="normal")
        self.teks.delete("1.0", "end")
        self.teks.insert("1.0", pj.cetak_laporan())
        self.teks.config(state="disabled")
        self.daftar.delete(0, "end")
        for baris in pj.tampilkan_riwayat_penjualan():
            self.daftar.insert("end", baris)

    def buka_struk(self, _event=None):
        pilihan = self.daftar.curselection()
        if pilihan:
            self.app.tampilkan_struk(self.app.penjualan.get_daftar_penjualan()[pilihan[0]])


# ------------------------------------------------------------------ Aplikasi
class AplikasiLiteraHouse(tk.Tk):
    def __init__(self, isi_contoh=True):
        super().__init__()
        self.title("Litera House - Bookstore POS")
        self.geometry("1120x700")
        self.minsize(1000, 640)

        self.daftar_kategori = []
        self.daftar_buku = []
        self.daftar_pelanggan = []
        self.penjualan = Penjualan()
        self.no_transaksi = 0

        tkfont.nametofont("TkDefaultFont").configure(size=10)
        gaya = ttk.Style(self)
        if "clam" in gaya.theme_names():
            gaya.theme_use("clam")
        gaya.configure("Treeview", rowheight=24)
        gaya.configure("TNotebook.Tab", padding=(16, 6))

        if isi_contoh:
            self.isi_data_contoh()

        judul = ttk.Label(self, text="LITERA HOUSE  -  Bookstore POS", font=("TkDefaultFont", 15, "bold"),
                          foreground="white", background=WARNA_JUDUL, padding=(14, 10))
        judul.pack(fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)
        self.tab = {
            "Kasir": TabKasir(self.notebook, self),
            "Buku": TabBuku(self.notebook, self),
            "Kategori": TabKategori(self.notebook, self),
            "Pelanggan": TabPelanggan(self.notebook, self),
            "Laporan": TabLaporan(self.notebook, self),
        }
        for nama, frame in self.tab.items():
            self.notebook.add(frame, text=nama)
        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self.tab_aktif().refresh())

        self.var_status = tk.StringVar(value="Siap.")
        ttk.Label(self, textvariable=self.var_status, relief="sunken", anchor="w",
                  padding=(8, 3)).pack(fill="x", side="bottom")
        self.refresh_semua()

    # ---- bantu
    def tab_aktif(self):
        return self.nametowidget(self.notebook.select())

    def refresh_semua(self):
        for frame in self.tab.values():
            frame.refresh()

    def status(self, teks):
        self.var_status.set(teks)

    def coba(self, fungsi):
        """Menjalankan fungsi; error dari class ditampilkan sebagai pesan, bukan crash."""
        try:
            fungsi()
            return True
        except (LiteraHouseError, ValueError) as e:
            messagebox.showerror("Tidak dapat diproses", str(e))
            return False

    def id_transaksi_berikut(self):
        self.no_transaksi += 1
        return f"T{self.no_transaksi:03d}"

    def cari_kategori(self, id_kategori):
        for k in self.daftar_kategori:
            if k.get_id_kategori() == id_kategori:
                return k
        raise KategoriTidakDitemukanError(id_kategori)

    def cari_buku_kode(self, kode):
        for b in self.daftar_buku:
            if b.get_kode_buku() == kode:
                return b
        raise BukuTidakDitemukanError(kode)

    def tampilkan_teks(self, judul, isi):
        jendela = tk.Toplevel(self)
        jendela.title(judul)
        jendela.transient(self)
        jendela.geometry(f"+{self.winfo_rootx() + 120}+{self.winfo_rooty() + 90}")
        teks = tk.Text(jendela, width=52, height=min(30, isi.count("\n") + 2),
                       font=("Courier New", 10), padx=10, pady=10)
        teks.insert("1.0", isi)
        teks.config(state="disabled")
        teks.pack(fill="both", expand=True)
        ttk.Button(jendela, text="Tutup", command=jendela.destroy).pack(pady=8)
        return jendela

    def tampilkan_struk(self, transaksi):
        return self.tampilkan_teks(f"Struk {transaksi.get_id_transaksi()}", transaksi.cetak_struk())

    def isi_data_contoh(self):
        """Data awal supaya aplikasi langsung bisa dicoba (hilang saat aplikasi ditutup)."""
        novel = Kategori("K01", "Novel", "Buku cerita panjang")
        diri = Kategori("K02", "Pengembangan Diri", "Buku pengembangan pribadi")
        sains = Kategori("K03", "Sains", "Buku ilmu pengetahuan")
        for k in (novel, diri, sains):
            k.tambah_kategori(self.daftar_kategori)
        for b in (
            BukuFiksi("B001", "Laskar Pelangi", "Andrea Hirata", 85000, 12, novel, "Drama"),
            BukuFiksi("B002", "Bumi", "Tere Liye", 90000, 8, novel, "Fantasi"),
            BukuNonFiksi("B003", "Atomic Habits", "James Clear", 110000, 5, diri, "Psikologi"),
            BukuNonFiksi("B004", "Sapiens", "Yuval Noah Harari", 135000, 4, sains, "Sejarah"),
            BukuFiksi("B005", "Dilan 1990", "Pidi Baiq", 70000, 0, novel, "Roman"),
        ):
            b.tambah_buku(self.daftar_buku)
        Pelanggan("P001", "Budi Santoso", "081234567890", "Pekalongan").tambah_pelanggan(self.daftar_pelanggan)
        Pelanggan("P002", "Siti Aminah", "081298765432", "Semarang").tambah_pelanggan(self.daftar_pelanggan)


def main():
    try:  # tampilan tajam di layar Windows beresolusi tinggi
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError, ImportError):
        pass
    AplikasiLiteraHouse().mainloop()


if __name__ == "__main__":
    main()
