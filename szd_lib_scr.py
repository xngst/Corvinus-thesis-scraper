#!/usr/bin/python
"""
Finds meta details and scrapes thesis PDFs from
http://szd.lib.uni-corvinus.hu/
"""

from datetime import datetime
from pathlib import Path
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent


def pdf_download(pdf_url: str, out_dir: Path, file_name: str) -> None:
    """Downloads a PDF thesis to the specified output directory."""
    print(f"Downloading: {pdf_url}")
    try:
        pdf_response = requests.get(pdf_url, stream=True, timeout=15)
        if pdf_response.status_code == 200:
            file_path = out_dir / file_name
            with open(file_path, "wb") as file:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    file.write(chunk)
        else:
            print(f"Failed to download PDF. Status code: {pdf_response.status_code}")
    except requests.RequestException as e:
        print(f"Network error downloading {pdf_url}: {e}")


def szd_lib_scraper(
    from_id: int,
    to_id: int,
    out_dir: str | Path,
    wait_s: int = 1,
    spoof: bool = False,
    download: bool = True,
) -> None:
    """
    Scrapes metadata and PDFs from the Corvinus thesis repository.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    header = {}
    if spoof:
        as_referer = "http://szd.lib.uni-corvinus.hu/cgi/search/advanced"
        header = {"referer": as_referer, "User-Agent": generate_user_agent()}

    response_log = {}
    collector_list = []
    base = "http://szd.lib.uni-corvinus.hu/"

    print(f"Starting scrape from ID {from_id} to {to_id}...")

    try:
        for id_code in range(from_id, to_id):
            url = f"{base}{id_code}"
            print(f"Checking: {url}")

            try:
                response = requests.get(url, headers=header, timeout=10)
                response_log[url] = dict(response.headers)

                if response.status_code != 200:
                    print(f"-> Status code: {response.status_code}")
                    continue

                # Parse HTML Metadata
                soup = BeautifulSoup(response.text, "html.parser")
                meta = soup.select("head > meta")
                meta_dict = {}

                for item in meta:
                    name = item.get("name")
                    content = item.get("content")
                    if not name or not content:
                        continue

                    if name in meta_dict:
                        if isinstance(meta_dict[name], list):
                            meta_dict[name].append(content)
                        else:
                            meta_dict[name] = [meta_dict[name], content]
                    else:
                    
                        meta_dict[name] = content

                if not meta_dict:
                    continue

                row_series = pd.Series(meta_dict)
                row_series["eprintid"] = id_code

                # Download PDFs
                if download and "eprints.document_url" in row_series:
                    pdf_url = row_series["eprints.document_url"]
                    eprint_id = row_series.get("eprints.eprintid", id_code)
                    
                    if isinstance(pdf_url, list):
                        for idx, p_url in enumerate(pdf_url, start=1):
                            file_name = f"{eprint_id}_{idx}.pdf"
                            pdf_download(p_url, out_dir, file_name)
                    else:
                        file_name = f"{eprint_id}.pdf"
                        pdf_download(pdf_url, out_dir, file_name)

                collector_list.append(row_series)

            except requests.RequestException as req_err:
                print(f"Request failed for {url}: {req_err}")

            if wait_s > 0:
                sleep(wait_s)

    finally:
        if collector_list:
            collector_df = pd.DataFrame(collector_list)
            time_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            excel_path = out_dir / f"szd_lib_info_table_{time_stamp}.xlsx"
            collector_df.to_excel(excel_path, index=False)
            print(f"Saved metadata to: {excel_path}")

        log_path = out_dir / f"request_report_{time_stamp}.txt"
        with open(log_path, "w", encoding="utf-8") as file:
            for req_url, headers in response_log.items():
                file.write(f"{req_url}: {headers}\n")
        print(f"Saved request log to: {log_path}")


if __name__ == "__main__":
    szd_lib_scraper(
        from_id=12944,
        to_id=16500,
        out_dir=Path("/home/user/Downloads"),
        wait_s=1,
        spoof=True,
        download=False,
    )
