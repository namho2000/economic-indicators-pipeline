import sqlite3
import pandas as pd
from config import DB_PATH

def get_interest_rate():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM interest_rate", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_exchange_rate_monthly():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM exchange_rate", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])

    # 월별 평균 집계
    monthly = (
        df.groupby(df["date"].dt.to_period("M"))["value"]
        .mean()
        .reset_index()
    )
    monthly["date"] = monthly["date"].dt.to_timestamp()
    monthly.rename(columns={"value": "exchange_rate"}, inplace=True)

    return monthly

def merge_data():
    interest = get_interest_rate()
    exchange = get_exchange_rate_monthly()

    # 날짜 기준으로 병합 (공통 월만 남김)
    merged = pd.merge(interest, exchange, on="date", how="inner")

    # 금리 컬럼 이름 바꿔주기
    merged.rename(columns={"value": "interest_rate"}, inplace=True)

    return merged

if __name__ == "__main__":
    merged_df = merge_data()
    print(merged_df.head())
