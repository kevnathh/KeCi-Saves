import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("rainbow:[KECI SAVES]")
st.markdown("blue:[Teman Menabung KeCi]")
st.link_button(label="Buka Spreadsheet", url="https://docs.google.com/spreadsheets/d/1iDoYhhNWSWjfGlDZVDYHYB_-e77ZEAIIP_5QOd5ra9E/edit?gid=0#gid=0")

# PW
FORM_PASSWORD = st.secrets["credentials"]["form_password"]

# GSheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch exsisting data
existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=0)
existing_data = existing_data.dropna(how="all")

# List Pengisi Form
LIST_NAMA = [
    "-",
    "Kevin",
    "Cia",
    "Kevin Cia",
    "Fee Bank"
]

FLOW = ["MASUK", "KELUAR"]

with st.form(key="Sheet1", clear_on_submit=True):
    tanggal = st.date_input(label="TANGGAL*")
    flow = st.selectbox("MASUK/KELUAR*", options=FLOW)
    difference = st.number_input(label="INPUT UANG*")
    who = st.selectbox("SIAPA?*", options=LIST_NAMA)
    notes = st.text_input(label="NOTES")
    password = st.text_input(label="PASSWORD", type="password")

    st.markdown("**wajib*")
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if not tanggal or not difference or not who or not flow:
            st.warning("Isi kolom-kolom wajib!")
            st.stop()
        elif password != FORM_PASSWORD:
            st.warning("Password salah!")
            st.stop()
        else:
            # Ambil saldo terakhir
            if not existing_data.empty:
                last_saldo = existing_data["SALDO"].iloc[-1]
            else:
                last_saldo = 0

            # Hitung saldo baru
            new_saldo = last_saldo + (difference if flow == "MASUK" else -difference)
            
            data_baru = pd.DataFrame(
                [
                    {
                        "TANGGAL": tanggal,
                        "SALDO": new_saldo,
                        "DIFFERENCE\n(INPUT)": difference if flow == "MASUK" else -difference,
                        "MASUK/KELUAR?": flow,
                        "SIAPA?": who,
                        "NOTES": notes,
                    }
                ]
            )

            updated_df = pd.concat([existing_data, data_baru], ignore_index=True)

            conn.update(worksheet="Sheet1", data=updated_df)

            st.success("Data berhasil ditambahkan!")
            st.rerun()

            # Baca ulang setelah update
            existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
            existing_data = existing_data.dropna(how="all")

# --- Setelah form ---
if not existing_data.empty:
    current_saldo = existing_data["SALDO"].iloc[-1]
else:
    current_saldo = 0

st.metric(label="💰 Saldo Sekarang", value=f"{current_saldo:,.0f}")

# --- Tampilkan data dengan editor ---
st.subheader("Data Tabungan")

edited_df = st.data_editor(
    existing_data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "SALDO": st.column_config.NumberColumn(disabled=True),   # 🔒 SALDO dikunci
    }
)

# Simpan perubahan manual ke Google Sheets
if st.button("💾 Simpan Perubahan ke Spreadsheet"):
    conn.update(worksheet="Sheet1", data=edited_df)
    st.success("Perubahan berhasil disimpan ke Google Sheets!")
    st.rerun()