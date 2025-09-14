import requests
import pandas as pd
from config import API_KEY, BASE_URL

def fetch_data(start_code, start_date, end_date, cycle="M"):
    # 한국은행 ECOS API에서 데이터 수집
    # start_code: 지표 코드 (예: 기준금리 722Y001, 환율 731Y002 등)
    # start_date, end_date : YYYYMM 형식
    # cycle: 주기 (M=월별, Q=분기별, A=연간)
    
    url = f"{BASE_URL}/{API_KEY}/json/kr/1/1000/{start_code}/{cycle}/{start_date}/{end_date}/?/?/?"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API 요청 실패 : {response.status_code}")
    
    data = response.json()
    rows = data.get("StatisticSearch", {}).get("row", [])
    df = pd.DataFrame(rows)

    if df.empty:
        raise Exception("데이터가 없습니다.")
    
    df = df[["TIME", "ITEM_NAME1", "DATA_VALUE"]]
    df.rename(columns={
        "TIME": "date",
        "ITEM_NAME1": "indicator",
        "DATA_VALUE": "value"
    }, inplace=True)

    date_format = "%Y%m"
    if cycle == "D":
        date_format = "%Y%m%d"
        
    df["date"] = pd.to_datetime(df["date"], format=date_format)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df
