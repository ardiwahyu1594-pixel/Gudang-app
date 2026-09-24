from datetime import datetime, date
import os
import pandas as pd
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Aplikasi Manajemen Gudang", page_icon="📦", layout="wide"
)

# File Database Lokal (CSV)
DB_BARANG = "data_barang.csv"
DB_TRANSAKSI = "data_transaksi.csv"


# Inisialisasi Data jika belum ada
def init_db():
  if not os.path.exists(DB_BARANG):
    df_barang = pd.DataFrame(
        columns=[
            "Kode Barang",
            "Nama Barang",
            "Kategori",
            "Warna Label",
            "Tgl Kedatangan",
            "Tgl Produksi",
            "Tgl Expire",
            "Nama Rak",
            "Nomor Rak",
            "Tingkat Rak",
            "Stok Sistem",
            "Harga Satuan",
        ]
    )
    df_barang.to_csv(DB_BARANG, index=False)

  if not os.path.exists(DB_TRANSAKSI):
    df_transaksi = pd.DataFrame(
        columns=[
            "Tanggal",
            "Kode Barang",
            "Nama Barang",
            "Tipe",
            "Jumlah",
            "Keterangan",
        ]
    )
    df_transaksi.to_csv(DB_TRANSAKSI, index=False)


init_db()

# Load Data
df_barang = pd.read_csv(DB_BARANG)

# Perbaikan otomatis jika kolom versi lama belum ada
if "Tgl Kedatangan" not in df_barang.columns:
  df_barang["Tgl Kedatangan"] = "-"
if "Tgl Produksi" not in df_barang.columns:
  df_barang["Tgl Produksi"] = "-"
if "Tgl Expire" not in df_barang.columns:
  df_barang["Tgl Expire"] = "-"
if "Warna Label" not in df_barang.columns:
  df_barang["Warna Label"] = "Putih (Normal)"
if "Nama Rak" not in df_barang.columns:
  df_barang["Nama Rak"] = "-"
if "Nomor Rak" not in df_barang.columns:
  df_barang["Nomor Rak"] = "-"
if "Tingkat Rak" not in df_barang.columns:
  df_barang["Tingkat Rak"] = "Level 1 (Bawah)"
if "Kategori" not in df_barang.columns:
  df_barang["Kategori"] = "-"
if "Harga Satuan" not in df_barang.columns:
  df_barang["Harga Satuan"] = 0.0
df_barang.to_csv(DB_BARANG, index=False)

df_transaksi = pd.read_csv(DB_TRANSAKSI)


# Fungsi untuk memberikan warna latar belakang baris tabel berdasarkan pilihan manual
def warnai_manual(row):
  warna = str(row.get("Warna Label", ""))
  if "Biru" in warna:
    return ["background-color: #d1ecf1"] * len(row)  # Biru Muda
  elif "Hijau" in warna:
    return ["background-color: #d4edda"] * len(row)  # Hijau Muda
  elif "Kuning" in warna:
    return ["background-color: #fff3cd"] * len(row)  # Kuning Muda
  elif "Merah" in warna or "Pink" in warna:
    return ["background-color: #f8d7da"] * len(row)  # Merah / Pink Muda
  elif "Ungu" in warna:
    return ["background-color: #e2d9f3"] * len(row)  # Ungu Muda
  else:
    return [""] * len(row)


# Navigasi Sidebar
st.sidebar.title("📌 Menu Gudang")
menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "📊 Dashboard Stok",
        "📍 Pemetaan Rak",
        "📜 Riwayat Transaksi",
        "✏️ Edit Data Barang",
        "🗑️ Hapus Barang",
        "📥 Barang Masuk",
        "📤 Barang Keluar",
        "📋 Stok Opname",
        "➕ Tambah Barang Baru",
    ],
)

