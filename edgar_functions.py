import pandas as pd
import requests
from bs4 import BeautifulSoup

statement_keys_map = {
    "balance_sheet": [
        "balance sheet",
        "balance sheets",
        "statement of financial position",
        "consolidated balance sheets",
        "consolidated balance sheet",
        "consolidated financial position",
        "consolidated balance sheets - southern",
        "consolidated statements of financial position",
        "consolidated statement of financial position",
        "consolidated statements of financial condition",
        "combined and consolidated balance sheet",
        "condensed consolidated balance sheets",
        "consolidated balance sheets, as of december 31",
        "dow consolidated balance sheets",
        "consolidated balance sheets (unaudited)",
    ],
    "income_statement": [
        "income statement",
        "income statements",
        "statement of earnings (loss)",
        "statements of consolidated income",
        "consolidated statements of operations",
        "consolidated statement of operations",
        "consolidated statements of earnings",
        "consolidated statement of earnings",
        "consolidated statements of income",
        "consolidated statement of income",
        "consolidated income statements",
        "consolidated income statement",
        "condensed consolidated statements of earnings",
        "consolidated results of operations",
        "consolidated statements of income (loss)",
        "consolidated statements of income - southern",
        "consolidated statements of operations and comprehensive income",
        "consolidated statements of comprehensive income",
    ],
    "cash_flow_statement": [
        "cash flows statement",
        "cash flows statements",
        "statement of cash flows",
        "statements of consolidated cash flows",
        "consolidated statements of cash flows",
        "consolidated statement of cash flows",
        "consolidated statement of cash flow",
        "consolidated cash flows statements",
        "consolidated cash flow statements",
        "condensed consolidated statements of cash flows",
        "consolidated statements of cash flows (unaudited)",
        "consolidated statements of cash flows - southern",
    ],
}

headers = {"User-Agent": "danek1911@gmail.com"}

def cik_matching_ticker(ticker, headers=headers):
    ticker = ticker.upper().replace(".","-")
    ticker_json = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers).json()

    for company in ticker_json.values():
        if company["ticker"]==ticker:
            cik= str(company["cik_str"]).zfill(10)
            return cik
    raise ValueError(f"Ticker {ticker} not found in SEC database")

def get_submission_data_for_ticker(ticker, headers=headers, only_filings_df=False):
    cik = cik_matching_ticker(ticker)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    company_json = requests.get(url, headers=headers).json()
    if only_filings_df:
        return pd.DataFrame(company_json['filings']['recent'])
    return company_json

def get_filtered_filings(ticker, ten_k=True, ten_q=True, just_accession_numbers=False, headers=headers):
    company_filings_df = get_submission_data_for_ticker(ticker, only_filings_df=True, headers=headers)
    if ten_k:
        df = company_filings_df[company_filings_df['form'] == '10-K']
    else:
        df = company_filings_df[company_filings_df['form'] == '10-Q']
    if just_accession_numbers:
        df = df.set_index('reportDate')
        accession_df = df['accessionNumber']
        return accession_df
    else:
        return df

