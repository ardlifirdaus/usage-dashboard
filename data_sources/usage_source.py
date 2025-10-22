from data_sources.base_source import BaseDataSource
from marquee_text import get_marquee_title

class UsageSource(BaseDataSource):
    def clean_data(self):
        # Tidak ada transformasi tambahan
        pass

    def get_service_column(self):
        return "service_detail"

    def get_total_column(self):
        return "total_faktur"

    def get_dashboard_titles(self):
        return {
            "main": get_marquee_title("📊 Dashboard Usage Data"),
            "pie": "Distribusi Usage per Service Detail",
            "bar": "Total Usage per Bulan",
            "top10": "Top 10 Company dengan Usage Terbanyak"
        }