# ==========================================
# 1. DASHBOARD STOK
# ==========================================
if menu == "📊 Dashboard Stok":
  st.title("📊 Dashboard Stok & Masa Simpan Gudang")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang. Silakan tambah barang baru melalui menu.")
  else:
    total_jenis = len(df_barang)
    total_item = df_barang["Stok Sistem"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Jenis Barang", f"{total_jenis} Jenis")
    col2.metric("Total Unit dalam Stok", f"{total_item} Unit")

    st.subheader("Daftar Inventaris Lengkap dengan Tanggal Kedatangan & Expire")
    df_styled = df_barang.style.apply(warnai_manual, axis=1)
    st.dataframe(df_styled, use_container_width=True)

# ==========================================
# 2. PEMETAAN RAK
# ==========================================
elif menu == "📍 Pemetaan Rak":
  st.title("📍 Denah & Pemetaan Posisi Rak Barang")
  st.markdown("Cek posisi letak barang berdasarkan Nama Rak, Nomor, dan Tingkatnya.")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang.")
  else:
    daftar_nama_rak = ["Semua Nama Rak"] + sorted(
        df_barang["Nama Rak"].dropna().unique().tolist()
    )
    pilih_nama_rak = st.selectbox("Filter Berdasarkan Nama Rak", daftar_nama_rak)

    if pilih_nama_rak == "Semua Nama Rak":
      df_tampil = df_barang
    else:
      df_tampil = df_barang[df_barang["Nama Rak"] == pilih_nama_rak]

    st.subheader(f"Daftar Barang di {pilih_nama_rak}")
    df_tampil_styled = df_tampil[[
        "Kode Barang",
        "Nama Barang",
        "Tgl Kedatangan",
        "Tgl Expire",
        "Nama Rak",
        "Nomor Rak",
        "Tingkat Rak",
        "Stok Sistem",
    ]].style.apply(warnai_manual, axis=1)
    st.dataframe(df_tampil_styled, use_container_width=True)

# ==========================================
# 3. RIWAYAT TRANSAKSI (BARU)
# ==========================================
elif menu == "📜 Riwayat Transaksi":
  st.title("📜 Riwayat Barang Masuk & Keluar")
  st.markdown(
      "Catatan seluruh aktivitas keluar masuk material beserta tanggal dan"
      " jamnya."
  )
  st.markdown("---")

  if df_transaksi.empty:
    st.info("Belum ada riwayat transaksi barang masuk atau keluar.")
  else:
    # Filter tipe transaksi (Semua, MASUK, KELUAR)
    filter_tipe = st.selectbox(
        "Filter Tipe Transaksi", ["Semua", "MASUK", "KELUAR"]
    )
    if filter_tipe != "Semua":
      df_trx_tampil = df_transaksi[df_transaksi["Tipe"] == filter_tipe]
    else:
      df_trx_tampil = df_transaksi

    # Tampilkan urut dari yang paling baru
    df_trx_tampil = df_trx_tampil.iloc[::-1]

    st.dataframe(df_trx_tampil, use_container_width=True)

# ==========================================
# 4. EDIT DATA BARANG
# ==========================================
elif menu == "✏️ Edit Data Barang":
  st.title("✏️ Edit Lengkap Data, Tanggal & Lokasi Rak")
  st.markdown(
      "Pilih barang yang ingin diubah, lalu perbarui informasi datanya di"
      " bawah."
  )
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang untuk diedit!")
  else:
    pilih_brg = st.selectbox(
        "Pilih Barang yang Ingin Diedit",
        df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"],
    )

    kode_lama = pilih_brg.split(" - ")[0]
    data_lama = df_barang.loc[df_barang["Kode Barang"] == kode_lama].iloc[0]

    with st.form("form_edit_semua"):
      kode_baru_input = st.text_input(
          "Kode Barang", value=str(data_lama["Kode Barang"])
      )
      nama_baru_input = st.text_input(
          "Nama Barang", value=str(data_lama["Nama Barang"])
      )
      kategori_baru_input = st.text_input(
          "Kategori", value=str(data_lama["Kategori"])
      )

      try:
        def_tgl_datang = (
            datetime.strptime(str(data_lama["Tgl Kedatangan"]), "%Y-%m-%d").date()
            if data_lama["Tgl Kedatangan"] != "-"
            else date.today()
        )
      except:
        def_tgl_datang = date.today()

      try:
        def_tgl_prod = (
            datetime.strptime(str(data_lama["Tgl Produksi"]), "%Y-%m-%d").date()
            if data_lama["Tgl Produksi"] != "-"
            else date.today()
        )
      except:
        def_tgl_prod = date.today()

      try:
        def_tgl_exp = (
            datetime.strptime(str(data_lama["Tgl Expire"]), "%Y-%m-%d").date()
            if data_lama["Tgl Expire"] != "-"
            else date.today()
        )
      except:
        def_tgl_exp = date.today()

      col_t1, col_t2, col_t3 = st.columns(3)
      with col_t1:
        tgl_datang_baru = st.date_input(
            "Tanggal Kedatangan", value=def_tgl_datang
        )
      with col_t2:
        tgl_prod_baru = st.date_input("Tanggal Produksi", value=def_tgl_prod)
      with col_t3:
        tgl_exp_baru = st.date_input("Tanggal Expire", value=def_tgl_exp)

      pilihan_warna = [
          "Putih (Normal)",
          "Biru Muda (Karton/Box)",
          "Hijau Muda (Plastik)",
          "Kuning Muda (Sheet/Kertas)",
          "Merah/Pink (Aseptic)",
          "Ungu Muda",
      ]
      warna_lama = (
          data_lama["Warna Label"]
          if data_lama["Warna Label"] in pilihan_warna
          else "Putih (Normal)"
      )
      warna_baru = st.selectbox(
          "Pilih Warna Label Baris",
          pilihan_warna,
          index=pilihan_warna.index(warna_lama),
      )

      nama_rak_baru = st.text_input(
          "Nama Rak / Area", value=str(data_lama["Nama Rak"])
      )

      col_r1, col_r2 = st.columns(2)
      with col_r1:
        nomor_rak_baru = st.text_input(
            "Nomor Rak / Kolom", value=str(data_lama["Nomor Rak"])
        )
      with col_r2:
        tingkat_opsi = ["Level 1 (Bawah)", "Level 2", "Level 3", "Level 4 (Atas)"]
        default_idx = 0
        if data_lama["Tingkat Rak"] in tingkat_opsi:
          default_idx = tingkat_opsi.index(data_lama["Tingkat Rak"])
        tingkat_baru = st.selectbox(
            "Tingkat / Level Rak", tingkat_opsi, index=default_idx
        )

      stok_baru = st.number_input(
          "Stok Sistem",
          min_value=0,
          step=1,
          value=int(data_lama["Stok Sistem"]),
      )
      harga_baru = st.number_input(
          "Harga Satuan (Rp)",
          min_value=0.0,
          step=1000.0,
          format="%.2f",
          value=float(data_lama["Harga Satuan"]),
      )

      submit_simpan_edit = st.form_submit_button("💾 Simpan Perubahan Data")

      if submit_simpan_edit:
        idx = df_barang[df_barang["Kode Barang"] == kode_lama].index[0]
        df_barang.loc[idx, "Kode Barang"] = kode_baru_input
        df_barang.loc[idx, "Nama Barang"] = nama_baru_input
        df_barang.loc[idx, "Kategori"] = kategori_baru_input
        df_barang.loc[idx, "Tgl Kedatangan"] = tgl_datang_baru.strftime(
            "%Y-%m-%d"
        )
        df_barang.loc[idx, "Tgl Produksi"] = tgl_prod_baru.strftime("%Y-%m-%d")
        df_barang.loc[idx, "Tgl Expire"] = tgl_exp_baru.strftime("%Y-%m-%d")
        df_barang.loc[idx, "Warna Label"] = warna_baru
        df_barang.loc[idx, "Nama Rak"] = nama_rak_baru
        df_barang.loc[idx, "Nomor Rak"] = nomor_rak_baru
        df_barang.loc[idx, "Tingkat Rak"] = tingkat_baru
        df_barang.loc[idx, "Stok Sistem"] = stok_baru
        df_barang.loc[idx, "Harga Satuan"] = harga_baru

        df_barang.to_csv(DB_BARANG, index=False)
        st.success(f"Data barang `{nama_baru_input}` berhasil diperbarui!")
        st.rerun()

# ==========================================
# 5. HAPUS BARANG
# ==========================================
elif menu == "🗑️ Hapus Barang":
  st.title("🗑️ Hapus Data Barang")
  st.markdown("Pilih barang yang ingin dihapus dari daftar inventaris gudang.")
  st.markdown("---")

  if df_barang.empty:
    st.info("Tidak ada data barang untuk dihapus.")
  else:
    with st.form("form_hapus_barang"):
      pilih_hapus = st.selectbox(
          "Pilih Barang yang Akan Dihapus",
          df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"],
      )
      konfirmasi = st.checkbox("Saya yakin ingin menghapus barang ini")
      submit_hapus = st.form_submit_button("🗑️ Hapus Barang")

      if submit_hapus:
        if konfirmasi:
          kode_hapus = pilih_hapus.split(" - ")[0]
          df_barang = df_barang[df_barang["Kode Barang"] != kode_hapus]
          df_barang.to_csv(DB_BARANG, index=False)
          st.success(f"Barang `{kode_hapus}` berhasil dihapus dari sistem!")
          st.rerun()
        else:
          st.error("Silakan centang kotak konfirmasi terlebih dahulu!")

# ==========================================
# 6. BARANG MASUK
# ==========================================
elif menu == "📥 Barang Masuk":
  st.title("📥 Input Barang Masuk")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Tambahkan master barang terlebih dahulu!")
  else:
    with st.form("form_barang_masuk"):
      kode_pilih = st.selectbox(
          "Pilih Barang",
          df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"],
      )
      jumlah_masuk = st.number_input(
          "Jumlah Masuk", min_value=1, step=1, value=1
      )
      keterangan = st.text_input("Keterangan / Supplier", "Pembelian Baru")
      submit = st.form_submit_button("Simpan Barang Masuk")

      if submit:
        kode_barang = kode_pilih.split(" - ")[0]
        nama_barang = df_barang.loc[
            df_barang["Kode Barang"] == kode_barang, "Nama Barang"
        ].values[0]

        df_barang.loc[df_barang["Kode Barang"] == kode_barang, "Stok Sistem"] += (
            jumlah_masuk
        )
        df_barang.to_csv(DB_BARANG, index=False)

        new_trx = pd.DataFrame([{
            "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Kode Barang": kode_barang,
            "Nama Barang": nama_barang,
            "Tipe": "MASUK",
            "Jumlah": jumlah_masuk,
            "Keterangan": keterangan,
        }])
        df_transaksi = pd.concat([df_transaksi, new_trx], ignore_index=True)
        df_transaksi.to_csv(DB_TRANSAKSI, index=False)

        st.success(f"Berhasil menambahkan {jumlah_masuk} unit ke {nama_barang}!")

# ==========================================
# 7. BARANG KELUAR
# ==========================================
elif menu == "📤 Barang Keluar":
  st.title("📤 Input Barang Keluar")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang!")
  else:
    with st.form("form_barang_keluar"):
      kode_pilih = st.selectbox(
          "Pilih Barang",
          df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"],
      )
      jumlah_keluar = st.number_input(
          "Jumlah Keluar", min_value=1, step=1, value=1
      )
      keterangan = st.text_input("Keterangan / Tujuan", "Pengiriman ke Toko")
      submit = st.form_submit_button("Simpan Barang Keluar")

      if submit:
        kode_barang = kode_pilih.split(" - ")[0]
        stok_sekarang = df_barang.loc[
            df_barang["Kode Barang"] == kode_barang, "Stok Sistem"
        ].values[0]
        nama_barang = df_barang.loc[
            df_barang["Kode Barang"] == kode_barang, "Nama Barang"
        ].values[0]

        if jumlah_keluar > stok_sekarang:
          st.error(
              f"Stok tidak mencukupi! Stok saat ini: {stok_sekarang} unit."
          )
        else:
          df_barang.loc[
              df_barang["Kode Barang"] == kode_barang, "Stok Sistem"
          ] -= jumlah_keluar
          df_barang.to_csv(DB_BARANG, index=False)

          new_trx = pd.DataFrame([{
              "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "Kode Barang": kode_barang,
              "Nama Barang": nama_barang,
              "Tipe": "KELUAR",
              "Jumlah": jumlah_keluar,
              "Keterangan": keterangan,
          }])
          df_transaksi = pd.concat([df_transaksi, new_trx], ignore_index=True)
          df_transaksi.to_csv(DB_TRANSAKSI, index=False)

          st.success(
              f"Berhasil mengeluarkan {jumlah_keluar} unit {nama_barang}!"
          )

# ==========================================
# 8. STOK OPNAME
# ==========================================
elif menu == "📋 Stok Opname":
  st.title("📋 Cek Stok Opname (Audit Fisik)")
  st.markdown(
      "Bandingkan jumlah stok sistem dengan perhitungan fisik di rak gudang."
  )
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang untuk di-opname.")
  else:
    st.subheader("Formulir Audit Fisik per Rak")

    opname_data = []
    for index, row in df_barang.iterrows():
      col1, col2, col3 = st.columns([3, 2, 2])
      with col1:
        st.write(
            f"**{row['Nama Barang']}** (`{row['Kode Barang']}`)"
            f" <br><small><b>Rak:</b> {row['Nama Rak']} - {row['Nomor Rak']}"
            f" ({row['Tingkat Rak']}) | <b>Exp:</b> {row['Tgl Expire']}</small>",
            unsafe_allow_html=True,
        )
      with col2:
        st.write(f"Stok Sistem: **{row['Stok Sistem']}**")
      with col3:
        fisik = st.number_input(
            f"Fisik {row['Kode Barang']}",
            min_value=0,
            value=int(row["Stok Sistem"]),
            key=f"opname_{row['Kode Barang']}",
            label_visibility="collapsed",
        )
      opname_data.append({
          "Kode Barang": row["Kode Barang"],
          "Nama Barang": row["Nama Barang"],
          "Kategori": row["Kategori"],
          "Warna Label": row["Warna Label"],
          "Tgl Kedatangan": row["Tgl Kedatangan"],
          "Tgl Produksi": row["Tgl Produksi"],
          "Tgl Expire": row["Tgl Expire"],
          "Nama Rak": row["Nama Rak"],
          "Nomor Rak": row["Nomor Rak"],
          "Tingkat Rak": row["Tingkat Rak"],
          "Stok Sistem": row["Stok Sistem"],
          "Stok Fisik": fisik,
      })

    if st.button("🔍 Proses & Periksa Selisih"):
      df_opname = pd.DataFrame(opname_data)
      df_opname["Selisih (Fisik - Sistem)"] = (
          df_opname["Stok Fisik"] - df_opname["Stok Sistem"]
      )

      st.markdown("---")
      st.subheader("Hasil Laporan Stok Opname")
      df_opname_styled = df_opname.style.apply(warnai_manual, axis=1)
      st.dataframe(df_opname_styled, use_container_width=True)

      if st.button("💾 Sinkronkan Stok Sistem dengan Fisik Aktual"):
        for _, row in df_opname.iterrows():
          df_barang.loc[
              df_barang["Kode Barang"] == row["Kode Barang"], "Stok Sistem"
          ] = row["Stok Fisik"]
        df_barang.to_csv(DB_BARANG, index=False)
        st.success("Stok sistem berhasil disesuaikan dengan hasil opname fisik!")
        st.rerun()

# ==========================================
# 9. TAMBAH BARANG BARU
# ==========================================
elif menu == "➕ Tambah Barang Baru":
  st.title("➕ Tambah Master Barang, Tanggal & Lokasi")
  st.markdown("---")

  with st.form("form_tambah_barang"):
    kode_baru = st.text_input("Kode Barang (Contoh: BRG001)")
    nama_baru = st.text_input("Nama Barang")
    kategori = st.text_input("Kategori Barang")

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
      tgl_datang = st.date_input("Tanggal Kedatangan", value=date.today())
    with col_t2:
      tgl_prod = st.date_input("Tanggal Produksi", value=date.today())
    with col_t3:
      tgl_exp = st.date_input("Tanggal Expire", value=date.today())

    pilihan_warna = [
        "Putih (Normal)",
        "Biru Muda (Karton/Box)",
        "Hijau Muda (Plastik)",
        "Kuning Muda (Sheet/Kertas)",
        "Merah/Pink (Aseptic)",
        "Ungu Muda",
    ]
    warna_pilih = st.selectbox("Pilih Warna Label Baris", pilihan_warna)

    nama_rak = st.text_input("Nama Rak / Area (Contoh: Rak Besi A)")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
      nomor_rak = st.text_input("Nomor Rak / Kolom (Contoh: Rak 1)")
    with col_r2:
      tingkat_rak = st.selectbox(
          "Tingkat / Level Rak",
          ["Level 1 (Bawah)", "Level 2", "Level 3", "Level 4 (Atas)"],
      )

    stok_awal = st.number_input("Stok Awal", min_value=0, step=1)
    harga = st.number_input(
        "Harga Satuan (Rp)", min_value=0.0, step=1000.0, format="%.2f"
    )

    submit_barang = st.form_submit_button("Simpan Barang Lengkap")

    if submit_barang:
      if not kode_baru or not nama_baru:
        st.error("Kode dan Nama Barang wajib diisi!")
      elif kode_baru in df_barang["Kode Barang"].values:
        st.error("Kode barang sudah terdaftar!")
      else:
        new_row = pd.DataFrame([{
            "Kode Barang": kode_baru,
            "Nama Barang": nama_baru,
            "Kategori": kategori if kategori else "-",
            "Warna Label": warna_pilih,
            "Tgl Kedatangan": tgl_datang.strftime("%Y-%m-%d"),
            "Tgl Produksi": tgl_prod.strftime("%Y-%m-%d"),
            "Tgl Expire": tgl_exp.strftime("%Y-%m-%d"),
            "Nama Rak": nama_rak if nama_rak else "-",
            "Nomor Rak": nomor_rak if nomor_rak else "-",
            "Tingkat Rak": tingkat_rak,
            "Stok Sistem": stok_awal,
            "Harga Satuan": harga,
        }])
        df_barang = pd.concat([df_barang, new_row], ignore_index=True)
        df_barang.to_csv(DB_BARANG, index=False)
        st.success(
            f"Barang `{nama_baru}` berhasil disimpan lengkap dengan tanggal"
            " kedatangan & expire!"
        )
