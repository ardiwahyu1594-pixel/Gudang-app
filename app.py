from datetime import datetime
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

# Perbaikan otomatis jika kolom versi lama belum ada 'Nomor Rak' atau 'Tingkat Rak'
if "Nomor Rak" not in df_barang.columns:
  df_barang["Nomor Rak"] = "-"
if "Tingkat Rak" not in df_barang.columns:
  df_barang["Tingkat Rak"] = "Level 1"
df_barang.to_csv(DB_BARANG, index=False)

df_transaksi = pd.read_csv(DB_TRANSAKSI)

# Navigasi Sidebar
st.sidebar.title("📌 Menu Gudang")
menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "📊 Dashboard Stok",
        "📍 Pemetaan Rak",
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
  st.title("📊 Dashboard Stok & Lokasi Gudang")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang. Silakan tambah barang baru melalui menu.")
  else:
    total_jenis = len(df_barang)
    total_item = df_barang["Stok Sistem"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Jenis Barang", f"{total_jenis} Jenis")
    col2.metric("Total Unit dalam Stok", f"{total_item} Unit")

    st.subheader("Daftar Inventaris & Posisi Rak")
    st.dataframe(df_barang, use_container_width=True)

# ==========================================
# 2. PEMETAAN RAK (PENCARIAN LOKASI)
# ==========================================
elif menu == "📍 Pemetaan Rak":
  st.title("📍 Denah & Pemetaan Posisi Rak Barang")
  st.markdown("Cek posisi letak barang berdasarkan nomor rak dan tingkatnya.")
  st.markdown("---")

  if df_barang.empty:
    st.info("Belum ada data barang.")
  else:
    # Filter berdasarkan Nomor Rak
    daftar_rak = ["Semua Rak"] + sorted(
        df_barang["Nomor Rak"].dropna().unique().tolist()
    )
    pilih_rak = st.selectbox("Filter Berdasarkan Nomor Rak", daftar_rak)

    if pilih_rak == "Semua Rak":
      df_tampil = df_barang
    else:
      df_tampil = df_barang[df_barang["Nomor Rak"] == pilih_rak]

    st.subheader(f"Daftar Barang di {pilih_rak}")
    st.dataframe(
        df_tampil[[
            "Kode Barang",
            "Nama Barang",
            "Nomor Rak",
            "Tingkat Rak",
            "Stok Sistem",
        ]],
        use_container_width=True,
    )

# ==========================================
# 3. BARANG MASUK
# ==========================================
elif menu == "📥 Barang Masuk":
  st.title("📥 Input Barang Masuk")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Tambahkan master barang terlebih dahulu!")
  else:
    with st.form("form_barang_masuk"):
      kode_pilih = st.selectbox(
          "Pilih Barang", df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"]
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
# 4. BARANG KELUAR
# ==========================================
elif menu == "📤 Barang Keluar":
  st.title("📤 Input Barang Keluar")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang!")
  else:
    with st.form("form_barang_keluar"):
      kode_pilih = st.selectbox(
          "Pilih Barang", df_barang["Kode Barang"] + " - " + df_barang["Nama Barang"]
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

          st.success(f"Berhasil mengeluarkan {jumlah_keluar} unit {nama_barang}!")

# ==========================================
# 5. STOK OPNAME
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
            f"**{row['Nama Barang']}** (`{row['Kode Barang']}`)<br><small>Rak:"
            f" {row['Nomor Rak']} | Tingkat: {row['Tingkat Rak']}</small>",
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
      st.dataframe(df_opname, use_container_width=True)

      if st.button("💾 Sinkronkan Stok Sistem dengan Fisik Aktual"):
        for _, row in df_opname.iterrows():
          df_barang.loc[
              df_barang["Kode Barang"] == row["Kode Barang"], "Stok Sistem"
          ] = row["Stok Fisik"]
        df_barang.to_csv(DB_BARANG, index=False)
        st.success("Stok sistem berhasil disesuaikan dengan hasil opname fisik!")
        st.rerun()

# ==========================================
# 6. TAMBAH BARANG BARU
# ==========================================
elif menu == "➕ Tambah Barang Baru":
  st.title("➕ Tambah Master Barang & Posisi Rak")
  st.markdown("---")

  with st.form("form_tambah_barang"):
    kode_baru = st.text_input("Kode Barang (Contoh: BRG001)")
    nama_baru = st.text_input("Nama Barang")
    kategori = st.text_input("Kategori Barang")

    # Kolom Pemetaan Rak sesuai foto Anda
    col_r1, col_r2 = st.columns(2)
    with col_r1:
      nomor_rak = st.text_input(
          "Nomor Rak / Blok (Contoh: Rak 1, Rak 2, Rak 3)"
      )
    with col_r2:
      tingkat_rak = st.selectbox(
          "Tingkat / Level Rak",
          ["Level 1 (Bawah)", "Level 2", "Level 3", "Level 4 (Atas)"],
      )

    stok_awal = st.number_input("Stok Awal", min_value=0, step=1)
    harga = st.number_input(
        "Harga Satuan (Rp)", min_value=0.0, step=1000.0, format="%.2f"
    )

    submit_barang = st.form_submit_button("Simpan Barang & Lokasi")

    if submit_barang:
      if not kode_baru or not nama_baru:
        st.error("Kode dan Nama Barang wajib diisi!")
      elif kode_baru in df_barang["Kode Barang"].values:
        st.error("Kode barang sudah terdaftar!")
      else:
        new_row = pd.DataFrame([{
            "Kode Barang": kode_baru,
            "Nama Barang": nama_baru,
            "Kategori": kategori,
            "Nomor Rak": nomor_rak if nomor_rak else "-",
            "Tingkat Rak": tingkat_rak,
            "Stok Sistem": stok_awal,
            "Harga Satuan": harga,
        }])
        df_barang = pd.concat([df_barang, new_row], ignore_index=True)
        df_barang.to_csv(DB_BARANG, index=False)
        st.success(
            f"Barang {nama_baru} berhasil disimpan di {nomor_rak} ({tingkat_rak})!"
        )
