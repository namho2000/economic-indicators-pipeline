from fetch_data import fetch_data
from save_to_db import save_to_db

def main():
    # 1.지표 코드와 기간 설정 (필요하면 여기에 여러 지표 추가 가능)
    indicatorts = [
        {"code": "722Y001", "name": "interest_rate"},   #기준금리
        {"code": "731Y002", "name": "exchange_rate"}    #원/달러 환율 예시
    ]
    start_date = "202001"
    end_date = "202312"

    # 2.각 지표 수집 -> DB 저장
    for ind in indicatorts:
        # 지표에 따라 주기(cycle)를 다르게 지정
        if ind["code"] == "731Y002":
            # 원/달러 환율은 일별(D)로 조회
            df = fetch_data(ind["code"], "20200101", "20231213", cycle="D")
        else:
            # 그외 지표는 월별(M)로 조회
            df = fetch_data(ind["code"], start_date, end_date)

        save_to_db(df, ind["name"])
        
if __name__ == "__main__":
    main()