import streamlit as st
import pandas as pd

def summary_table(df, is_dpp_ppn=False):
    """
    Menampilkan tabel ringkasan total usage / dpp-ppn per service detail atau amount detail.
    """
    # Tentukan field sesuai tipe source
    detail_col = "amount_detail" if is_dpp_ppn else "service_detail"
    total_col = "filtered_total"

    if detail_col not in df.columns:
        st.warning(f"⚠️ Kolom '{detail_col}' tidak ditemukan.")
        return

    # Grouping dan tampilkan tabel ringkasan
    summary = (
        df.groupby(detail_col)[total_col]
        .sum()
        .reset_index()
        .sort_values(total_col, ascending=False)
    )
    summary = summary.rename(columns={detail_col: "Detail", total_col: "Total"})

    st.subheader("📑 Ringkasan Data")
    st.dataframe(summary.style.format({"Total": "{:,.0f}"}), use_container_width=True)
    
def top10_table(df, total_col, title):
    st.subheader(title)

    # Pastikan kolom yang dibutuhkan ada
    if "nama" not in df.columns:
        st.warning("Kolom 'nama' tidak ditemukan pada data.")
        return

    # Hitung total per company dan per service_detail
    pivot = df.pivot_table(
        index="nama",
        columns=df.columns[df.columns.str.contains("service_detail|amount_detail")][0],
        values=total_col,
        aggfunc="sum",
        fill_value=0
    )

    # Tambahkan kolom total di akhir
    pivot["Total"] = pivot.sum(axis=1)

    # Ambil Top 10
    top10 = pivot.sort_values("Total", ascending=False).head(10).reset_index()

    # Format angka (tanpa error jika kolom string)
    numeric_cols = top10.select_dtypes(include=['number']).columns
    top10[numeric_cols] = top10[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    st.dataframe(
        top10.style.format({col: "{:,.0f}" for col in numeric_cols}),
        width='stretch'
    )