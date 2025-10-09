import os
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Usage", layout="wide")

# ==============================
# 🔐 Konfigurasi Login update credentials
# ==============================
credentials = {
    "usernames": {
        "pixel-guardian": {
            "name": "Pixel Guardian",
            "password": "$2b$12$DYaJpiZYUn/RCFTJnu0k.O8ELLeMqWMhRY9CBYXsQXPOkMJgjq91K"  
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
    display_name = credentials["usernames"].get(username, {}).get("name", username)
    st.sidebar.success(f"Welcome 👋 {display_name}")
    authenticator.logout("Logout", "sidebar", key="logout_btn")

    st.title("📊 Dashboard Usage Data")

    # path file Excel
    file_path = os.path.join(os.path.dirname(__file__), "usage-company.xlsx")
    if not os.path.exists(file_path):
        st.error(f"❌ File Excel tidak ditemukan di path: {file_path}")
        st.stop()

    df = pd.read_excel(file_path, sheet_name="Sheet1")

    # ==============================
    # Sidebar Filters
    # ==============================
    st.sidebar.header("Filter Data")

    bulan_map = {
        "1": "Januari", "2": "Februari", "3": "Maret", "4": "April",
        "5": "Mei", "6": "Juni", "7": "Juli", "8": "Agustus",
        "9": "September", "10": "Oktober", "11": "November", "12": "Desember"
    }

    # Tahun
    if "tahun_pajak" in df.columns:
        tahun_options = sorted(df["tahun_pajak"].dropna().unique().tolist())
    elif "masa_pajak_tahun" in df.columns:
        tahun_options = sorted(df["masa_pajak_tahun"].dropna().unique().tolist())
    else:
        tahun_options = ["2025"]

    selected_year = st.sidebar.selectbox(
        "Pilih Tahun Pajak", tahun_options, index=len(tahun_options) - 1
    )

    # Bulan
    bulan_options_display = list(bulan_map.values())
    bulan_selected_display = st.sidebar.multiselect(
        "Pilih Bulan", bulan_options_display, default=bulan_options_display
    )
    selected_month_nums = [k for k, v in bulan_map.items() if v in bulan_selected_display]

    # Company Filter
    st.sidebar.markdown("### Filter Company")
    all_companies = sorted(df["nama"].dropna().unique().tolist())
    if "companies_selected" not in st.session_state:
        st.session_state["companies_selected"] = all_companies.copy()

    col_ca, col_uc = st.sidebar.columns(2)
    if col_ca.button("✅ Check All", key="check_all_comp"):
        st.session_state["companies_selected"] = all_companies.copy()
    if col_uc.button("❌ Uncheck All", key="uncheck_all_comp"):
        st.session_state["companies_selected"] = []

    companies_selected = st.sidebar.multiselect(
        "Pilih Company", options=all_companies, key="companies_selected"
    )

    # Service Filter
    st.sidebar.markdown("### Filter Service Detail")
    all_services = sorted(df["service_detail"].dropna().unique().tolist())
    if "services_selected" not in st.session_state:
        st.session_state["services_selected"] = all_services.copy()

    col_sca, col_suc = st.sidebar.columns(2)
    if col_sca.button("✅ Check All Services", key="check_all_serv"):
        st.session_state["services_selected"] = all_services.copy()
    if col_suc.button("❌ Uncheck All Services", key="uncheck_all_serv"):
        st.session_state["services_selected"] = []

    services_selected = st.sidebar.multiselect(
        "Pilih Service Detail", options=all_services, key="services_selected"
    )

    # ==============================
    # Apply Filters
    # ==============================
    if companies_selected:
        df = df[df["nama"].isin(companies_selected)]
    else:
        st.warning("⚠️ Tidak ada company dipilih.")
        st.stop()

    if "tahun_pajak" in df.columns:
        df = df[df["tahun_pajak"] == selected_year]
    elif "masa_pajak_tahun" in df.columns:
        df = df[df["masa_pajak_tahun"] == selected_year]

    if services_selected:
        df = df[df["service_detail"].isin(services_selected)]
    else:
        st.warning("⚠️ Tidak ada service_detail dipilih.")
        st.stop()

    month_cols = [m for m in selected_month_nums if m in df.columns]
    for col in month_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["filtered_total"] = df[month_cols].sum(axis=1)

    # ==============================
    # Warna (Pelangi Cerah)
    # ==============================
    color_map = {
        "keluaran": "#FFB347",      # oranye muda
        "dalam-negri": "#FFD700",   # kuning cerah
        "masukan": "#87CEFA",       # biru langit
        "luar-negri": "#90EE90",    # hijau muda
        "self": "#DA70D6",          # ungu muda
        "vswp": "#FF69B4"           # pink cerah
    }

    service_order = ["keluaran", "masukan", "dalam-negri", "luar-negri", "self", "vswp"]

    # ==============================
    # Pie Chart
    # ==============================
    pie_data = df.groupby("service_detail")["filtered_total"].sum().reset_index().sort_values("filtered_total", ascending=False)
    st.subheader("🍩 Distribusi Usage per Service Detail")
    fig_pie = px.pie(
        pie_data,
        names="service_detail",
        values="filtered_total",
        title="Distribusi Usage per Service Detail",
        hole=0.4,
        color="service_detail",
        color_discrete_map=color_map,
        category_orders={"service_detail": service_order}
    )
    fig_pie.update_traces(textinfo="percent+label", textposition="inside", pull=[0.02]*len(pie_data))
    st.plotly_chart(
        fig_pie,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )

    # ==============================
    # Bar Chart (Stacked per service_detail)
    # ==============================
    df_melt = df.melt(id_vars=["service_detail"], value_vars=month_cols, var_name="bulan", value_name="jumlah")
    df_melt["bulan"] = df_melt["bulan"].map(bulan_map)
    bulan_order_vals = [bulan_map[k] for k in sorted(selected_month_nums, key=lambda x: int(x))]
    df_melt["bulan"] = pd.Categorical(df_melt["bulan"], categories=bulan_order_vals, ordered=True)
    usage_per_month_detail = df_melt.groupby(["bulan", "service_detail"], as_index=False, observed=False)["jumlah"].sum()

    st.subheader("📊 Total Usage per Bulan")
    fig_bar = px.bar(
        usage_per_month_detail,
        x="bulan",
        y="jumlah",
        color="service_detail",
        barmode="stack",
        title="Total Usage per Bulan",
        color_discrete_map=color_map,
        category_orders={"service_detail": service_order}
    )
    fig_bar.update_xaxes(categoryorder="array", categoryarray=bulan_order_vals)
    st.plotly_chart(
        fig_bar,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )
    
    # ==============================
    # Ringkasan Data (table)
    # ==============================
    summary = pie_data.rename(columns={"service_detail": "Service Detail", "filtered_total": "Total"})
    st.subheader("📑 Ringkasan Data")
    st.dataframe(summary.style.format({"Total": "{:,.0f}"}), width='stretch')
    
    # ==============================
    # 🏆 Top 10 Company
    # ==============================
    
    st.subheader("🏆 Top 10 Company dengan Usage Terbanyak")
    
    def map_service_detail(sd):
        s = str(sd).lower()
        if "keluar" in s:
            return "Faktur Keluaran"
        if "masuk" in s:
            return "Faktur Masukan"
        if "dalam" in s:
            return "Bupot WPDN"
        if "luar" in s:
            return "Bupot WPLN"
        if "self" in s:
            return "Bupot Self"
        if "vswp" in s:
            return "VSWP"
        return sd
    
    # Total per service_detail
    df["_amount"] = df[month_cols].sum(axis=1)
    df["_service_group"] = df["service_detail"].apply(map_service_detail)
    
    agg = df.groupby(["nama", "_service_group"], as_index=False)["_amount"].sum()
    pivot = agg.pivot_table(index="nama", columns="_service_group", values="_amount", aggfunc="sum", fill_value=0)
    
    # Pastikan semua kolom ada dan urut sesuai kebutuhan
    desired_cols = ["Faktur Keluaran", "Faktur Masukan", "Bupot WPDN", "Bupot WPLN", "Bupot Self", "VSWP"]
    for c in desired_cols:
        if c not in pivot.columns:
            pivot[c] = 0
    
    pivot["Total"] = pivot[desired_cols].sum(axis=1)
    
    # Susun ulang urutan kolom
    top10 = pivot.reset_index().rename(columns={"nama": "Nama"})
    top10 = top10[["Nama"] + desired_cols + ["Total"]].sort_values("Total", ascending=False).head(10).reset_index(drop=True)
    
    # Format kolom numerik
    for col in desired_cols + ["Total"]:
        top10[col] = pd.to_numeric(top10[col], errors="coerce").fillna(0)
    
    st.dataframe(
        top10.style.format({col: "{:,.0f}" for col in desired_cols + ["Total"]}),
        width="stretch"
    )

    # ==============================
    # Download Button
    # ==============================
    st.download_button(
        label="⬇️ Download Data Source (Excel)",
        data=open(file_path, "rb").read(),
        file_name="usage-company.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif authentication_status is False:
    st.error("❌ Username/password salah")
elif authentication_status is None:
    st.warning("⚠️ Silakan login untuk melanjutkan")
