import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os
import yaml
from yaml.loader import SafeLoader

from data_sources.usage_source import UsageSource
from data_sources.dpp_ppn_source import DppPpnSource
from components.filters import sidebar_filters
from components.charts import pie_chart, bar_chart
from components.tables import top10_table
from utils.color_map import color_map

class DashboardApp:
    def __init__(self):
        self.df = None
        self.source = None
        self.service_col = None
        self.total_col = None
        self.bulan_map = None
        self.selected_month_nums = []
        self.titles = None

    # ==============================
    # 🔐 Login
    # ==============================
    def login(self):
        with open("credentials.yaml") as file:
            config = yaml.load(file, Loader=SafeLoader)

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        authenticator.login()

        if st.session_state["authentication_status"] is False:
            st.error("Username/password salah")
            st.stop()
        elif st.session_state["authentication_status"] is None:
            st.warning("Silakan login terlebih dahulu")
            st.stop()

        st.sidebar.success(f"👋 Selamat datang {st.session_state['name']}")

    # ==============================
    # 📂 Pilih Source Data
    # ==============================
    def select_data_source(self):
        st.sidebar.header("Pilih Source Data")
        file_option = st.sidebar.radio("Pilih tipe file:", ("Usage Data", "Dpp & Ppn Data"))

        if file_option == "Usage Data":
            self.source = UsageSource(os.path.join(os.path.dirname(__file__), "usage-company.xlsx"))
        else:
            self.source = DppPpnSource(os.path.join(os.path.dirname(__file__), "dpp-ppn-company.xlsx"))

        self.source.load_data()
        self.df = self.source.df
        self.service_col = self.source.get_service_column()
        self.total_col = self.source.get_total_column()
        self.titles = self.source.get_dashboard_titles()

        # reset filter service agar auto check all saat ganti source
        st.session_state["reset_service"] = True

    # ==============================
    # 🧭 Sidebar Filters
    # ==============================
    def apply_filters(self):
        self.df, self.bulan_map, self.selected_month_nums = sidebar_filters(
            self.df,
            self.service_col
        )

    # ==============================
    # 🍩 Pie Chart
    # ==============================
    def render_pie_chart(self):
        pie_chart(self.df, self.service_col, self.total_col, color_map, self.titles["pie"])

    # ==============================
    # 📊 Bar Chart + Ringkasan
    # ==============================
    def render_bar_chart_and_summary(self):
        # Ambil bulan yang dipilih user (interaktif)
        month_cols = [col for col in self.selected_month_nums if str(col) in self.df.columns]

        if not month_cols:
            st.warning("⚠️ Tidak ada bulan yang dipilih atau kolom bulan tidak ditemukan.")
            return

        df_melt = self.df.melt(
            id_vars=[self.service_col],
            value_vars=month_cols,
            var_name="bulan",
            value_name="jumlah"
        )

        bar_chart(df_melt, self.service_col, color_map, self.titles["bar"])

        # ==========================
        # 📑 Ringkasan Data Table
        # ==========================
        st.subheader("📑 Ringkasan Data")
        summary = (
            self.df.groupby(self.service_col)[self.total_col]
            .sum()
            .reset_index()
            .rename(columns={self.service_col: "Service Detail", self.total_col: "Total"})
        )
        st.dataframe(summary.style.format({"Total": "{:,.0f}"}), use_container_width=True)

        
    # ==============================
    # 🏆 Top 10 Table
    # ==============================
    def render_top10(self):
        top10_table(self.df, self.total_col, self.titles["top10"])

    # ==============================
    # 📥 Export Source Data
    # ==============================
    def render_export(self):
        st.sidebar.markdown("---")
        st.sidebar.subheader("📤 Export Source Data")
        with open(self.source.file_path, "rb") as f:
            st.sidebar.download_button(
                label="⬇️ Download File Source",
                data=f,
                file_name=os.path.basename(self.source.file_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # ==============================
    # 🚀 Jalankan Dashboard
    # ==============================
    def run(self):
        self.login()
        self.select_data_source()
        self.apply_filters()

        st.title(self.titles["main"])
        self.render_pie_chart()
        self.render_bar_chart_and_summary()
        self.render_top10()
        self.render_export()


if __name__ == "__main__":
    app = DashboardApp()
    app.run()
