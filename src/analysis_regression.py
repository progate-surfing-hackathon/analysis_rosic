import os

# 現在時刻をJSTで取得
from datetime import datetime
from typing import List, Tuple
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine
from type.step import StepAnalyzer
from type.weather import MeteoWeatherAPI

jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
print("JST:", jst_now)


def get_current_date() -> str:
    """現在の日付をYYYY-MM-DD形式で取得"""
    return jst_now.strftime("%Y-%m-%d")


def load_data(db_url) -> pd.DataFrame:
    """MySQLデータベースから集約済みデータを読み込む"""
    load_dotenv()
    engine = create_engine(db_url)

    query = """
    SELECT
        author,
        DATE(created_at) AS analysis_date,
        AVG(temp) AS avg_temp,
        MAX(steps) AS final_steps,
        MAX(paid_monney) AS final_paid_monney
    FROM
        activity
    GROUP BY
        author,
        analysis_date
    ORDER BY
        author,
        analysis_date
    """
    return pd.read_sql(query, engine)


def train_model(
    daily_df: pd.DataFrame,
) -> Tuple[LinearRegression, pd.DataFrame, pd.Series]:
    """重回帰モデルを学習する"""
    X = daily_df[["avg_temp", "final_steps"]]
    y = daily_df["final_paid_monney"]

    model = LinearRegression()
    model.fit(X, y)
    return model, X, y


def evaluate_model(
    model: LinearRegression, X: pd.DataFrame, y: pd.Series
) -> Tuple[np.ndarray, float, float]:
    """モデルを評価し、結果を返す"""
    coef = model.coef_
    intercept = float(model.intercept_)
    r2_score = float(model.score(X, y))
    return coef, intercept, r2_score


def predict_spending(model: LinearRegression, temp: int, steps: int) -> int:
    """新しいデータで予測を行う"""
    new_data = pd.DataFrame([[temp, steps]], columns=["avg_temp", "final_steps"])
    return int(round(model.predict(new_data)[0]))


def print_results(
    author: str, coef: np.ndarray, intercept: float, r2_score: float, prediction: int
) -> None:
    """分析結果を表示する"""
    print(f"\n{'='*50}")
    print(f"## {author} の分析結果")
    print(f"{'='*50}")
    print(f"回帰係数 (気温, 歩数): {coef}")
    print(f"切片: {intercept:.2f}")
    print(f"決定係数 (R^2): {r2_score:.3f}")
    print("回帰式:")
    print(f"飲料代 = {coef[0]:.2f} * 気温 + {coef[1]:.3f} * 歩数 + ({intercept:.2f})")
    print(f"\n予測結果 (気温30℃、歩数8000歩): {prediction}円")


def analyze_user(
    df: pd.DataFrame, author: str, predict_temp: int, predict_steps: int
) -> None:
    """ユーザーごとの分析を実行する"""
    user_df = df[df["author"] == author].copy()
    model, X, y = train_model(user_df)
    coef, intercept, r2_score = evaluate_model(model, X, y)
    prediction = predict_spending(model, predict_temp, predict_steps)
    print_results(author, coef, intercept, r2_score, prediction)


def main(db_url) -> None:
    """メイン処理"""
    df = load_data(db_url)

    # データベースからすべてのauthor名を取得
    authors: List[str] = df["author"].unique().tolist()

    for author in authors:
        # ここでモジュールをインポートして気温と歩数の予測値を計算
        # 参照のするのは
        # author:,temp:,steps:,paid_monney:,created_at:

        weather_analyzer = MeteoWeatherAPI()
        print(type(df))
        author_df = df[df["author"] == author]
        step_anlyzer = StepAnalyzer(author_df)

        temp_result = weather_analyzer.get_weather_summary("Tokyo", get_current_date())
        if temp_result:
            print(f"平均気温: {temp_result['temp_avg']:.1f}℃")
            temp: int = int(temp_result["temp_avg"])
        else:
            print("天気データの取得に失敗しました")
            continue

        # step
        result = step_anlyzer.analyze_today()

        print(f"今日の曜日: {result['day_type']}")
        print(f"過去データ数: {result['count']}件")
        print(f"平均歩数: {result['avg_steps']:,}歩")
        print(f"予測歩数: {result['predicted_steps']:,}歩")

        steps: int = result["predicted_steps"]
        analyze_user(df, author, temp, steps)


if __name__ == "__main__":
    db_url = os.environ["DB_URL"]
    main(db_url)

# データ型
# author, analysis_date, avg_temp, final_steps, final_money
