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


# Navigasi Sidebar
st.sidebar.title("📌 Menu Gudang")
menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "📊 Dashboard Stok",
        "📍 Pemetaan Rak (Visual)",
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
  st.title("📊 Dashboard Stok & Material Gudang")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang. Silakan tambah barang baru melalui menu.")
  else:
    total_jenis = len(df_barang)
    total_item = df_barang["Stok Sistem"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Jenis / Lot Barang", f"{total_jenis} Jenis")
    col2.metric("Total Qty Seluruh Unit", f"{total_item} Unit")

    st.subheader("Daftar Inventaris Lengkap")
    df_styled = df_barang.style.apply(warnai_manual, axis=1)
    st.dataframe(df_styled, use_container_width=True)

# ==========================================
# 2. PEMETAAN RAK (BENTUK VISUAL RAK)
# ==========================================
elif menu == "📍 Pemetaan Rak (Visual)":
  st.title("📍 Layout & Pemetaan Posisi Rak Bertingkat")
  st.markdown(
      "Visualisasi penempatan material berdasarkan Nama Rak, Nomor Kolom, dan"
      " Tingkat Rak."
  )
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang.")
  else:
    daftar_nama_rak = sorted(df_barang["Nama Rak"].dropna().unique().tolist())
    pilih_nama_rak = st.selectbox(
        "🏢 Pilih Nama Rak / Area Gudang", daftar_nama_rak
    )

    st.markdown(f"### 📦 Visualisasi Rak: **{pilih_nama_rak}**")
    df_rak = df_barang[df_barang["Nama Rak"] == pilih_nama_rak]

    if df_rak.empty:
      st.warning(f"Belum ada material di {pilih_nama_rak}.")
    else:
      # Urutkan berdasarkan tingkat dari atas ke bawah atau sebaliknya
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
            st.markdown(
                f"**🪜 {lvl}** *(Struktur Rak Besi Bertingkat)*"
            )
            cols = st.columns(
                min(len(df_lvl), 3)
            )  # Buat kotak grid per kolom rak
            for i, (_, row) in enumerate(df_lvl.iterrows()):
              with cols[i % len(cols)]:
                st.info(
                    f"**{row['Nama Barang']}**\n\n"
                    f"🏷️ **Kode:** `{row['Kode Barang']}`\n\n"
                    f"🔖 **Batch:** {row['No Batch']}\n\n"
                    f"📌 **Blok/Kolom:** {row['Nomor Rak']}\n\n"
                    f"📦 **Stok:** {row['Stok Sistem']} {row['Satuan']}\n\n"
                    f"⏳ **Exp:** {row['Tgl Expire']}"
                )
            st.markdown("---")

      st.subheader(f"📋 Tabel Detail Rak {pilih_nama_rak}")
      df_tampil_styled = df_rak[[
          "Kode Barang",
          "Nama Barang",
          "No Batch",
          "Nomor Rak",
          "Tingkat Rak",
          "Stok Sistem",
          "Satuan",
          "Tgl Expire",
      ]].style.apply(warnai_manual, axis=1)
      st.dataframe(df_tampil_styled, use_container_width=True)

# ==========================================
# 3. RIWAYAT TRANSAKSI
# ==========================================
elif menu == "📜 Riwayat Transaksi":
  st.title("📜 Riwayat Barang Masuk & Keluar")
  st.markdown("Catatan aktivitas keluar masuk material beserta tanggal dan jamnya.")
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
# 4. EDIT DATA BARANG
# ==========================================
elif menu == "✏️ Edit Data Barang":
  st.title("✏️ Edit Lengkap Data, Batch & Satuan")
  st.markdown("Perbarui informasi material di gudang.")
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
          "Kode Barang / Lot", value=str(data_lama["Kode Barang"])
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
            "Incoming Date", value=def_tgl_datang
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
        df_barang.loc[idx, "Tgl Produksi"] = tgl_prod_baru.strftime("%Y-%m-%d")
        df_barang.loc[idx, "Tgl Expire"] = tgl_exp_baru.strftime("%Y-%m-%d")
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
          df_barang["Kode Barang"]
          + " - "
          + df_barang["Nama Barang"]
          + " ("
          + df_barang["Satuan"]
          + ")",
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
          df_barang["Kode Barang"]
          + " - "
          + df_barang["Nama Barang"]
          + " ("
          + df_barang["Satuan"]
          + ")",
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
            f" <br><small><b>Batch:</b> {row['No Batch']} | <b>Rak:</b>"
            f" {row['Nama Rak']}-{row['Nomor Rak']} ({row['Tingkat Rak']})"
            f" | <b>Exp:</b> {row['Tgl Expire']}</small>",
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
# 9. TAMBAH BARANG BARU
# ==========================================
elif menu == "➕ Tambah Barang Baru":
  st.title("➕ Tambah Master Material & Form Identifikasi")
  st.markdown("---")

  with st.form("form_tambah_barang"):
    kode_baru = st.text_input("Kode Barang / Lot (Contoh: NITRIC-01)")
    nama_baru = st.text_input("Material Name (Contoh: Nitric Acid)")
    batch_baru = st.text_input("Lot / Batch No (Contoh: 3924497)")
    kategori = st.text_input("Kategori Barang (Contoh: Chemical)")

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
      tgl_datang = st.date_input("Incoming Date", value=date.today())
    with col_t2:
      tgl_prod = st.date_input("Prode Date", value=date.today())
    with col_t3:
      tgl_exp = st.date_input("Exp. Date", value=date.today())

    pilihan_warna = [
        "Putih (Normal)",
        "Biru Muda (Karton/Box)",
        "Hijau Muda (Plastik)",
        "Kuning Muda (Sheet/Kertas)",
        "Merah/Pink (Aseptic)",
        "Ungu Muda",
    ]
    warna_pilih = st.selectbox("Pilih Warna Label Baris", pilihan_warna)

    nama_rak = st.text_input("Nama Rak / Area (Contoh: Rak Chemical A)")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
      nomor_rak = st.text_input("Nomor Rak / Kolom (Contoh: Rak 1)")
    with col_r2:
      tingkat_rak = st.selectbox(
          "Tingkat / Level Rak",
          ["Level 1 (Bawah)", "Level 2", "Level 3", "Level 4 (Atas)"],
      )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
      stok_awal = st.number_input("Qty (Jumlah Stok)", min_value=0, step=1)
    with col_s2:
      satuan_pilih = st.selectbox(
          "Satuan (Unit)", ["Pcs", "Kg", "Zak", "Ltr", "Box", "Drum", "Pail", "Roll"]
      )

    submit_barang = st.form_submit_button("Simpan Data Material")

    if submit_barang:
      if not kode_baru or not nama_baru:
        st.error("Kode dan Nama Material wajib diisi!")
      elif kode_baru in df_barang["Kode Barang"].values:
        st.error("Kode barang sudah terdaftar!")
      else:
        new_row = pd.DataFrame([{
            "Kode Barang": kode_baru,
            "Nama Barang": nama_baru,
            "No Batch": batch_baru if batch_baru else "-",
            "Kategori": kategori if kategori else "-",
            "Warna Label": warna_pilih,
            "Tgl Kedatangan": tgl_datang.strftime("%Y-%m-%d"),
            "Tgl Produksi": tgl_prod.strftime("%Y-%m-%d"),
            "Tgl Expire": tgl_exp.strftime("%Y-%m-%d"),
            "Nama Rak": nama_rak if nama_rak else "-",
            "Nomor Rak": nomor_rak if nomor_rak else "-",
            "Tingkat Rak": tingkat_rak,
            "Stok Sistem": stok_awal,
            "Satuan": satuan_pilih,
        }])
        df_barang = pd.concat([df_barang, new_row], ignore_index=True)
        df_barang.to_csv(DB_BARANG, index=False)
        st.success(
            f"Material `{nama_baru}` (Batch: `{batch_baru}`) berhasil disimpan"
            f" di {nama_rak}!"
        )
