import os
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Usage", layout="wide")

# ==============================
# 🔐 Konfigurasi Login (sesuaikan dengan versi streamlit-authenticator di environment)
# ==============================
credentials = {
    "usernames": {
        "handsome-support": {
            "name": "Handsome Support",
            "password": "$2b$12$8LCmjipKFaOD1.PdTHHPgeYtGRRHXt1MyV/tRJpZ3PSuvHLt.p8dK"  # hash 'ter1makas1h-4rdl1'
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

    # portable file path (expects usage-company.xlsx in same repo)
    file_path = os.path.join(os.path.dirname(__file__), "usage-company.xlsx")
    if not os.path.exists(file_path):
        st.error(f"❌ File Excel tidak ditemukan di path: {file_path}")
        st.stop()

    df = pd.read_excel(file_path, sheet_name="Sheet1")

    # ==============================
    # Sidebar Filters: Tahun, Bulan, Company, Service Detail
    # ==============================
    st.sidebar.header("Filter Data")

    # bulan mapping
    bulan_map = {
        "1": "Januari", "2": "Februari", "3": "Maret", "4": "April",
        "5": "Mei", "6": "Juni", "7": "Juli", "8": "Agustus",
        "9": "September", "10": "Oktober", "11": "November", "12": "Desember"
    }

    # tahun (fallback ke '2025' jika tidak ada kolom)
    if "masa_pajak_tahun" in df.columns:
        tahun_options = sorted(df["masa_pajak_tahun"].dropna().unique().tolist())
    else:
        tahun_options = ["2025"]
    selected_year = st.sidebar.selectbox("Pilih Tahun", tahun_options, index=len(tahun_options)-1)

    # bulan pilihan (display nama)
    bulan_options_display = list(bulan_map.values())
    bulan_selected_display = st.sidebar.multiselect("Pilih Bulan", bulan_options_display, default=bulan_options_display)
    # map back to numbers as strings
    selected_month_nums = [k for k, v in bulan_map.items() if v in bulan_selected_display]

    # company filter with Check All / Uncheck All + search
    st.sidebar.markdown("### Filter Company")
    all_companies = sorted(df["nama"].dropna().unique().tolist())
    search_company = st.sidebar.text_input("Cari Company (ketik sebagian nama, lalu tekan Enter)").strip().lower()
    if search_company:
        company_options = [c for c in all_companies if search_company in c.lower()]
    else:
        company_options = all_companies

    # persistent selection via session_state
    if "companies_selected" not in st.session_state:
        st.session_state.companies_selected = company_options

    col_ca, col_uc = st.sidebar.columns(2)
    with col_ca:
        if st.button("✅ Check All", key="check_all_comp"):
            st.session_state.companies_selected = company_options
    with col_uc:
        if st.button("❌ Uncheck All", key="uncheck_all_comp"):
            st.session_state.companies_selected = []

    companies_selected = st.sidebar.multiselect(
        "Pilih Company",
        options=company_options,
        default=st.session_state.companies_selected,
        key="company_multiselect"
    )
    # store latest selection
    st.session_state.companies_selected = companies_selected

    # service_detail filter with Check All / Uncheck All
    st.sidebar.markdown("### Filter Service Detail")
    all_services = sorted(df["service_detail"].dropna().unique().tolist())
    if "services_selected" not in st.session_state:
        st.session_state.services_selected = all_services

    col_sca, col_suc = st.sidebar.columns(2)
    with col_sca:
        if st.button("✅ Check All Services", key="check_all_serv"):
            st.session_state.services_selected = all_services
    with col_suc:
        if st.button("❌ Uncheck All Services", key="uncheck_all_serv"):
            st.session_state.services_selected = []

    services_selected = st.sidebar.multiselect(
        "Pilih Service Detail",
        options=all_services,
        default=st.session_state.services_selected,
        key="service_multiselect"
    )
    st.session_state.services_selected = services_selected

    # ==============================
    # Apply filters to df (order: company -> year -> service -> months)
    # ==============================
    # companies
    if companies_selected:
        df = df[df["nama"].isin(companies_selected)]
    else:
        st.warning("⚠️ Tidak ada company dipilih. Pilih minimal 1 company.")
        st.stop()

    # year
    if "masa_pajak_tahun" in df.columns:
        df = df[df["masa_pajak_tahun"] == selected_year]

    # services
    if services_selected:
        df = df[df["service_detail"].isin(services_selected)]
    else:
        st.warning("⚠️ Tidak ada service_detail dipilih. Pilih minimal 1 service.")
        st.stop()

    # months -> determine month_cols (string names in df)
    month_cols = [m for m in selected_month_nums if m in df.columns]
    if not month_cols:
        st.warning("⚠️ Tidak ada kolom bulan yang cocok di file untuk pilihan bulan tersebut.")
        st.stop()

    # ensure month columns numeric
    for col in month_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # compute per-row filtered total (based on selected months)
    df["filtered_total"] = df[month_cols].sum(axis=1)

    # ==============================
    # Pie Chart -> ring (hole)
    # ==============================
    pie_data = df.groupby("service_detail")["filtered_total"].sum().reset_index().sort_values("filtered_total", ascending=False)
    st.subheader("🍩 Distribusi Usage per Service Detail")
    fig_pie = px.pie(
        pie_data,
        names="service_detail",
        values="filtered_total",
        title="Distribusi Usage per Service Detail",
        hole=0.4  # ring
    )
    # show percentages and labels nicely
    fig_pie.update_traces(textinfo="percent+label", textposition="inside", pull=[0.02]*len(pie_data))
    st.plotly_chart(fig_pie, use_container_width=True)

    # ==============================
    # Bar Chart (stacked per service_detail)
    # ==============================
    # melt using only month_cols
    df_melt = df.melt(id_vars=["service_detail"], value_vars=month_cols, var_name="bulan", value_name="jumlah")
    df_melt["bulan"] = df_melt["bulan"].map(bulan_map)
    # ensure ordering
    bulan_order_vals = [bulan_map[k] for k in sorted(selected_month_nums, key=lambda x: int(x))]
    df_melt["bulan"] = pd.Categorical(df_melt["bulan"], categories=bulan_order_vals, ordered=True)
    usage_per_month_detail = df_melt.groupby(["bulan", "service_detail"], as_index=False)["jumlah"].sum()

    st.subheader("📊 Total Usage per Bulan")
    fig_bar = px.bar(
        usage_per_month_detail,
        x="bulan",
        y="jumlah",
        color="service_detail",
        barmode="stack",
        title="Total Usage per Bulan",
    )
    fig_bar.update_xaxes(categoryorder="array", categoryarray=bulan_order_vals)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ==============================
    # Ringkasan Data (table)
    # ==============================
    summary = pie_data.rename(columns={"service_detail": "Service Detail", "filtered_total": "Total"})
    st.subheader("📑 Ringkasan Data")
    st.dataframe(summary.style.format({"Total": "{:,.0f}"}), use_container_width=True)

    # --------------------------
    # Top 10 Company — robust mapping & pivot (uses selected months)
    # --------------------------
    # robust mapping (same as before)
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
        return sd

    # compute _amount using selected month_cols
    df["_amount"] = df[month_cols].sum(axis=1)
    df["_service_group"] = df["service_detail"].apply(map_service_detail)

    agg = df.groupby(["nama", "_service_group"], as_index=False)["_amount"].sum()
    pivot = agg.pivot_table(index="nama", columns="_service_group", values="_amount", aggfunc="sum", fill_value=0)

    desired_service_cols = ["Faktur Keluaran", "Faktur Masukan", "Bupot WPDN", "Bupot WPLN", "Bupot Self"]
    for c in desired_service_cols:
        if c not in pivot.columns:
            pivot[c] = 0

    pivot["Total"] = pivot[desired_service_cols].sum(axis=1)
    top10 = pivot.reset_index().rename(columns={"nama": "Nama"})

    # reorder and keep only desired columns present
    final_cols = ["Nama"] + desired_service_cols + ["Total"]
    existing_cols = [c for c in final_cols if c in top10.columns]
    top10 = top10[existing_cols]
    if "Total" in top10.columns:
        top10 = top10.sort_values("Total", ascending=False).head(10).reset_index(drop=True)

    num_cols = top10.select_dtypes(include=["number"]).columns.tolist()
    fmt = {c: "{:,.0f}" for c in num_cols}

    st.subheader("🏆 Top 10 Company dengan Usage Terbanyak")
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

elif authentication_status is False:
    st.error("❌ Username/password salah")
elif authentication_status is None:
    st.warning("⚠️ Silakan login untuk melanjutkan")
