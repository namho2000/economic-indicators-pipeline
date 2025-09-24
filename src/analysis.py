import sqlite3
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from scipy.stats import pearsonr, linregress
from config import DB_PATH
import platform

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = fm.FontProperties(fname=font_path).get_name()

sns.set(style="whitegrid")
matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['axes.unicode_minus'] = False

def load_and_prepare():
    conn = sqlite3.connect(DB_PATH)

    # 금리 (월별)
    interest_df = pd.read_sql("SELECT * FROM interest_rate", conn)
    interest_df['date'] = pd.to_datetime(interest_df['date'])
    if 'value' in interest_df.columns:
        interest_df = interest_df.rename(columns={'value': 'interest_rate'})
    
    # 환율 (일별 -> 월평균)
    exchange_df = pd.read_sql("SELECT * FROM exchange_rate", conn)
    exchange_df['date'] = pd.to_datetime(exchange_df['date'])
    if 'value' in exchange_df.columns:
        exchange_df = exchange_df.rename(columns={'value': 'exchange_rate'})
    
    conn.close()

    ex_monthly = (
        exchange_df
        .set_index('date')
        .resample('M')['exchange_rate']
        .mean()
        .reset_index()
    )

    interest_monthly = interest_df.copy()
    interest_monthly['date'] = interest_monthly['date'].dt.to_period('M').dt.to_timestamp('M')

    merged = pd.merge(
        interest_monthly[['date', 'interest_rate']],
        ex_monthly[['date', 'exchange_rate']],
        on='date', how='inner'
    )
    merged = merged.dropna().reset_index(drop=True)

    merged['interest_rate'] = pd.to_numeric(merged['interest_rate'], errors='coerce')
    merged['exchange_rate'] = pd.to_numeric(merged['exchange_rate'], errors='coerce')
    
    return merged

def compute_correlation(merged):
    r, p_value = pearsonr(merged['interest_rate'], merged['exchange_rate'])
    return r, p_value

def run_regression(merged):
    slope, intercept, r_value, p_value, stderr = linregress(
        merged['interest_rate'], merged['exchange_rate']
    )
    r_squared = r_value**2
    return {
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "p_value": p_value,
        "stderr": stderr,
        "r_squared": r_squared
    }

# ✅ step + line 그래프 적용
def plot_time_series(merged, save_path=None):
    fig, ax1 = plt.subplots(figsize=(12,6))

    ax1.step(merged['date'], merged['interest_rate'], where="mid", color='tab:blue', label='기준금리')
    ax1.set_xlabel('날짜')
    ax1.set_ylabel('기준금리 (%)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.plot(merged['date'], merged['exchange_rate'], color='tab:orange', label='원/달러 환율')
    ax2.set_ylabel('환율 (KRW/USD)', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    plt.title('기준금리와 원/달러 환율 추이 (월별)')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300)
    plt.show()

def plot_scatter_with_regression(merged, reg_res=None, save_path=None):
    plt.figure(figsize=(8,6))
    sns.regplot(x='interest_rate', y='exchange_rate', data=merged, ci=95, line_kws={"color":"red"})
    plt.xlabel('기준금리 (%)')
    plt.ylabel('환율 (KRW/USD)')
    if reg_res:
        text = (f"기울기 = {reg_res['slope']:.3f} (₩ per %)\n"
                f"R² = {reg_res['r_squared']:.3f}\n"
                f"p-value = {reg_res['p_value']:.3f}")
        plt.annotate(text, xy=(0.02, 0.95), xycoords='axes fraction', fontsize=10,
                     ha='left', va='top', bbox=dict(boxstyle="round", fc="w"))
        
    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

def lag_analysis(merged, max_lag=6, save_path=None):
    lags = range(-max_lag, max_lag+1)
    corrs = []
    for lag in lags:
        shifted = merged['interest_rate'].shift(lag)
        corr = merged['exchange_rate'].corr(shifted)
        corrs.append(corr)

    lag_df = pd.DataFrame({'지연(lag)': list(lags), '상관계수': corrs})

    plt.figure(figsize=(8,4))
    sns.lineplot(data=lag_df, x='지연(lag)', y='상관계수', marker='o')
    plt.axvline(0, color='k', linestyle='--')
    plt.xlabel('시차 (개월, +는 금리 선행)')
    plt.ylabel('피어슨 상관계수')
    plt.title('시차별 상관관계: 환율 vs 금리')
    plt.grid(True)
    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

    return lag_df

def main():
    merged = load_and_prepare()
    print("데이터 샘플:\n", merged.head(), "\n")
    print("총 행 개수:", len(merged))

    r, p = compute_correlation(merged)
    print(f"피어슨 상관계수 r = {r:.4f}, p-value = {p:.4f}")

    reg_res = run_regression(merged)
    print("회귀분석 결과:")
    for k, v in reg_res.items():
        print(f"    {k}: {v}")

    plot_time_series(merged, save_path="time_series.png")
    plot_scatter_with_regression(merged, reg_res=reg_res, save_path="scatter_regression.png")
    lag_df = lag_analysis(merged, max_lag=6, save_path="lag_correlation.png")

    print("\n시차별 상관계수:\n", lag_df.to_string(index=False))

if __name__ == "__main__":
    main()
