# backend/scrapers/base.py
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """
    Implementations must provide:
      - fetch_case(case_type, case_number, year) -> dict with parsed fields and pdf_links
      - fetch_causelist(date, court_identifier) -> dict/list
    """

    @abstractmethod
    def fetch_case(self, case_type: str, case_number: str, year: str) -> dict:
        pass

    @abstractmethod
    def fetch_causelist(self, date: str, court_identifier: str) -> dict:
        pass
