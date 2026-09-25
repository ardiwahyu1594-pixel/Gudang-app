from datetime import datetime, date, timedelta, timezone
import sqlite3
import pandas as pd
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Aplikasi Manajemen Gudang", page_icon="📦", layout="wide"
)

# Nama Database SQLite Permanen
DB_FILE = "gudang_permanent.db"


# Inisialisasi Database SQLite Permanen
def get_connection():
  conn = sqlite3.connect(DB_FILE, check_same_thread=False)
  return conn


def init_db():
  conn = get_connection()
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS barang (
            id_unik TEXT PRIMARY KEY,
            kode_barang TEXT,
            nama_barang TEXT,
            no_batch TEXT,
            kategori TEXT,
            warna_label TEXT,
            tgl_kedatangan TEXT,
            tgl_produksi TEXT,
            tgl_expire TEXT,
            nama_rak TEXT,
            nomor_rak TEXT,
            tingkat_rak TEXT,
            stok_sistem INTEGER,
            satuan TEXT
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            id_unik TEXT,
            kode_barang TEXT,
            nama_barang TEXT,
            tipe TEXT,
            jumlah INTEGER,
            keterangan TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


# Fungsi Load Data
def load_data_barang():
  conn = get_connection()
  df = pd.read_sql_query("SELECT * FROM barang", conn)
  conn.close()
  return df


def load_data_transaksi():
  conn = get_connection()
  df = pd.read_sql_query("SELECT * FROM transaksi", conn)
  conn.close()
  return df


df_barang = load_data_barang()
df_transaksi = load_data_transaksi()

# Penyesuaian Nama Kolom
if not df_barang.empty:
  df_barang = df_barang.rename(
      columns={
          "id_unik": "ID Unik",
          "kode_barang": "Kode Barang",
          "nama_barang": "Nama Barang",
          "no_batch": "No Batch",
          "kategori": "Kategori",
          "warna_label": "Warna Label",
          "tgl_kedatangan": "Tgl Kedatangan",
          "tgl_produksi": "Tgl Produksi",
          "tgl_expire": "Tgl Expire",
          "nama_rak": "Nama Rak",
          "nomor_rak": "Nomor Rak",
          "tingkat_rak": "Tingkat Rak",
          "stok_sistem": "Stok Sistem",
          "satuan": "Satuan",
      }
  )
else:
  df_barang = pd.DataFrame(
      columns=[
          "ID Unik",
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

if not df_transaksi.empty:
  df_transaksi = df_transaksi.rename(
      columns={
          "tanggal": "Tanggal",
          "id_unik": "ID Unik",
          "kode_barang": "Kode Barang",
          "nama_barang": "Nama Barang",
          "tipe": "Tipe",
          "jumlah": "Jumlah",
          "keterangan": "Keterangan",
      }
  )
else:
  df_transaksi = pd.DataFrame(
      columns=[
          "Tanggal",
          "ID Unik",
          "Kode Barang",
          "Nama Barang",
          "Tipe",
          "Jumlah",
          "Keterangan",
      ]
  )


def get_waktu_wib():
  tz_wib = timezone(timedelta(hours=7))
  return datetime.now(tz_wib).strftime("%Y-%m-%d %H:%M")


# Fungsi untuk memberikan warna latar belakang baris tabel yang aman
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


# Judul Utama
st.title("📦 Aplikasi Manajemen Gudang")

# Navigasi Menu di Samping (Sidebar) agar Nyaman
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "📊 Dashboard",
        "📷 Scan/Cek Rak",
        "📍 Pemetaan",
        "📥 Barang Masuk",
        "📤 Barang Keluar",
        "📜 Riwayat Transaksi",
        "✏️ Edit Data",
        "🗑️ Hapus Barang",
        "📋 Stok Opname",
        "➕ Tambah Master Baru",
    ],
)

# ==========================================
# 1. DASHBOARD STOK
# ==========================================
if menu == "📊 Dashboard":
  st.subheader("📊 Dashboard Stok & Ringkasan Material")
  st.markdown("---")

  if df_barang.empty:
    st.info(
        "Belum ada data barang. Silakan tambah barang baru melalui menu Tambah"
        " Master Baru di samping."
    )
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
          "Warna Label",
      ]
      try:
        df_ringkas_styled = df_sumber[kolom_ringkas].style.apply(
            warnai_manual, axis=1
        )
        st.dataframe(df_ringkas_styled, use_container_width=True)
      except:
        st.dataframe(df_sumber[kolom_ringkas], use_container_width=True)

      st.markdown("---")
      with st.expander("🔎 Klik di sini untuk Melihat Detail Lengkap Material"):
        opsi_detail = (
            df_sumber["ID Unik"]
            + " | "
            + df_sumber["Kode Barang"]
            + " - "
            + df_sumber["Nama Barang"]
            + " (Datang: "
            + df_sumber["Tgl Kedatangan"]
            + ")"
        )
        pilih_detail = st.selectbox(
            "Pilih Material / Palet", opsi_detail, key="pilih_detail_box"
        )

        if pilih_detail:
          id_pilih = pilih_detail.split(" | ")[0]
          row_detail = df_sumber[df_sumber["ID Unik"] == id_pilih].iloc[0]

          st.info(
              f"📦 **Nama Material:** {row_detail['Nama Barang']}\n\n"
              f"🏷️ **Kode Barang:** `{row_detail['Kode Barang']}`\n\n"
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
elif menu == "📷 Scan/Cek Rak":
  st.subheader("📷 Scan Barcode / Cek Rak Instan")
  st.markdown("---")
  gambar_kamera = st.camera_input("Ambil Foto Barcode Rak")
  if gambar_kamera:
    st.success("Barcode berhasil dipindai oleh kamera!")

  if not df_barang.empty:
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
            f"🏷️ **Kode:** `{row['Kode Barang']}` | 🔖 **Batch:**"
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
elif menu == "📍 Pemetaan":
  st.subheader("📍 Layout & Pemetaan Posisi Rak Bertingkat")
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
                    f"🏷️ **Kode:** `{row['Kode Barang']}`\n\n"
                    f"🔖 **Batch:** {row['No Batch']}\n\n"
                    f"📌 **Blok/Kolom:** {row['Nomor Rak']}\n\n"
                    f"📦 **Stok:** {row['Stok Sistem']} {row['Satuan']}**\n\n"
                    f"📥 **Datang:** {row['Tgl Kedatangan']}\n\n"
                    f"⏳ **Exp:** {row['Tgl Expire']}"
                )
            st.markdown("---")

