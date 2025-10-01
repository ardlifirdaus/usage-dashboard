import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Usage", layout="wide")

# ==============================
# 🔐 Konfigurasi Login
# ==============================
credentials = {
    "usernames": {
        "handsome-support": {
            "name": "Handsome Support",
            "password": "$2b$12$8LCmjipKFaOD1.PdTHHPgeYtGRRHXt1MyV/tRJpZ3PSuvHLt.p8dK"  
        }
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="streamlit_dashboard",
    key="abcdef",
    cookie_expiry_days=1
)

# ==============================
# 🔑 Login Form
# ==============================
authenticator.login(location="main", key="Login")

authentication_status = st.session_state.get("authentication_status", None)
username = st.session_state.get("username", None)

# ==============================
# Kondisi Login
# ==============================
if authentication_status:
    st.sidebar.success(f"Welcome 👋 {credentials['usernames'][username]['name']}")
    authenticator.logout("Logout", "sidebar", key="logout_btn")

    st.title("📊 Dashboard Usage Data")

    file_path = os.path.join(os.path.dirname(__file__), "usage-company.xlsx")
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, sheet_name="Sheet1")

        # ==============================
        # Filter
        # ==============================
        st.sidebar.header("Filter Data")

        # Map bulan angka ke nama Indonesia
        bulan_map = {
            "1": "Januari", "2": "Februari", "3": "Maret", "4": "April",
            "5": "Mei", "6": "Juni", "7": "Juli", "8": "Agustus",
            "9": "September", "10": "Oktober", "11": "November", "12": "Desember"
        }
        bulan_order = list(bulan_map.keys())

        # Pilih tahun (kalau ada kolom tahun_pajak)
        tahun_options = df["masa_pajak_tahun"].unique().tolist() if "masa_pajak_tahun" in df.columns else ["2025"]
        tahun = st.sidebar.selectbox("Pilih Tahun", tahun_options)

        # Pilih bulan
        bulan_selected = st.sidebar.multiselect(
            "Pilih Bulan",
            options=list(bulan_map.values()),
            default=list(bulan_map.values())
        )

        # Pilih company
        all_companies = df["nama"].unique().tolist()
        select_all = st.sidebar.checkbox("Pilih Semua Perusahaan", value=True)

        if select_all:
            companies_selected = all_companies
        else:
            companies_selected = st.sidebar.multiselect("Pilih Perusahaan", all_companies, default=[])

        # Filter data
        df = df[df["nama"].isin(companies_selected)]
        if "masa_pajak_tahun" in df.columns:
            df = df[df["masa_pajak_tahun"] == tahun]

        selected_month_nums = [k for k, v in bulan_map.items() if v in bulan_selected]
        month_cols = [m for m in df.columns if m in selected_month_nums]

        # ==============================
        # Pie Chart General Usage
        # ==============================
        df["filtered_total"] = df[month_cols].sum(axis=1)
        pie_data = df.groupby("service_detail")["filtered_total"].sum().reset_index()

        fig_pie = px.pie(
            pie_data,
            names="service_detail",
            values="filtered_total",
            title="Distribusi Usage per Service Detail"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # ==============================
        # Bar Chart (Total Usage per Bulan per Service Detail)
        # ==============================
        usage_per_month_detail = (
            df.melt(id_vars=["service_detail"], value_vars=month_cols, var_name="bulan", value_name="jumlah")
            .groupby(["bulan", "service_detail"], as_index=False)["jumlah"].sum()
        )
        usage_per_month_detail["bulan"] = usage_per_month_detail["bulan"].map(bulan_map)

        fig_bar = px.bar(
            usage_per_month_detail,
            x="bulan",
            y="jumlah",
            color="service_detail",
            barmode="stack",
            title="Total Usage per Bulan",
            text_auto=True
        )
        fig_bar.update_xaxes(categoryorder="array", categoryarray=list(bulan_map.values()))
        st.plotly_chart(fig_bar, use_container_width=True)

        # ==============================
        # Ringkasan Data
        # ==============================
        summary = (
            df.groupby("service_detail")["filtered_total"].sum().reset_index().sort_values("filtered_total", ascending=False)
        )
        st.subheader("📑 Ringkasan Data")
        st.dataframe(summary.style.format({"filtered_total": "{:,.0f}"}), use_container_width=True)

        # --------------------------
        # Top 10 Company — robust mapping & pivot
        # --------------------------
        
        # optional: show unique service_detail values for debugging
        if st.sidebar.checkbox("🔎 Tampilkan daftar service_detail unik (debug)", value=False):
            st.sidebar.write(df["service_detail"].value_counts())
        
        # mapping robust berdasarkan kata kunci
        def map_service_detail(sd):
            s = str(sd).lower()
            if any(k in s for k in ["keluar", "keluaran", "faktur keluar", "faktur-keluar"]):
                return "Faktur Keluaran"
            if any(k in s for k in ["masuk", "masukan", "faktur masuk", "faktur-masukan"]):
                return "Faktur Masukan"
            if any(k in s for k in ["dalam", "dalam-negri", "wpdn", "w.p.d.n", "wpdn"]):
                return "Bupot WPDN"
            if any(k in s for k in ["luar", "luar-negri", "wpln", "w.l.d.n", "wldn"]):
                return "Bupot WPLN"
            if "self" in s or "self payment" in s:
                return "Bupot Self"
            # fallback: jika tidak match, kembalikan original (so we can inspect)
            return sd
        
        # columns bulan yang aktif (string)
        bulan_aktif = [c for c in df.columns if str(c).isdigit()]
        
        # jika kamu pakai daftar pilihan dari sidebar, gunakan that list instead of all bulan:
        # bulan_aktif = [str(i) for i in selected_months]  # jika selected_months berisi angka string
        
        # buat kolom amount = sum bulan terpilih (sesuaikan dengan variable bulan yg kamu pakai)
        df["_amount"] = df[bulan_aktif].sum(axis=1)
        
        # buat kolom group yang sudah dinormalisasi
        df["_service_group"] = df["service_detail"].apply(map_service_detail)
        
        # aggregate dan pivot
        agg = df.groupby(["nama", "_service_group"], as_index=False)["_amount"].sum()
        pivot = agg.pivot_table(index="nama", columns="_service_group", values="_amount", aggfunc="sum", fill_value=0)
        
        # pastikan semua kolom target ada
        desired_service_cols = ["Faktur Keluaran", "Faktur Masukan", "Bupot WPDN", "Bupot WPLN", "Bupot Self"]
        for c in desired_service_cols:
            if c not in pivot.columns:
                pivot[c] = 0
        
        # total dan final top10
        pivot["Total"] = pivot[desired_service_cols].sum(axis=1)
        top10 = pivot.reset_index().rename(columns={"nama": "Nama"})
        top10 = top10[["nama"] + desired_service_cols + ["Total"]] if "nama" in top10.columns else top10
        # ensure column name 'nama' -> 'Nama'
        if "nama" in top10.columns:
            top10 = top10.rename(columns={"nama": "Nama"})
        # reindex to desired order if present
        final_cols = ["Nama"] + desired_service_cols + ["Total"]
        existing_cols = [c for c in final_cols if c in top10.columns]
        top10 = top10[existing_cols]
        
        # sort & top10
        if "Total" in top10.columns:
            top10 = top10.sort_values("Total", ascending=False).head(10).reset_index(drop=True)
        
        # format numeric columns only
        num_cols = top10.select_dtypes(include=["number"]).columns.tolist()
        fmt = {c: "{:,.0f}" for c in num_cols}
        
        st.subheader("🏆 Top 10 Company dengan Usage Terbanyak (fix)")
        st.dataframe(top10.style.format(fmt), use_container_width=True)

        # ==============================
        # Download Option
        # ==============================
        st.download_button(
            label="⬇️ Download Data Source (Excel)",
            data=open(file_path, "rb").read(),
            file_name="usage-company.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error(f"❌ File Excel tidak ditemukan di path: {file_path}")

elif authentication_status is False:
    st.error("❌ Username/password salah")
elif authentication_status is None:
    st.warning("⚠️ Silakan login untuk melanjutkan")
