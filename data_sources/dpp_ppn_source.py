import pandas as pd
from data_sources.base_source import BaseDataSource
from marquee_text import get_marquee_title

class DppPpnSource(BaseDataSource):
    def clean_data(self):
        self.df["amount_detail"] = self.df["amount_detail"].astype(str).str.lower()
        allowed = ["dpp-keluaran", "ppn-keluaran", "dpp-masukan", "ppn-masukan"]
        self.df = self.df[self.df["amount_detail"].isin(allowed)]

        # buat kolom total dari sum bulan
        month_cols = [col for col in self.df.columns if str(col).isdigit()]
        self.df["filtered_total"] = self.df[month_cols].sum(axis=1)

    def get_service_column(self):
        return "amount_detail"

    def get_total_column(self):
        return "filtered_total"

    def get_dashboard_titles(self):
        return {
            "main": get_marquee_title("📊 Dashboard Dpp & Ppn Data"),
            "pie": "Distribusi Dpp & Ppn per Amount Detail",
            "bar": "Total Dpp & Ppn per Bulan",
            "top10": "Top 10 Company dengan Dpp & Ppn Terbanyak"
        }