# ==========================================
# 4. BARANG MASUK
# ==========================================
elif menu == "📥 Barang Masuk":
  st.subheader("📥 Input Barang Masuk (Palet / Kedatangan Baru)")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada master barang. Silakan tambah di menu Tambah Baru.")
  else:
    daftar_nama_master = sorted(
        df_barang["Nama Barang"].dropna().unique().tolist()
    )

    with st.form("form_barang_masuk_lengkap"):
      tipe_input_nama = st.radio(
          "Pilih Sumber Nama Material",
          ["Pilih dari Barang yang Sudah Ada", "Ketik Nama Material Baru"],
          horizontal=True,
      )

      if tipe_input_nama == "Pilih dari Barang yang Sudah Ada":
        nama_terpilih = st.selectbox(
            "Pilih Nama Material", daftar_nama_master
        )
        nama_baru = nama_terpilih
        contoh_row = df_barang[df_barang["Nama Barang"] == nama_terpilih].iloc[
            0
        ]
        kode_baru = str(contoh_row["Kode Barang"])
        default_kategori = str(contoh_row["Kategori"])
        default_satuan = str(contoh_row["Satuan"])
        default_rak = str(contoh_row["Nama Rak"])
      else:
        nama_baru = st.text_input("Nama Material Baru (Ketik manual)")
        kode_baru = st.text_input("Kode Barang Baru (Wajib Diisi)")
        default_kategori = "Packaging"
        default_satuan = "Pcs"
        default_rak = "Rak A"

      batch_baru = st.text_input("Lot / Batch No (Opsional)")
      kategori = st.text_input("Kategori Barang", value=default_kategori)

      ada_tgl_prod_masuk = st.checkbox(
          "Ada Tanggal Produksi?", value=True, key="chk_prod_masuk"
      )
      ada_tgl_exp_masuk = st.checkbox(
          "Ada Tanggal Expire?", value=True, key="chk_exp_masuk"
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
          "Nama Rak / Area", value=default_rak, key="rak_masuk"
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
        satuan_opsi = [
            "Pcs",
            "Kg",
            "Zak",
            "Ltr",
            "Box",
            "Drum",
            "Pail",
            "Roll",
        ]
        idx_satuan = (
            satuan_opsi.index(default_satuan)
            if default_satuan in satuan_opsi
            else 0
        )
        satuan_pilih = st.selectbox(
            "Satuan (Unit)", satuan_opsi, index=idx_satuan, key="satuan_masuk"
        )

      keterangan = st.text_input("Keterangan / Supplier", "Datang Palet Baru")
      submit_masuk = st.form_submit_button("Simpan Barang Masuk")

      if submit_masuk:
        if not kode_baru or not nama_baru:
          st.error("Nama Material (dan Kode jika baru) wajib diisi!")
        else:
          id_baru = f"ID-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
          final_tgl_prod = (
              tgl_prod.strftime("%Y-%m-%d") if ada_tgl_prod_masuk else "-"
          )
          final_tgl_exp = (
              tgl_exp.strftime("%Y-%m-%d") if ada_tgl_exp_masuk else "-"
          )

          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              """
                INSERT INTO barang VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
              (
                  id_baru,
                  kode_baru,
                  nama_baru,
                  batch_baru if batch_baru else "-",
                  kategori if kategori else "-",
                  warna_pilih,
                  tgl_datang.strftime("%Y-%m-%d"),
                  final_tgl_prod,
                  final_tgl_exp,
                  nama_rak if nama_rak else "-",
                  nomor_rak if nomor_rak else "-",
                  tingkat_rak,
                  stok_awal,
                  satuan_pilih,
              ),
          )
          cursor.execute(
              """
                INSERT INTO transaksi (tanggal, id_unik, kode_barang, nama_barang, tipe, jumlah, keterangan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
              (
                  get_waktu_wib(),
                  id_baru,
                  kode_baru,
                  nama_barang,
                  "MASUK",
                  stok_awal,
                  keterangan,
              ),
          )
          conn.commit()
          conn.close()

          st.session_state["pesan_sukses"] = (
              f"✅ Barang Masuk `{nama_baru}` (Qty: {stok_awal} {satuan_pilih})"
              " berhasil disimpan secara permanen!"
          )
          st.rerun()

  if "pesan_sukses" in st.session_state:
    st.success(st.session_state["pesan_sukses"])
    del st.session_state["pesan_sukses"]

# ==========================================
# 5. BARANG KELUAR
# ==========================================
elif menu == "📤 Barang Keluar":
  st.subheader("📤 Input Barang Keluar")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang!")
  else:
    with st.form("form_barang_keluar"):
      opsi_keluar = (
          df_barang["ID Unik"]
          + " | "
          + df_barang["Kode Barang"]
          + " - "
          + df_barang["Nama Barang"]
          + " (Datang: "
          + df_barang["Tgl Kedatangan"]
          + " | Stok: "
          + df_barang["Stok Sistem"].astype(str)
          + " "
          + df_barang["Satuan"]
          + ")"
      )
      pilih_keluar = st.selectbox("Pilih Barang / Palet", opsi_keluar)

      jumlah_keluar = st.number_input(
          "Jumlah Keluar", min_value=1, step=1, value=1
      )
      keterangan = st.text_input("Keterangan / Tujuan", "Pengiriman ke Produksi")
      submit = st.form_submit_button("Simpan Barang Keluar")

      if submit:
        id_pilih = pilih_keluar.split(" | ")[0]
        row_keluar = df_barang[df_barang["ID Unik"] == id_pilih].iloc[0]
        stok_sekarang = int(row_keluar["Stok Sistem"])
        nama_barang = row_keluar["Nama Barang"]
        kode_barang = row_keluar["Kode Barang"]

        if jumlah_keluar > stok_sekarang:
          st.error(
              f"Stok tidak mencukupi! Stok palet ini: {stok_sekarang} unit."
          )
        else:
          stok_baru = stok_sekarang - jumlah_keluar
          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute(
              "UPDATE barang SET stok_sistem = ? WHERE id_unik = ?",
              (stok_baru, id_pilih),
          )
          cursor.execute(
              """
                INSERT INTO transaksi (tanggal, id_unik, kode_barang, nama_barang, tipe, jumlah, keterangan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
              (
                  get_waktu_wib(),
                  id_pilih,
                  kode_barang,
                  nama_barang,
                  "KELUAR",
                  jumlah_keluar,
                  keterangan,
              ),
          )
          conn.commit()
          conn.close()

          st.session_state["pesan_sukses"] = (
              f"✅ Berhasil mengeluarkan {jumlah_keluar} unit {nama_barang}!"
          )
          st.rerun()

  if "pesan_sukses" in st.session_state:
    st.success(st.session_state["pesan_sukses"])
    del st.session_state["pesan_sukses"]

# ==========================================
# 6. RIWAYAT TRANSAKSI
# ==========================================
elif menu == "📜 Riwayat Transaksi":
  st.subheader("📜 Riwayat Barang Masuk & Keluar")
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
    kolom_tampil_trx = [
        col for col in df_trx_tampil.columns if col != "ID Unik"
    ]
    st.dataframe(
        df_trx_tampil[kolom_tampil_trx], use_container_width=True
    )

# ==========================================
# 7. EDIT DATA BARANG
# ==========================================
elif menu == "✏️ Edit Data Barang":
  st.subheader("✏️ Edit Data Barang & Lokasi")
  st.markdown("---")

  if df_barang.empty:
    st.warning("Belum ada data barang untuk diedit!")
  else:
    opsi_edit = (
        df_barang["ID Unik"]
        + " | "
        + df_barang["Kode Barang"]
        + " - "
        + df_barang["Nama Barang"]
        + " (Datang: "
        + df_barang["Tgl Kedatangan"]
        + ")"
    )
    pilih_brg = st.selectbox(
        "Pilih Barang / Palet yang Ingin Diedit", opsi_edit
    )

    id_lama = pilih_brg.split(" | ")[0]
    data_lama = df_barang.loc[df_barang["ID Unik"] == id_lama].iloc[0]

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
        final_tgl_prod_ed = (
            tgl_prod_baru.strftime("%Y-%m-%d") if ada_tgl_prod else "-"
        )
        final_tgl_exp_ed = (
            tgl_exp_baru.strftime("%Y-%m-%d") if ada_tgl_exp else "-"
        )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE barang SET kode_barang = ?, nama_barang = ?, no_batch = ?, kategori = ?, 
            warna_label = ?, tgl_kedatangan = ?, tgl_produksi = ?, tgl_expire = ?, 
            nama_rak = ?, nomor_rak = ?, tingkat_rak = ?, stok_sistem = ?, satuan = ?
            WHERE id_unik = ?
        """,
            (
                kode_baru_input,
                nama_baru_input,
                batch_baru_input if batch_baru_input else "-",
                kategori_baru_input,
                warna_baru,
                tgl_datang_baru.strftime("%Y-%m-%d"),
                final_tgl_prod_ed,
                final_tgl_exp_ed,
                nama_rak_baru,
                nomor_rak_baru,
                tingkat_baru,
                stok_baru,
                satuan_baru,
                id_lama,
            ),
        )
        conn.commit()
        conn.close()

        st.session_state["pesan_sukses"] = (
            f"✅ Data material `{nama_baru_input}` berhasil diperbarui!"
        )
        st.rerun()

  if "pesan_sukses" in st.session_state:
    st.success(st.session_state["pesan_sukses"])
    del st.session_state["pesan_sukses"]

# ==========================================
# 8. HAPUS BARANG
# ==========================================
elif menu == "🗑️ Hapus Barang":
  st.subheader("🗑️ Hapus Data Barang")
  st.markdown("---")

  if df_barang.empty:
    st.info("Tidak ada data barang untuk dihapus.")
  else:
    with st.form("form_hapus_barang"):
      opsi_hapus = (
          df_barang["ID Unik"]
          + " | "
          + df_barang["Kode Barang"]
          + " - "
          + df_barang["Nama Barang"]
          + " (Datang: "
          + df_barang["Tgl Kedatangan"]
          + ")"
      )
      pilih_hapus = st.selectbox("Pilih Barang yang Akan Dihapus", opsi_hapus)
      konfirmasi = st.checkbox("Saya yakin ingin menghapus barang ini")
      submit_hapus = st.form_submit_button("🗑️ Hapus Barang")

      if submit_hapus:
        if konfirmasi:
          id_hapus = pilih_hapus.split(" | ")[0]
          conn = get_connection()
          cursor = conn.cursor()
          cursor.execute("DELETE FROM barang WHERE id_unik = ?", (id_hapus,))
          conn.commit()
          conn.close()

          st.session_state["pesan_sukses"] = (
              "✅ Barang berhasil dihapus secara permanen!"
          )
          st.rerun()
        else:
          st.error("Silakan centang kotak konfirmasi terlebih dahulu!")

  if "pesan_sukses" in st.session_state:
    st.success(st.session_state["pesan_sukses"])
    del st.session_state["pesan_sukses"]

# ==========================================
# 9. STOK OPNAME
# ==========================================
elif menu == "📋 Stok Opname":
  st.subheader("📋 Cek Stok Opname (Audit Fisik)")
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
            f"Fisik {row['ID Unik']}",
            min_value=0,
            value=int(row["Stok Sistem"]),
            key=f"opname_{row['ID Unik']}",
            label_visibility="collapsed",
        )
      opname_data.append({
          "ID Unik": row["ID Unik"],
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
      kolom_tampil_opname = [
          col for col in df_opname.columns if col not in ["ID Unik"]
      ]
      st.dataframe(df_opname[kolom_tampil_opname], use_container_width=True)

      if st.button("💾 Sinkronkan Stok Sistem dengan Fisik Aktual"):
        conn = get_connection()
        cursor = conn.cursor()
        for _, row in df_opname.iterrows():
          cursor.execute(
              "UPDATE barang SET stok_sistem = ? WHERE id_unik = ?",
              (row["Stok Fisik"], row["ID Unik"]),
          )
        conn.commit()
        conn.close()
        st.success(
            "✅ Stok sistem berhasil disesuaikan dengan hasil opname fisik"
            " secara permanen!"
        )

# ==========================================
# 10. TAMBAH BARANG BARU (MASTER)
# ==========================================
elif menu == "➕ Tambah Master Baru":
  st.subheader("➕ Tambah Master Material Baru")
  st.markdown("---")

  with st.form("form_tambah_barang_baru"):
    kode_baru = st.text_input("Kode Barang (Boleh sama dengan material lain)")
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
      else:
        id_baru = f"ID-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        final_tgl_prod = (
            tgl_prod.strftime("%Y-%m-%d") if ada_tgl_prod_tambah else "-"
        )
        final_tgl_exp = (
            tgl_exp.strftime("%Y-%m-%d") if ada_tgl_exp_tambah else "-"
        )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO barang VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                id_baru,
                kode_baru,
                nama_baru,
                batch_baru if batch_baru else "-",
                kategori if kategori else "-",
                warna_pilih,
                tgl_datang.strftime("%Y-%m-%d"),
                final_tgl_prod,
                final_tgl_exp,
                nama_rak if nama_rak else "-",
                nomor_rak if nomor_rak else "-",
                tingkat_rak,
                stok_awal,
                satuan_pilih,
            ),
        )
        conn.commit()
        conn.close()

        st.session_state["pesan_sukses"] = (
            f"✅ Master Material `{nama_baru}` berhasil disimpan secara permanen!"
        )
        st.rerun()

  if "pesan_sukses" in st.session_state:
    st.success(st.session_state["pesan_sukses"])
    del st.session_state["pesan_sukses"]
