# backend/scrapers/example_highcourt.py
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper
from typing import Dict

class ExampleHighCourtScraper(BaseScraper):
    """
    Example for a hypothetical High Court site with search form accessible via GET params.
    Replace base_url and selectors per real court.
    """

    base_url = "https://example-highcourt.nic.in/search"

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.headers = {"User-Agent": "CourtFetcher/1.0"}

    def fetch_case(self, case_type: str, case_number: str, year: str) -> Dict:
        params = {"caseType": case_type, "caseNo": case_number, "year": year}
        r = self.session.get(self.base_url, params=params, headers=self.headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        parsed = {"parties": None, "filing_date": None, "next_hearing": None, "status": None, "pdf_links": []}

        # Example selectors - change as needed
        parties_el = soup.select_one(".case-parties")
        if parties_el:
            parsed["parties"] = parties_el.get_text(strip=True)

        filing = soup.find(text=lambda t: t and "Filing Date" in t)
        if filing:
            parsed["filing_date"] = filing.parent.get_text(strip=True)

        status = soup.find(class_="case-status")
        if status:
            parsed["status"] = status.get_text(strip=True)

        for a in soup.select("a"):
            href = a.get("href", "")
            if href and href.endswith(".pdf"):
                from urllib.parse import urljoin
                parsed["pdf_links"].append(urljoin(self.base_url, href))
        return {"parsed": parsed, "raw": r.text, "src": r.url}

    def fetch_causelist(self, date: str, court_identifier: str) -> dict:
        # Hypothetical URL: /causelist?date=YYYY-MM-DD
        r = self.session.get(f"https://example-highcourt.nic.in/causelist?date={date}", headers=self.headers)
        soup = BeautifulSoup(r.text, "html.parser")
        pdfs = []
        for a in soup.select("a"):
            href = a.get("href", "")
            if href.endswith(".pdf"):
                from urllib.parse import urljoin
                pdfs.append(urljoin(r.url, href))
        return {"date": date, "pdfs": pdfs}
