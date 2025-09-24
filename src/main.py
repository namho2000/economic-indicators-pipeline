from fetch_data import fetch_data
from save_to_db import save_to_db

def main():
    # 1.지표 코드와 기간 설정 (필요하면 여기에 여러 지표 추가 가능)
    indicatorts = [
        {"code": "722Y001", "name": "interest_rate"},   # 한국은행 기준금리
        {"code": "731Y001", "name": "exchange_rate"}    # 원/달러 환율
    ]
    
    # 분석 기간 (2000 ~ 2023)
    start_date_month = "200001"
    end_date_month = "202312"
    start_date_day = "20000101"
    end_date_day = "20231231"


    # 2.각 지표 수집 -> DB 저장

    for ind in indicatorts:
        if ind["code"] == "731Y001": # 환율 (일별)
            df = fetch_data(ind["code"], start_date_day, end_date_day, cycle="D", item_filter="원/미국달러")
        else: # 기준금리 (월별)
            df = fetch_data(ind["code"], start_date_month, end_date_month, cycle="M")

        save_to_db(df, ind["name"])

if __name__ == "__main__":
    main()