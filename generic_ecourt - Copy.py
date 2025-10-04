# backend/scrapers/generic_ecourts.py
import requests
from bs4 import BeautifulSoup
from .base import BaseScraper
import re
from typing import Dict

class GenericECourtsScraper(BaseScraper):
    """
    Tries generic patterns. Many courts will need a custom scraper.
    """

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.headers = {"User-Agent": "CourtFetcher/1.0 (+contact)"}

    def fetch_case(self, case_type: str, case_number: str, year: str) -> Dict:
        # This is a DEMO: many courts have unique endpoints; you must add per-court logic.
        # Example approach: try ecourts public search URL patterns (if any), otherwise fallback to google "site:ecourts.gov.in case no"
        # Here we do a naive search using Google results page via requests (may be blocked/require scraping care).
        search_query = f"{case_type} {case_number} {year} site:ecourts.gov.in"
        google_search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
        r = self.session.get(google_search_url, headers=self.headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find first link — this is fragile; better to write per-court scrapers.
        first_link = None
        a = soup.select_one("a")
        if a and a.get("href"):
            href = a.get("href")
            # google wraps links — naive extract
            m = re.search(r"/url\?q=(https?://[^&]+)", href)
            if m:
                first_link = m.group(1)
            else:
                first_link = href

        parsed = {"parties": None, "filing_date": None, "next_hearing": None,
                  "status": None, "pdf_links": []}

        raw = r.text
        if not first_link:
            return {"parsed": parsed, "raw": raw, "note": "no link found via generic search"}

        # try to fetch first_link
        try:
            rr = self.session.get(first_link, headers=self.headers, timeout=20)
            page = BeautifulSoup(rr.text, "html.parser")
            text = page.get_text(separator="\n")
            # naive extractions
            # Parties: look for common labels
            def find_between(patterns):
                for p in patterns:
                    el = page.find(text=re.compile(p, re.I))
                    if el:
                        # try parent text
                        parent = el.parent
                        if parent:
                            return parent.get_text(strip=True)
                return None

            parsed["parties"] = find_between(["Petitioner", "Respondent", "Parties", "Name of Parties"])
            parsed["status"] = find_between(["Status"])
            # collect PDF links
            for link in page.find_all("a", href=True):
                href = link["href"]
                if href.lower().endswith(".pdf") or "judgment" in href.lower() or "order" in href.lower():
                    if href.startswith("/"):
                        from urllib.parse import urljoin
                        href = urljoin(first_link, href)
                    parsed["pdf_links"].append(href)
        except Exception as e:
            return {"parsed": parsed, "raw": raw, "error": str(e)}

        return {"parsed": parsed, "raw": r.text + "\n\n" + (rr.text if 'rr' in locals() else ""), "src_link": first_link}
    
    def fetch_causelist(self, date: str, court_identifier: str) -> dict:
        # For cause lists, many high courts/district courts publish daily cause lists as PDFs on their sites.
        # Approach: check known cause-list URL patterns, or search for "cause list <court> <date> site:.gov.in"
        q = f"cause list {court_identifier} {date} site:gov.in"
        google = self.session.get(f"https://www.google.com/search?q={requests.utils.quote(q)}", headers=self.headers, timeout=20)
        soup = BeautifulSoup(google.text, "html.parser")
        pdfs = []
        for a in soup.select("a"):
            href = a.get("href", "")
            import re
            m = re.search(r"/url\?q=(https?://[^&]+)", href)
            if m and m.group(1).lower().endswith(".pdf"):
                pdfs.append(m.group(1))
        return {"date": date, "court": court_identifier, "pdfs": pdfs}
