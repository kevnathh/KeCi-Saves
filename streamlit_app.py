import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- Fungsi untuk hitung saldo ulang ---
def hitung_saldo(df: pd.DataFrame) -> pd.DataFrame:
    saldo = 0
    new_saldos = []
    for diff in df["DIFFERENCE\n(INPUT)"]:
        saldo += diff
        new_saldos.append(saldo)
    df["SALDO"] = new_saldos
    return df

# --- Tampilan utama ---
st.title("🌈 KECI SAVES")
st.markdown("💙 Teman Menabung KeCi")
st.link_button(
    label="Buka Spreadsheet",
    url="https://docs.google.com/spreadsheets/d/1iDoYhhNWSWjfGlDZVDYHYB_-e77ZEAIIP_5QOd5ra9E/edit?gid=0#gid=0"
)

# --- Password dari secrets ---
FORM_PASSWORD = st.secrets["credentials"]["form_password"]

# --- GSheets Connection ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Fetch data awal ---
existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=0)
existing_data = existing_data.dropna(how="all")

# --- List pilihan ---
LIST_NAMA = ["-", "Kevin", "Cia", "Kevin Cia", "Fee Bank"]
FLOW = ["MASUK", "KELUAR"]

# --- Form input data ---
with st.form(key="Sheet1", clear_on_submit=True):
    tanggal = st.date_input(label="TANGGAL*")
    flow = st.selectbox("MASUK/KELUAR*", options=FLOW)
    difference = st.number_input(label="INPUT UANG*")
    who = st.selectbox("SIAPA?*", options=LIST_NAMA)
    notes = st.text_input(label="NOTES")
    password = st.text_input(label="PASSWORD", type="password")

    st.markdown("**Kolom dengan * wajib diisi**")
    submit_button = st.form_submit_button(label="💾 Submit", type="primary")

    if submit_button:
        if not tanggal or not difference or not who or not flow:
            st.warning("Isi kolom-kolom wajib!")
            st.stop()
        elif password != FORM_PASSWORD:
            st.warning("Password salah!")
            st.stop()
        else:
            # Buat data baru
            data_baru = pd.DataFrame(
                [
                    {
                        "TANGGAL": tanggal,
                        "DIFFERENCE\n(INPUT)": difference if flow == "MASUK" else -difference,
                        "MASUK/KELUAR?": flow,
                        "SIAPA?": who,
                        "NOTES": notes,
                    }
                ]
            )

            # Gabungkan lalu hitung ulang saldo
            updated_df = pd.concat([existing_data, data_baru], ignore_index=True)
            updated_df = hitung_saldo(updated_df)

            # Simpan ke Google Sheets
            conn.update(worksheet="Sheet1", data=updated_df)

            st.success("Data berhasil ditambahkan!")
            st.rerun()

# --- Setelah form: tampilkan saldo terakhir ---
if not existing_data.empty:
    existing_data = hitung_saldo(existing_data)  # pastikan saldo selalu terupdate
    current_saldo = existing_data["SALDO"].iloc[-1]
else:
    current_saldo = 0

st.metric(label="💰 Saldo Sekarang", value=f"{current_saldo:,.0f}")

# --- Data Editor ---
st.subheader("Data Tabungan")

edited_df = st.data_editor(
    existing_data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "SALDO": st.column_config.NumberColumn(disabled=True),   # 🔒 SALDO tidak bisa diubah manual
    }
)

# --- Simpan perubahan manual ---
update_pass = st.text_input("Password Update Data", type="password")

if st.button("💾 Simpan Perubahan ke Spreadsheet", type="primary"):
    if update_pass != FORM_PASSWORD:
        st.error("Password salah untuk update data!")
    else:
        edited_df = hitung_saldo(edited_df)  # hitung ulang saldo sebelum simpan
        conn.update(worksheet="Sheet1", data=edited_df)
        st.success("Perubahan berhasil disimpan ke Google Sheets!")
        st.rerun()