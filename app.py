from datetime import datetime, date, timedelta, timezone
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
            "No Batch",
            "Kategori",
            "Warna Label",
            "Tgl Kedatangan",
            "Tgl Produksi",
            "Tgl Expire",
            "Nama Rak",
            "Nomor Rak",
            "Tingkat Rak",
            "Stok Sistem",
            "Satuan",
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
if "No Batch" not in df_barang.columns:
  df_barang["No Batch"] = "-"
if "Satuan" not in df_barang.columns:
  df_barang["Satuan"] = "Pcs"
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
df_barang.to_csv(DB_BARANG, index=False)

df_transaksi = pd.read_csv(DB_TRANSAKSI)


# Fungsi Waktu WIB (GMT+7)
def get_waktu_wib():
  tz_wib = timezone(timedelta(hours=7))
  return datetime.now(tz_wib).strftime("%Y-%m-%d %H:%M")


# Fungsi untuk memberikan warna latar belakang baris tabel berdasarkan pilihan manual
def warnai_manual(row):
  warna = str(row.get("Warna Label", ""))
  if "Biru" in warna:
    return ["background-color: #d1ecf1"] * len(row)
  elif "Hijau" in warna:
    return ["background-color: #d4edda"] * len(row)
  elif "Kuning" in warna:
    return ["background-color: #fff3cd"] * len(row)
  elif "Merah" in warna or "Pink" in warna:
    return ["background-color: #f8d7da"] * len(row)
  elif "Ungu" in warna:
    return ["background-color: #e2d9f3"] * len(row)
  else:
    return [""] * len(row)


# Judul Utama Aplikasi di HP
st.title("📦 Aplikasi Manajemen Gudang")

# Navigasi Model Tab Menu di Atas (Horizontal Tabs) yang Nyaman untuk HP
menu = st.tabs([
    "📊 Dashboard",
    "📷 Scan/Cek Rak",
    "📍 Pemetaan",
    "📥 Masuk",
    "📤 Keluar",
    "📜 Riwayat",
    "✏️ Edit",
    "🗑️ Hapus",
    "📋 Opname",
    "➕ Tambah",
])

