# 📈 Economic Indicators Data Pipeline

한국은행 ECOS API를 활용하여 **기준금리와 원/달러 환율**을 수집•저장•분석•시각화한 **End-to-End 데이터 파이프라인**입니다.
API 페이징 처리, 주기(M/D) 정합, 지표 필터링, DB 적재, 재현 가능한 분석 스크립트까지 한 번에 확인할 수 있습니다.

---

## 🎯 목적
- 한국은행 ECOS API로 **경제지표 자동 수집**
- **SQLite**에 적재하여 반복 분석 가능한 단일 소스 구축
- **환율(일별) → 월평균** 변환 및 **월말 기준**으로 금리와 정합
- **상관분석/단순회귀/시차(Lag)**로 1차 관계 탐색
- 결과를 **스크립트 및 이미지 아웃풋**으로 일관되게 재현

---

## 🗒️ 데이터 소스

- **기준금리**: ECOS 코드 '722Y001' (월별, 2000.01~2023.12)
- **환율(원/USD)**: ECOS 코드 '731Y001w' 중 **indicator = "원/미국달러(매매기준율)"**
    - 일별 제공 → **월평균(M)**으로 집계, 금리와 월말 타임스탬프 기준 병합

---

## 📁 디렉토리
ecoomic-indicators-pipeline/
│
├─ src/
│ ├─ fetch_data.py # ECOS API 호출(자동 분할), 스키마 정리
│ ├─ save_to_db.py # SQLite 저장
│ ├─ analysis.py # 전처리(월평균/월말 정합), 상관·회귀·시차 분석, 시각화
│ ├─ main.py # 수집 → 저장 파이프라인
│ └─ config.py # API_KEY, BASE_URL, DB_PATH
│
├─ data/
│ └─ economic.db # SQLite DB (자동 생성/갱신)
│
├─ time_series.png
├─ scatter_regression.png
├─ lag_correlation.png
└─ README.md

---

## ⚙️ 실행 방법

1) 저장소 클론
'''bash
git clone https://github.com/namho2000/economic-indicators-pipeline.git
cd economic-indicators-pipeline/src

2) 패키지 설치
'''bash
pip install -r ../requirements.txt

3) config.py 설정
'''python
API_KEY = "YOUR_ECOS_API_KEY"
BASE_URL = "https://ecos.bok.or.kr/api/StatisticSearch"
DB_PATH = "../data/economic.db"

4) 데이터 수집/삭제
'''bash
python main.py