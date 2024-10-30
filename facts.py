import pandas as pd
import requests
import edgar_functions as edgar
import os

headers = {"User-Agent": "danek1911@gmail.com"}

def get_facts(ticker, headers=headers):
    cik= edgar.cik_matching_ticker(ticker)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    company_facts = requests.get(url,headers=headers).json()
    return company_facts

def facts_DF(ticker, headers=headers):
    facts = get_facts(ticker, headers)
    us_gaap_data = facts["facts"]["us-gaap"]
    df_data = []
    for fact, details in us_gaap_data.items():
        for unit in details["units"]:
            for item in details["units"][unit]:
                row = item.copy()
                row["fact"] = fact
                df_data.append(row)

    df = pd.DataFrame(df_data)
    df["end"] = pd.to_datetime(df["end"])
    df["start"] = pd.to_datetime(df["start"])
    df = df.drop_duplicates(subset=["fact","end","val"])
    df.set_index("end", inplace=True)
    labels_dict = {fact: details["label"] for fact, details in us_gaap_data.items()}
    return df, labels_dict

def annual_facts(ticker,headers=headers):
    accession_nums = edgar.get_filtered_filings(ticker,ten_k=True,just_accession_numbers=True)
    accession_nums.index = pd.to_datetime(accession_nums.index, errors='coerce')
    df, label_dict = facts_DF(ticker, headers)
    ten_k = df[df["accn"].isin(accession_nums)]
    ten_k = ten_k[ten_k.index.isin(accession_nums.index)]
    pivot = ten_k.pivot_table(values="val",columns="fact",index="end")
    pivot.rename(columns=label_dict, inplace=True)
    return pivot.T

def quarterly_facts(ticker, headers=headers):
    accession_nums = edgar.get_filtered_filings(ticker, ten_k=False, just_accession_numbers=True)
    df, label_dict = facts_DF(ticker, headers)
    ten_q = df[df["accn"].isin(accession_nums)]
    ten_q = ten_q[ten_q.index.isin(accession_nums.index)].reset_index(drop=False)
    ten_q = ten_q.drop_duplicates(subset=["fact", "end"], keep="last")
    pivot = ten_q.pivot_table(values="val", columns="fact", index="end")
    pivot.rename(columns=label_dict, inplace=True)
    return pivot.T

def save_dataframe_to_csv(dataframe, folder_name, ticker, statement_name, frequency):
    directory_path = os.path.join(folder_name, ticker)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, f"{statement_name}_{frequency}.csv")
    dataframe.to_csv(file_path)
    return None

#annual_facts = annual_facts("SPRY")
#annual_facts.to_csv('C:/Users/danek/OneDrive/Desktop/ABC.csv')

quarterly_facts = quarterly_facts("SPRY")
save_dataframe_to_csv(quarterly_facts, folder_name="EdgarFiles", ticker="SPRY", frequency=1, statement_name="10-K")
quarterly_facts.to_csv('C:/Users/danek/OneDrive/Desktop/SPRYDataTest.csv')


