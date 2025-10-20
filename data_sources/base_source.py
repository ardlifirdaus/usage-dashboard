from abc import ABC, abstractmethod
import pandas as pd

class BaseDataSource(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        self.df = pd.read_excel(self.file_path, sheet_name="Sheet1")
        self.clean_data()

    @abstractmethod
    def clean_data(self):
        """Membersihkan atau menyesuaikan struktur data sesuai source"""
        pass

    @abstractmethod
    def get_service_column(self) -> str:
        """Mengembalikan nama kolom service detail"""
        pass

    @abstractmethod
    def get_total_column(self) -> str:
        """Mengembalikan nama kolom total"""
        pass

    @abstractmethod
    def get_dashboard_titles(self) -> dict:
        """Mengembalikan judul dashboard"""
        pass
