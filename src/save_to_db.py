import sqlite3
from config import DB_PATH

def save_to_db(df, table_name):
    # DateFream을 SQLite DB에 저장
    # table_name: 지표명 기반 테이블명
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"{table_name} 테이블에 {len(df)}개 데이터 저장 완료.")