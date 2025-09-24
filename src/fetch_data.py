import requests
import pandas as pd
from config import API_KEY, BASE_URL

def fetch_data(start_code, start_date, end_date, cycle="M", item_filter=None):
    """
    한국은행 ECOS API 데이터 수집 (자동 분할 요청)
    - start_code: 지표 코드 (예: 기준금리 722Y001, 환율 731Y001)
    - start_date, end_date: YYYYMM (M), YYYYMMDD (D)
    - cycle: M=월별, D=일별
    - item_filter: 특정 indicator 필터링 (예: "원/미국달러")
    """

    all_data = []
    step = 5000  # 한 번에 가져올 최대 row 수

    for start in range(1, 1000000, step):
        end = start + step - 1
        url = f"{BASE_URL}/{API_KEY}/json/kr/{start}/{end}/{start_code}/{cycle}/{start_date}/{end_date}/?/?/?"

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"API 요청 실패: {response.status_code}")

        data = response.json()
        rows = data.get("StatisticSearch", {}).get("row", [])
        if not rows:
            break

        all_data.extend(rows)

        total_count = data.get("StatisticSearch", {}).get("list_total_count", 0)
        if end >= total_count:
            break

    df = pd.DataFrame(all_data)
    if df.empty:
        raise Exception("데이터가 없습니다.")

    # 기본 컬럼 정리
    df = df.rename(columns={
        "TIME": "date",
        "ITEM_NAME1": "indicator",
        "DATA_VALUE": "value"
    })
    df = df[["date", "indicator", "value"]]

    # 날짜/값 변환
    date_format = "%Y%m" if cycle == "M" else "%Y%m%d"
    df["date"] = pd.to_datetime(df["date"], format=date_format, errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # ✅ 필터링 (원/미국달러(매매기준율)만 선택)
    if item_filter:
        df = df[df["indicator"].str.contains(item_filter, na=False)]

    return df
