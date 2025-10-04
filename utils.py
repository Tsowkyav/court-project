# backend/utils.py
import os
from pathlib import Path
import requests

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, filename_hint: str = None) -> str:
    """
    Download remote file into downloads/ and return saved path.
    """
    local_name = filename_hint or url.split("/")[-1].split("?")[0]
    out_path = DOWNLOAD_DIR / local_name
    # stream
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return str(out_path)
