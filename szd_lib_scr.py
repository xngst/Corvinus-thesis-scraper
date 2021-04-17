#!/usr/bin/python

"""
Finds meta details and scrape thesis pdfs from
http://szd.lib.uni-corvinus.hu/
"""

from datetime import datetime
from pathlib import Path
from time import sleep

import pandas as pd
import requests

from bs4 import BeautifulSoup
from user_agent import generate_user_agent

def pdf_download(pdf_url: str,
                 out_dir: str,
                 file_name: str) -> None:
    """
    pdf_url: url address of pdf
    out_dir: path to save thesis pdf
    file_name: 
    downloads pdf to out_dir
    returns None
    """
    print(pdf_url)
    pdf_response = requests.get(pdf_url, stream=True)
    if pdf_response.status_code == 200:
        with open(out_dir/f"{file_name}", 'wb') as file:
            file.write(pdf_response.content)
    else:
        pass
    return

def szd_lib_scraper(from_id: int,
                    to_id: int,
                    out_dir: str,
                    wait_s: int = 0,
                    spoof: bool = False,
                    download: bool = True) -> None:
    """
    from_id:    first eprintid in scraped range
    to_id:      last eprintid in scraped range
    wait_s:     wait server response time * n second, default value is 0
    spoof:      change referer to:
                'http://szd.lib.uni-corvinus.hu/cgi/search/advanced'
                and generate random user agent (module user_agent is required)
                default value is False
    out_dir:    path to save thesis pdf and request log
    download:   download thesis pdf davault value is True
                files are named based on eprints.eprintid
                example: 
                2337.pdf
                if multiple files found:
                2338_1.pdf, 2338_2.pdf
    returns None
    """

    if spoof:
        as_referer = 'http://szd.lib.uni-corvinus.hu/cgi/search/advanced'
        header = {'referer': as_referer, 'User-Agent': generate_user_agent()}
    else:
        header = {}

    response_log = {}
    out_dir = Path(out_dir)
    collector_df = pd.DataFrame()
    base = 'http://szd.lib.uni-corvinus.hu/'

    for id_code in range(from_id, to_id):
        try:
            url = (base + str(id_code))
            print(url)

        #GET
            response = requests.get(url, headers=header)
            response_log[url] = response.headers

            if response.status_code != 200:
                print(response.status_code)
                #if not ok jump to next id_code
                continue

        #GET HTML CONTENT
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            meta = soup.select('head > meta')
            meta_dict = {}
            for item in meta:
                try:
                    if item["name"] in meta_dict.keys():
                        if isinstance(meta_dict[item["name"]], list): 
                            meta_dict[item["name"]].append(item["content"])
                        else:
                            meta_dict[item["name"]] = [meta_dict[item["name"]]]
                            meta_dict[item["name"]].append(item["content"])
                    else:
                        meta_dict[item["name"]] = item["content"]
                except KeyError as e:
                    pass
            row_series = pd.Series(meta_dict)

        #DOWNLOAD PDF
            if download:
                try:
                    pdf_url = row_series['eprints.document_url']
                    doc_count = 1
                    if isinstance(pdf_url, list):
                        for url in pdf_url:
                            file_name = f"{row_series['eprints.eprintid']}_{doc_count}.pdf"
                            pdf_download(url, out_dir, file_name)
                            doc_count += 1
                    else:
                        file_name = f"{row_series['eprints.eprintid']}.pdf"
                        pdf_download(pdf_url, out_dir, file_name)
                except KeyError as ke:
                    print(ke)
                    pass
                    
            collector_df = collector_df.append(row_series.to_frame().T)

            #wait for response time * wait_s
            #response time is around 0.017079
            sleep(wait_s)

        finally:
        #SAVE REPORT with every iteration: 
            #info_table and response_log
            time_stamp = datetime.now().strftime('%Y-%m-%d')

            collector_df.reset_index(inplace=True, drop=True)
            collector_df.to_excel(out_dir/f'szd_lib_info_table_{time_stamp}.xlsx')

            with open(out_dir/f'request_report_{time_stamp}.txt', 'w') as file:
                print(response_log, file=file)
    return

if __name__ == "__main__":
    szd_lib_scraper(from_id=1,
                    to_id=13600,
                    out_dir=r".",
                    wait_s=1,
                    spoof=False,
                    download=True)