# ==========================================
# 1. DASHBOARD STOK
# ==========================================
with menu[0]:
  st.subheader("📊 Dashboard Stok & Ringkasan Material")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang. Silakan tambah barang baru melalui menu ➕.")
  else:
    total_jenis = len(df_barang)
    total_item = df_barang["Stok Sistem"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Jenis / Lot", f"{total_jenis} Jenis")
    col2.metric("Total Qty Unit", f"{total_item} Unit")

    st.markdown("---")
    keyword = st.text_input(
        "🔍 Ketik nama barang, kode, atau no batch untuk mencari:"
    )

    if keyword:
      df_sumber = df_barang[
          df_barang.astype(str)
          .apply(lambda row: row.str.contains(keyword, case=False).any(), axis=1)
      ]
      st.write(
          f"Ditemukan {len(df_sumber)} hasil untuk kata kunci: **{keyword}**"
      )
    else:
      df_sumber = df_barang

    if not df_sumber.empty:
      st.markdown("### 📋 Ringkasan Stok Utama (Multi-Palet)")
      kolom_ringkas = [
          "Kode Barang",
          "Nama Barang",
          "Stok Sistem",
          "Satuan",
          "Nama Rak",
          "Nomor Rak",
          "Tgl Kedatangan",
      ]
      df_ringkas_styled = df_sumber[kolom_ringkas].style.apply(
          warnai_manual, axis=1
      )
      st.dataframe(df_ringkas_styled, use_container_width=True)

      st.markdown("---")
      # Menggunakan Expander agar detail tertutup rapi dan hanya muncul saat diklik
      with st.expander("🔎 Klik di sini untuk Melihat Detail Lengkap Material"):
        pilih_detail = st.selectbox(
            "Pilih Material / Palet",
            df_sumber["Kode Barang"] + " - " + df_sumber["Nama Barang"],
        )

        if pilih_detail:
          kode_pilih = pilih_detail.split(" - ")[0]
          row_detail = df_sumber[df_sumber["Kode Barang"] == kode_pilih].iloc[0]

          st.info(
              f"📦 **Nama Material:** {row_detail['Nama Barang']}\n\n"
              f"🏷️ **Kode / Lot Palet:** `{row_detail['Kode Barang']}`\n\n"
              f"🔖 **No Batch / Lot No:** `{row_detail['No Batch']}`\n\n"
              f"🏷️ **Kategori:** {row_detail['Kategori']} | 🎨 **Label:**"
              f" {row_detail['Warna Label']}\n\n"
              f"📍 **Lokasi Rak:** {row_detail['Nama Rak']} - Kolom"
              f" {row_detail['Nomor Rak']} ({row_detail['Tingkat Rak']})\n\n"
              f"📊 **Stok Palet Ini:** **{row_detail['Stok Sistem']}"
              f" {row_detail['Satuan']}**\n\n"
              f"📥 **Incoming Date (Tanggal Kedatangan):**"
              f" `{row_detail['Tgl Kedatangan']}`\n\n"
              f"🏭 **Prode Date (Produksi):** `{row_detail['Tgl Produksi']}`\n\n"
              f"⏳ **Exp. Date (Kadaluarsa):** `{row_detail['Tgl Expire']}`"
          )
    else:
      st.warning("Material tidak ditemukan.")

    st.markdown("---")
    st.markdown("### 📈 Grafik Statistik Stok per Rak")
    if "Nama Rak" in df_barang.columns and not df_barang.empty:
      df_grafik = df_barang.groupby("Nama Rak")["Stok Sistem"].sum()
      st.bar_chart(df_grafik)

# ==========================================
# 2. SCAN BARCODE / CEK RAK
# ==========================================
with menu[1]:
  st.subheader("📷 Scan Barcode / Cek Rak Instan")
  st.markdown(
      "Gunakan kamera HP atau pilih nama rak untuk melihat seluruh isi palet"
      " barang."
  )
  st.markdown("---")

  gambar_kamera = st.camera_input("Ambil Foto Barcode Rak")
  if gambar_kamera:
    st.success("Barcode berhasil dipindai oleh kamera!")

  st.markdown("---")
  if df_barang.empty:
    st.info("Belum ada data barang di gudang.")
  else:
    daftar_rak = ["-- Pilih Nama Rak --"] + sorted(
        df_barang["Nama Rak"].dropna().unique().tolist()
    )
    pilih_rak_scan = st.selectbox("Pilih Nama Rak / Area Gudang", daftar_rak)

    if pilih_rak_scan != "-- Pilih Nama Rak --":
      df_hasil_rak = df_barang[df_barang["Nama Rak"] == pilih_rak_scan]
      st.success(
          f"Ditemukan {len(df_hasil_rak)} data palet di **{pilih_rak_scan}**:"
      )

      for _, row in df_hasil_rak.iterrows():
        st.info(
            f"📦 **{row['Nama Barang']}**\n\n"
            f"🏷️ **Kode/Lot:** `{row['Kode Barang']}` | 🔖 **Batch:**"
            f" `{row['No Batch']}`\n\n"
            f"📌 **Lokasi:** {row['Nama Rak']} - No. {row['Nomor Rak']} ("
            f"{row['Tingkat Rak']})\n\n"
            f"📊 **Stok:** **{row['Stok Sistem']} {row['Satuan']}** | 📥"
            f" **Datang:** {row['Tgl Kedatangan']} | ⏳ **Exp:**"
            f" {row['Tgl Expire']}"
        )

# ==========================================
# 3. PEMETAAN RAK (VISUAL)
# ==========================================
with menu[2]:
  st.subheader("📍 Layout & Pemetaan Posisi Rak Bertingkat")
  st.markdown("Visualisasi penempatan material per rak.")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang.")
  else:
    daftar_nama_rak = sorted(df_barang["Nama Rak"].dropna().unique().tolist())
    pilih_nama_rak = st.selectbox(
        "🏢 Pilih Nama Rak / Area Gudang",
        daftar_nama_rak,
        key="pilih_rak_visual",
    )

    st.markdown(f"### 📦 Visualisasi Rak: **{pilih_nama_rak}**")
    df_rak = df_barang[df_barang["Nama Rak"] == pilih_nama_rak]

    if df_rak.empty:
      st.warning(f"Belum ada material di {pilih_nama_rak}.")
    else:
      tingkat_list = [
          "Level 4 (Atas)",
          "Level 3",
          "Level 2",
          "Level 1 (Bawah)",
      ]

      for lvl in tingkat_list:
        df_lvl = df_rak[df_rak["Tingkat Rak"] == lvl]
        if not df_lvl.empty:
          with st.container():
            st.markdown(f"**🪜 {lvl}**")
            cols = st.columns(min(len(df_lvl), 3))
            for i, (_, row) in enumerate(df_lvl.iterrows()):
              with cols[i % len(cols)]:
                st.info(
                    f"**{row['Nama Barang']}**\n\n"
                    f"🏷️ **Kode/Lot:** `{row['Kode Barang']}`\n\n"
                    f"🔖 **Batch:** {row['No Batch']}\n\n"
                    f"📌 **Blok/Kolom:** {row['Nomor Rak']}\n\n"
                    f"📦 **Stok:** {row['Stok Sistem']} {row['Satuan']}\n\n"
                    f"📥 **Datang:** {row['Tgl Kedatangan']}\n\n"
                    f"⏳ **Exp:** {row['Tgl Expire']}"
                )
            st.markdown("---")

# ==========================================
# 4. BARANG MASUK
# ==========================================
with menu[3]:
  st.subheader("📥 Input Barang Masuk (Palet / Kedatangan Baru)")
  st.markdown(
      "Catat kedatangan material baru lengkap dengan tanggal masuk, batch,"
      " dan tanggal kedaluwarsa."
  )
  st.markdown("---")

  with st.form("form_barang_masuk_lengkap"):
    kode_baru = st.text_input(
        "Kode / No Lot Palet Baru (Contoh: PM-00003-4)"
    )
    nama_baru = st.text_input(
        "Nama Material (Contoh: Carton klatu Premium @65 mL)"
    )
    batch_baru = st.text_input("Lot / Batch No (Opsional)")
    kategori = st.text_input(
        "Kategori Barang (Contoh: Packaging / Chemical)"
    )

    ada_tgl_prod_masuk = st.checkbox(
        "Ada Tanggal Produksi? (Centang jika ada, kosongkan jika tidak ada)",
        value=True,
        key="chk_prod_masuk",
    )
    ada_tgl_exp_masuk = st.checkbox(
        "Ada Tanggal Expire? (Centang jika ada, kosongkan jika tidak ada)",
        value=True,
        key="chk_exp_masuk",
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
      tgl_datang = st.date_input("Incoming Date (Tanggal Kedatangan)")
    with col_t2:
      tgl_prod = st.date_input("Prode Date", value=date.today(), key="prod_masuk")
    with col_t3:
      tgl_exp = st.date_input("Exp. Date", value=date.today(), key="exp_masuk")

    pilihan_warna = [
        "Putih (Normal)",
        "Biru Muda (Karton/Box)",
        "Hijau Muda (Plastik)",
        "Kuning Muda (Sheet/Kertas)",
        "Merah/Pink (Aseptic)",
        "Ungu Muda",
    ]
    warna_pilih = st.selectbox(
        "Pilih Warna Label Baris", pilihan_warna, key="warna_masuk"
    )

    nama_rak = st.text_input(
        "Nama Rak / Area (Contoh: Rak Packaging A)", key="rak_masuk"
    )

    col_r1, col_r2 = st.columns(2)
    with col_r1:
      nomor_rak = st.text_input(
          "Nomor Rak / Kolom (Contoh: Rak 1)", key="norak_masuk"
      )
    with col_r2:
      tingkat_rak = st.selectbox(
          "Tingkat / Level Rak",
          ["Level 1 (Bawah)", "Level 2", "Level 3", "Level 4 (Atas)"],
          key="tingkat_masuk",
      )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
      stok_awal = st.number_input(
          "Qty (Jumlah Barang Masuk)", min_value=1, step=1, value=1
      )
    with col_s2:
      satuan_pilih = st.selectbox(
          "Satuan (Unit)",
          ["Pcs", "Kg", "Zak", "Ltr", "Box", "Drum", "Pail", "Roll"],
          key="satuan_masuk",
      )

    keterangan = st.text_input("Keterangan / Supplier", "Pembelian / Datang Baru")

    submit_masuk = st.form_submit_button("Simpan Barang Masuk")

    if submit_masuk:
      if not kode_baru or not nama_baru:
        st.error("Kode dan Nama Material wajib diisi!")
      elif kode_baru in df_barang["Kode Barang"].values:
        st.error("Kode/Lot palet tersebut sudah terdaftar di sistem!")
      else:
        final_tgl_prod = (
            tgl_prod.strftime("%Y-%m-%d") if ada_tgl_prod_masuk else "-"
        )
        final_tgl_exp = (
            tgl_exp.strftime("%Y-%m-%d") if ada_tgl_exp_masuk else "-"
        )

        new_row = pd.DataFrame([{
            "Kode Barang": kode_baru,
            "Nama Barang": nama_baru,
            "No Batch": batch_baru if batch_baru else "-",
            "Kategori": kategori if kategori else "-",
            "Warna Label": warna_pilih,
            "Tgl Kedatangan": tgl_datang.strftime("%Y-%m-%d"),
            "Tgl Produksi": final_tgl_prod,
            "Tgl Expire": final_tgl_exp,
            "Nama Rak": nama_rak if nama_rak else "-",
            "Nomor Rak": nomor_rak if nomor_rak else "-",
            "Tingkat Rak": tingkat_rak,
            "Stok Sistem": stok_awal,
            "Satuan": satuan_pilih,
        }])
        df_barang = pd.concat([df_barang, new_row], ignore_index=True)
        df_barang.to_csv(DB_BARANG, index=False)

        new_trx = pd.DataFrame([{
            "Tanggal": get_waktu_wib(),
            "Kode Barang": kode_baru,
            "Nama Barang": nama_baru,
            "Tipe": "MASUK",
            "Jumlah": stok_awal,
            "Keterangan": keterangan,
        }])
        df_transaksi = pd.concat([df_transaksi, new_trx], ignore_index=True)
        df_transaksi.to_csv(DB_TRANSAKSI, index=False)

        st.success(
            f"Barang Masuk `{nama_baru}` (Tgl Kedatangan: {tgl_datang.strftime('%Y-%m-%d')} | Qty: {stok_awal} {satuan_pilih}) berhasil disimpan & tercatat di riwayat!"
        )

# ==========================================
# 5. BARANG KELUAR
# ==========================================
with menu[4]:
  st.subheader("📤 Input Barang Keluar")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang!")
  else:
    with st.form("form_barang_keluar"):
      kode_pilih = st.selectbox(
          "Pilih Barang / Palet",
          df_barang["Kode Barang"]
          + " - "
          + df_barang["Nama Barang"]
          + " (Datang: "
          + df_barang["Tgl Kedatangan"]
          + ")",
          key="pilih_keluar",
      )
      jumlah_keluar = st.number_input(
          "Jumlah Keluar", min_value=1, step=1, value=1
      )
      keterangan = st.text_input("Keterangan / Tujuan", "Pengiriman ke Produksi")
      submit = st.form_submit_button("Simpan Barang Keluar")

      if submit:
        kode_barang = kode_pilih.split(" - ")[0]
        idx = df_barang[df_barang["Kode Barang"] == kode_barang].index[0]
        stok_sekarang = int(df_barang.loc[idx, "Stok Sistem"])
        nama_barang = df_barang.loc[idx, "Nama Barang"]

        if jumlah_keluar > stok_sekarang:
          st.error(
              f"Stok tidak mencukupi! Stok palet ini: {stok_sekarang} unit."
          )
        else:
          df_barang.loc[idx, "Stok Sistem"] -= jumlah_keluar
          df_barang.to_csv(DB_BARANG, index=False)

          new_trx = pd.DataFrame([{
              "Tanggal": get_waktu_wib(),
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
# 6. RIWAYAT TRANSAKSI
# ==========================================
with menu[5]:
  st.subheader("📜 Riwayat Barang Masuk & Keluar")
  st.markdown("Catatan aktivitas keluar masuk material beserta tanggal & jamnya.")
  st.markdown("---")

  if df_transaksi.empty:
    st.info("Belum ada riwayat transaksi.")
  else:
    filter_tipe = st.selectbox(
        "Filter Tipe Transaksi", ["Semua", "MASUK", "KELUAR"]
    )
    if filter_tipe != "Semua":
      df_trx_tampil = df_transaksi[df_transaksi["Tipe"] == filter_tipe]
    else:
      df_trx_tampil = df_transaksi

    df_trx_tampil = df_trx_tampil.iloc[::-1]
    st.dataframe(df_trx_tampil, use_container_width=True)

# ==========================================
# 7. EDIT DATA BARANG
# ==========================================
with menu[6]:
  st.subheader("✏️ Edit Data Barang & Lokasi")
  st.markdown("Perbarui informasi material di gudang.")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang untuk diedit!")
  else:
    pilih_brg = st.selectbox(
        "Pilih Barang / Palet yang Ingin Diedit",
        df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"],
        key="pilih_edit_barang",
    )

    kode_lama = pilih_brg.split(" - ")[0]
    data_lama = df_barang.loc[df_barang["Kode Barang"] == kode_lama].iloc[0]

    with st.form("form_edit_semua"):
      kode_baru_input = st.text_input(
          "Kode Barang / Lot Palet", value=str(data_lama["Kode Barang"])
      )
      nama_baru_input = st.text_input(
          "Nama Material", value=str(data_lama["Nama Barang"])
      )
      batch_baru_input = st.text_input(
          "No Batch / Lot No",
          value=(
              str(data_lama["No Batch"])
              if data_lama["No Batch"] != "-"
              else ""
          ),
      )
      kategori_baru_input = st.text_input(
          "Kategori", value=str(data_lama["Kategori"])
      )

      ada_tgl_prod = st.checkbox(
          "Ada Tanggal Produksi?",
          value=(True if data_lama["Tgl Produksi"] != "-" else False),
      )
      ada_tgl_exp = st.checkbox(
          "Ada Tanggal Expire?",
          value=(True if data_lama["Tgl Expire"] != "-" else False),
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
            "Incoming Date (Kedatangan)", value=def_tgl_datang
        )
      with col_t2:
        tgl_prod_baru = st.date_input("Prode Date", value=def_tgl_prod)
      with col_t3:
        tgl_exp_baru = st.date_input("Exp. Date", value=def_tgl_exp)

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
        tingkat_opsi = [
            "Level 1 (Bawah)",
            "Level 2",
            "Level 3",
            "Level 4 (Atas)",
        ]
        default_idx = 0
        if data_lama["Tingkat Rak"] in tingkat_opsi:
          default_idx = tingkat_opsi.index(data_lama["Tingkat Rak"])
        tingkat_baru = st.selectbox(
            "Tingkat / Level Rak", tingkat_opsi, index=default_idx
        )

      col_s1, col_s2 = st.columns(2)
      with col_s1:
        stok_baru = st.number_input(
            "Qty (Jumlah Stok)",
            min_value=0,
            step=1,
            value=int(data_lama["Stok Sistem"]),
        )
      with col_s2:
        satuan_opsi = ["Pcs", "Kg", "Zak", "Ltr", "Box", "Drum", "Pail", "Roll"]
        satuan_lama = (
            data_lama["Satuan"] if data_lama["Satuan"] in satuan_opsi else "Pcs"
        )
        satuan_baru = st.selectbox(
            "Satuan (Unit)", satuan_opsi, index=satuan_opsi.index(satuan_lama)
        )

      submit_simpan_edit = st.form_submit_button("💾 Simpan Perubahan Data")

      if submit_simpan_edit:
        idx = df_barang[df_barang["Kode Barang"] == kode_lama].index[0]
        df_barang.loc[idx, "Kode Barang"] = kode_baru_input
        df_barang.loc[idx, "Nama Barang"] = nama_baru_input
        df_barang.loc[idx, "No Batch"] = (
            batch_baru_input if batch_baru_input else "-"
        )
        df_barang.loc[idx, "Kategori"] = kategori_baru_input
        df_barang.loc[idx, "Tgl Kedatangan"] = tgl_datang_baru.strftime(
            "%Y-%m-%d"
        )
        df_barang.loc[idx, "Tgl Produksi"] = (
            tgl_prod_baru.strftime("%Y-%m-%d") if ada_tgl_prod else "-"
        )
        df_barang.loc[idx, "Tgl Expire"] = (
            tgl_exp_baru.strftime("%Y-%m-%d") if ada_tgl_exp else "-"
        )
        df_barang.loc[idx, "Warna Label"] = warna_baru
        df_barang.loc[idx, "Nama Rak"] = nama_rak_baru
        df_barang.loc[idx, "Nomor Rak"] = nomor_rak_baru
        df_barang.loc[idx, "Tingkat Rak"] = tingkat_baru
        df_barang.loc[idx, "Stok Sistem"] = stok_baru
        df_barang.loc[idx, "Satuan"] = satuan_baru

        df_barang.to_csv(DB_BARANG, index=False)
        st.success(f"Data material `{nama_baru_input}` berhasil diperbarui!")
        st.rerun()

# ==========================================
# 8. HAPUS BARANG
# ==========================================
with menu[7]:
  st.subheader("🗑️ Hapus Data Barang")
  st.markdown("Pilih barang yang ingin dihapus dari inventaris.")
  st.markdown("---")

  if df_barang.empty:
    st.info("Tidak ada data barang untuk dihapus.")
  else:
    with st.form("form_hapus_barang"):
      pilih_hapus = st.selectbox(
          "Pilih Barang yang Akan Dihapus",
          df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"],
          key="pilih_hapus_barang",
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
# 9. STOK OPNAME
# ==========================================
with menu[8]:
  st.subheader("📋 Cek Stok Opname (Audit Fisik)")
  st.markdown("Bandingkan jumlah stok sistem dengan perhitungan fisik di rak.")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang untuk di-opname.")
  else:
    st.markdown("### Formulir Audit Fisik per Rak")

    opname_data = []
    for index, row in df_barang.iterrows():
      col1, col2, col3 = st.columns([3, 2, 2])
      with col1:
        st.write(
            f"**{row['Nama Barang']}** (`{row['Kode Barang']}`)"
            f" <br><small><b>Batch:</b> {row['No Batch']} | <b>Rak:</b>"
            f" {row['Nama Rak']}-{row['Nomor Rak']} ({row['Tingkat Rak']})"
            f" | <b>Datang:</b> {row['Tgl Kedatangan']}</small>",
            unsafe_allow_html=True,
        )
      with col2:
        st.write(f"Stok Sistem: **{row['Stok Sistem']} {row['Satuan']}**")
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
          "No Batch": row["No Batch"],
          "Kategori": row["Kategori"],
          "Warna Label": row["Warna Label"],
          "Tgl Kedatangan": row["Tgl Kedatangan"],
          "Tgl Produksi": row["Tgl Produksi"],
          "Tgl Expire": row["Tgl Expire"],
          "Nama Rak": row["Nama Rak"],
          "Nomor Rak": row["Nomor Rak"],
          "Tingkat Rak": row["Tingkat Rak"],
          "Stok Sistem": row["Stok Sistem"],
          "Satuan": row["Satuan"],
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
# 10. TAMBAH BARANG BARU (MASTER)
# ==========================================
with menu[9]:
  st.subheader("➕ Tambah Master Material Baru")
  st.markdown("---")

  with st.form("form_tambah_barang_baru"):
    kode_baru = st.text_input("Kode Barang / Lot (Contoh: PM-00003)")
    nama_baru = st.text_input(
        "Material Name (Contoh: Carton klatu Premium @65 mL)"
    )
    batch_baru = st.text_input("Lot / Batch No (Opsional)")
    kategori = st.text_input("Kategori Barang (Contoh: Packaging)")

    ada_tgl_prod_tambah = st.checkbox(
        "Ada Tanggal Produksi?", value=True, key="chk_prod_tambah"
    )
    ada_tgl_exp_tambah = st.checkbox(
        "Ada Tanggal Expire?", value=True, key="chk_exp_tambah"
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
      tgl_datang = st.date_input("Incoming Date", key="datang_tambah")
    with col_t2:
      tgl_prod = st.date_input("Prode Date", value=date.today(), key="prod_tambah")
    with col_t3:
      tgl_exp = st.date_input("Exp. Date", value=date.today(), key="exp_tambah")

    pilihan_warna = [
        "Putih (Normal)",
        "Biru Muda (Karton/Box)",
        "Hijau Muda (Plastik)",
        "Kuning Muda (Sheet/Kertas)",
        "Merah/Pink (Aseptic)",
        "Ungu Muda",
    ]
    warna_pilih = st.selectbox(
        "Pilih Warna Label Baris", pilihan_warna, key="warna_tambah"
    )

    nama_rak = st.text_input(
        "Nama Rak / Area (Contoh: Rak Packaging A)", key="rak_tambah"
    )

    col_r1, col_r2 = st.columns(2)
    with col_r1:
      nomor_rak = st.text_input(
          "Nomor Rak / Kolom (Contoh: Rak 1)", key="norak_tambah"
      )
    with col_r2:
      tingkat_rak = st.selectbox(
          "Tingkat / Level Rak",
          ["Level 1 (Bawah)", "Level 2", "Level 3", "Level 4 (Atas)"],
          key="tingkat_tambah",
      )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
      stok_awal = st.number_input(
          "Qty (Jumlah Stok Awal)", min_value=0, step=1, value=0
      )
    with col_s2:
      satuan_pilih = st.selectbox(
          "Satuan (Unit)",
          ["Pcs", "Kg", "Zak", "Ltr", "Box", "Drum", "Pail", "Roll"],
          key="satuan_tambah",
      )

    submit_barang = st.form_submit_button("Simpan Master Material")

    if submit_barang:
      if not kode_baru or not nama_baru:
        st.error("Kode dan Nama Material wajib diisi!")
      elif kode_baru in df_barang["Kode Barang"].values:
        st.error("Kode barang sudah terdaftar!")
      else:
        final_tgl_prod = (
            tgl_prod.strftime("%Y-%m-%d") if ada_tgl_prod_tambah else "-"
        )
        final_tgl_exp = (
            tgl_exp.strftime("%Y-%m-%d") if ada_tgl_exp_tambah else "-"
        )
        new_row = pd.DataFrame([{
            "Kode Barang": kode_baru,
            "Nama Barang": nama_baru,
            "No Batch": batch_baru if batch_baru else "-",
            "Kategori": kategori if kategori else "-",
            "Warna Label": warna_pilih,
            "Tgl Kedatangan": tgl_datang.strftime("%Y-%m-%d"),
            "Tgl Produksi": final_tgl_prod,
            "Tgl Expire": final_tgl_exp,
            "Nama Rak": nama_rak if nama_rak else "-",
            "Nomor Rak": nomor_rak if nomor_rak else "-",
            "Tingkat Rak": tingkat_rak,
            "Stok Sistem": stok_awal,
            "Satuan": satuan_pilih,
        }])
        df_barang = pd.concat([df_barang, new_row], ignore_index=True)
        df_barang.to_csv(DB_BARANG, index=False)
        st.success(
            f"Master Material `{nama_baru}` berhasil disimpan di `{nama_rak}`!"
        )
