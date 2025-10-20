import streamlit as st
import pandas as pd

def sidebar_filters(df, service_col):
    st.sidebar.header("Filter Data")

    bulan_map = {
        "1": "Januari", "2": "Februari", "3": "Maret", "4": "April",
        "5": "Mei", "6": "Juni", "7": "Juli", "8": "Agustus",
        "9": "September", "10": "Oktober", "11": "November", "12": "Desember"
    }

    # Tahun Pajak
    tahun_field = "tahun_pajak" if "tahun_pajak" in df.columns else "masa_pajak_tahun" if "masa_pajak_tahun" in df.columns else None
    tahun_options = sorted(df[tahun_field].dropna().unique().tolist()) if tahun_field else ["2025"]
    selected_year = st.sidebar.selectbox("Pilih Tahun Pajak", tahun_options, index=len(tahun_options)-1)

    # Bulan
    bulan_options_display = list(bulan_map.values())
    bulan_selected_display = st.sidebar.multiselect(
        "Pilih Bulan", bulan_options_display, default=bulan_options_display
    )
    selected_month_nums = [k for k, v in bulan_map.items() if v in bulan_selected_display]

    # Company Filter
    st.sidebar.markdown("### Filter Company")
    all_companies = sorted(df["nama"].dropna().astype(str).unique().tolist())
    if "companies_selected" not in st.session_state:
        st.session_state["companies_selected"] = all_companies.copy()

    col_ca, col_uc = st.sidebar.columns(2)
    if col_ca.button("✅ Check All"):
        st.session_state["companies_selected"] = all_companies.copy()
    if col_uc.button("❌ Uncheck All"):
        st.session_state["companies_selected"] = []

    companies_selected = st.sidebar.multiselect(
        "Pilih Company", options=all_companies, key="companies_selected"
    )

    # Service Filter
    st.sidebar.markdown("### Filter Service Detail")
    all_services = sorted(df[service_col].dropna().unique().tolist())
    
    # Pastikan defaultnya check all setiap kali ganti source
    if "services_selected" not in st.session_state or st.session_state.get("reset_service", False):
        st.session_state["services_selected"] = all_services.copy()
        st.session_state["reset_service"] = False  # reset flag
    
    col_sca, col_suc = st.sidebar.columns(2)
    if col_sca.button("✅ Check All Services", key="check_all_serv"):
        st.session_state["services_selected"] = all_services.copy()
    if col_suc.button("❌ Uncheck All Services", key="uncheck_all_serv"):
        st.session_state["services_selected"] = []
    
    services_selected = st.sidebar.multiselect(
        "Pilih Service Detail",
        options=all_services,
        key="services_selected"
    )

    # Apply filters
    if companies_selected:
        df = df[df["nama"].isin(companies_selected)]
    else:
        st.warning("⚠️ Tidak ada company dipilih.")
        st.stop()

    if tahun_field:
        df = df[df[tahun_field] == selected_year]

    if services_selected:
        df = df[df[service_col].isin(services_selected)]
    else:
        st.warning("⚠️ Tidak ada service_detail dipilih.")
        st.stop()

    # Convert bulan to numeric safely
    month_cols = [m for m in selected_month_nums if m in df.columns]
    for col in month_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["filtered_total"] = df[month_cols].sum(axis=1)
    return df, bulan_map, selected_month_nums
