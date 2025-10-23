# Optional import marquee (jika file ada)
try:
    from marquee_dummy import show_marquee
except ImportError:
    show_marquee = None
import os
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Pajak", layout="wide")

# ==============================
# 🔐 Konfigurasi Login
# ==============================
credentials = {
    "usernames": {
        "sylva-zoldyck": {
            "name": "Sylva Zoldyck",
            "password": "$2b$12$ZcIcgKCZJLhvnUaa7rLYrujQ/NzybLcJKZz7UG9vYfTew0aNQs1hm"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="streamlit_dashboard",
    key="abcdef",
    cookie_expiry_days=0.01  # 15 menit
)

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

    # ==============================
    # Pilih Source Data
    # ==============================
    st.sidebar.header("⚙️ Pengaturan Data")
    source_option = st.sidebar.radio(
        "Pilih Source Data",
        ["Usage Data", "Dpp & Ppn Data"],
        horizontal=True
    )

    if source_option == "Usage Data":
        file_name = "usage-company.xlsx"
        dashboard_title = "📊 Dashboard Usage Data"
    else:
        file_name = "dpp-ppn-company.xlsx"
        dashboard_title = "📊 Dashboard Dpp & Ppn Data"

    st.title(dashboard_title)
    # Tampilkan marquee hanya jika file marquee_dummy.py ada
    if show_marquee:
        show_marquee()


    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_path):
        st.error(f"❌ File Excel tidak ditemukan di path: {file_path}")
        st.stop()

    df = pd.read_excel(file_path, sheet_name="Sheet1")

    # Deteksi Mode Otomatis
    if "amount_detail" in df.columns:
        mode = "dpp_ppn"
        detail_field = "amount_detail"
        amount_field = "amount"
    else:
        mode = "usage"
        detail_field = "service_detail"
        amount_field = "service"
    
    # Reset filter jika source berubah, tapi jaga session login
    if "last_source_option" not in st.session_state or st.session_state["last_source_option"] != source_option:
        preserve_keys = ["authentication_status", "username", "name", "logout_btn"]
        preserved = {k: st.session_state[k] for k in preserve_keys if k in st.session_state}
        st.session_state.clear()
        st.session_state.update(preserved)
        # Reset filter khusus data
        st.session_state["companies_selected"] = []
        st.session_state["services_selected"] = []
    st.session_state["last_source_option"] = source_option

    # ==============================
    # Sidebar Filters
    # ==============================
    st.sidebar.header("🧾 Filter Data")

    bulan_map = {
        "1": "Januari", "2": "Februari", "3": "Maret", "4": "April",
        "5": "Mei", "6": "Juni", "7": "Juli", "8": "Agustus",
        "9": "September", "10": "Oktober", "11": "November", "12": "Desember"
    }

    # Tahun Pajak
    if "tahun_pajak" in df.columns:
        tahun_options = sorted(df["tahun_pajak"].dropna().unique().tolist())
    elif "masa_pajak_tahun" in df.columns:
        tahun_options = sorted(df["masa_pajak_tahun"].dropna().unique().tolist())
    else:
        tahun_options = ["2025"]

    selected_year = st.sidebar.selectbox(
        "Pilih Tahun Pajak", tahun_options, index=len(tahun_options) - 1
    )

    # Bulan Pajak
    bulan_options_display = list(bulan_map.values())
    bulan_selected_display = st.sidebar.multiselect(
        "Pilih Bulan", bulan_options_display, default=bulan_options_display
    )
    selected_month_nums = [k for k, v in bulan_map.items() if v in bulan_selected_display]

    # ==============================
    # Company Filter
    # ==============================
    st.sidebar.markdown("### Filter Company")
    
    all_companies = sorted(df["nama"].dropna().astype(str).unique().tolist())
    company_key = f"companies_selected_{mode}"
    
    # Auto-select all saat login baru atau switch data source
    if (
        "last_source_option" not in st.session_state
        or st.session_state["last_source_option"] != source_option
        or company_key not in st.session_state
        or not st.session_state[company_key]
    ):
        st.session_state[company_key] = all_companies.copy()
        st.session_state["last_source_option"] = source_option
    
    # Tombol Check / Uncheck
    col_ca, col_uc = st.sidebar.columns(2)
    if col_ca.button("✅ Check All", key=f"check_all_comp_{mode}"):
        st.session_state[company_key] = all_companies.copy()
    if col_uc.button("❌ Uncheck All", key=f"uncheck_all_comp_{mode}"):
        st.session_state[company_key] = []
    
    # Multiselect filter
    companies_selected = st.sidebar.multiselect(
        "Pilih Company",
        options=all_companies,
        default=st.session_state.get(company_key, all_companies),
        key=company_key,
    )
    
    # Filter data
    if companies_selected:
        df = df[df["nama"].isin(companies_selected)]
    else:
        st.warning("⚠️ Tidak ada company dipilih.")
        st.stop()

    # ==============================
    # Service / Amount Detail Filter (auto adapt)
    # ==============================
    filter_label = "Amount Detail" if mode == "dpp_ppn" else "Service Detail"
    st.sidebar.markdown(f"### Filter {filter_label}")
    
    # Ambil semua opsi unik berdasarkan kolom aktif (detail_field)
    all_services = sorted(df[detail_field].dropna().astype(str).unique().tolist())
    
    # Key unik per mode supaya tidak bentrok antar source
    service_key = f"services_selected_{mode}"
    
    # Reset pilihan jika user ganti source
    if "last_source_option" not in st.session_state or st.session_state["last_source_option"] != source_option:
        st.session_state[service_key] = all_services.copy()
        st.session_state["last_source_option"] = source_option
    
    # Tombol Check / Uncheck
    col_sca, col_suc = st.sidebar.columns(2)
    if col_sca.button("✅ Check All", key=f"check_all_{mode}"):
        st.session_state[service_key] = all_services.copy()
    if col_suc.button("❌ Uncheck All", key=f"uncheck_all_{mode}"):
        st.session_state[service_key] = []
    
    # Multiselect
    services_selected = st.sidebar.multiselect(
        f"Pilih {filter_label}",
        options=all_services,
        default=st.session_state.get(service_key, all_services),
        key=service_key
    )
    
    # Filter DataFrame
    if services_selected:
        df = df[df[detail_field].isin(services_selected)]
    else:
        st.warning(f"⚠️ Tidak ada {filter_label.lower()} dipilih.")
        st.stop()

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
        df = df[df[detail_field].isin(services_selected)]
    else:
        st.warning("⚠️ Tidak ada service_detail dipilih.")
        st.stop()

    month_cols = [m for m in selected_month_nums if m in df.columns]
    for col in month_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["filtered_total"] = df[month_cols].sum(axis=1)

    # ==============================
    # Warna & Urutan
    # ==============================
    color_map = {
        "dpp-keluaran": "#FFA07A",
        "ppn-keluaran": "#FFD700",
        "dpp-masukan": "#87CEFA",
        "ppn-masukan": "#90EE90"
    }
    default_color_map = {
        "keluaran": "#FFB347",
        "masukan": "#87CEFA",
        "dalam-negri": "#FFD700",
        "luar-negri": "#90EE90",
        "self": "#DA70D6",
        "vswp": "#FF69B4"
    }
    
    service_order = ["keluaran", "masukan", "dalam-negri", "luar-negri", "self", "vswp", "dpp-keluaran", "ppn-keluaran", "dpp-masukan", "ppn-masukan"]

    # ==============================
    # Pie Chart
    # ==============================
    chart_title = (
        "Distribusi Dpp & Ppn per Amount Detail"
        if mode == "dpp_ppn"
        else "Distribusi Usage per Service Detail"
    )

    pie_data = df.groupby(detail_field)["filtered_total"].sum().reset_index()
    st.subheader(f"🍩 {chart_title}")
    fig_pie = px.pie(
        pie_data,
        names=detail_field,
        values="filtered_total",
        hole=0.4,
        color=detail_field,
        color_discrete_map=color_map if mode == "dpp_ppn" else default_color_map,
        category_orders={detail_field: service_order}
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # ==============================
    # Bar Chart per Bulan
    # ==============================
    df_melt = df.melt(id_vars=[detail_field], value_vars=month_cols, var_name="bulan", value_name="jumlah")
    df_melt["bulan"] = df_melt["bulan"].map(bulan_map)
    bulan_order_vals = [bulan_map[k] for k in sorted(selected_month_nums, key=lambda x: int(x))]
    df_melt["bulan"] = pd.Categorical(df_melt["bulan"], categories=bulan_order_vals, ordered=True)
    usage_per_month_detail = df_melt.groupby(["bulan", detail_field], as_index=False, observed=True)["jumlah"].sum()

    st.subheader("📊 Total per Bulan")
    fig_bar = px.bar(
        usage_per_month_detail,
        x="bulan",
        y="jumlah",
        color=detail_field,
        barmode="stack",
        color_discrete_map=color_map if mode == "dpp_ppn" else default_color_map,
        category_orders={detail_field: service_order}
    )
    fig_bar.update_xaxes(categoryorder="array", categoryarray=bulan_order_vals)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ==============================
    # Ringkasan Data (Sorted Desc)
    # ==============================
    st.subheader("📑 Ringkasan Data")
    summary = (
        pie_data
        .rename(columns={detail_field: "Detail", "filtered_total": "Total"})
        .sort_values("Total", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(summary.style.format({"Total": "{:,.0f}"}), width='stretch')

    # ==============================
    # 🏆 Top 10 Company (Flexible)
    # ==============================
    
    if mode == "usage":
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
    
        df["_amount"] = df[month_cols].sum(axis=1)
        df["_service_group"] = df[detail_field].apply(map_service_detail)
    
        agg = df.groupby(["nama", "_service_group"], as_index=False)["_amount"].sum()
        pivot = agg.pivot_table(index="nama", columns="_service_group", values="_amount", aggfunc="sum", fill_value=0)
    
        desired_cols = ["Faktur Keluaran", "Faktur Masukan", "Bupot WPDN", "Bupot WPLN", "Bupot Self", "VSWP"]
        for c in desired_cols:
            if c not in pivot.columns:
                pivot[c] = 0
    
    else:
        st.subheader("🏆 Top 10 Company dengan Amount Terbanyak")
    
        def map_amount_detail(ad):
            s = str(ad).lower()
            if "dpp" in s and "keluar" in s:
                return "Dpp Keluaran"
            if "ppn" in s and "keluar" in s:
                return "Ppn Keluaran"
            if "dpp" in s and "masuk" in s:
                return "Dpp Masukan"
            if "ppn" in s and "masuk" in s:
                return "Ppn Masukan"
            return ad
    
        df["_amount"] = df[month_cols].sum(axis=1)
        df["_service_group"] = df[detail_field].apply(map_amount_detail)
    
        agg = df.groupby(["nama", "_service_group"], as_index=False)["_amount"].sum()
        pivot = agg.pivot_table(index="nama", columns="_service_group", values="_amount", aggfunc="sum", fill_value=0)
    
        desired_cols = ["Dpp Keluaran", "Ppn Keluaran", "Dpp Masukan", "Ppn Masukan"]
        for c in desired_cols:
            if c not in pivot.columns:
                pivot[c] = 0
    
    # ========== Common table render ==========
    pivot["Total"] = pivot[desired_cols].sum(axis=1)
    top10 = (
        pivot.reset_index()
        .rename(columns={"nama": "Nama"})
        .loc[:, ["Nama"] + desired_cols + ["Total"]]
        .sort_values("Total", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    
    for col in desired_cols + ["Total"]:
        top10[col] = pd.to_numeric(top10[col], errors="coerce").fillna(0)
    
    st.dataframe(
        top10.style.format({col: "{:,.0f}" for col in desired_cols + ["Total"]}),
        use_container_width=True
    )

elif authentication_status is False:
    st.error("❌ Username/password salah")
elif authentication_status is None:
    st.warning("⚠️ Silakan login untuk melanjutkan")
