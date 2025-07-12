import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine


def load_data():
    """MySQLデータベースから集約済みデータを読み込む"""
    load_dotenv()
    db_url = os.environ["DB_URL"]
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


def train_model(daily_df):
    """重回帰モデルを学習する"""
    X = daily_df[["avg_temp", "final_steps"]]
    y = daily_df["final_paid_monney"]

    model = LinearRegression()
    model.fit(X, y)
    return model, X, y


def evaluate_model(model, X, y):
    """モデルを評価し、結果を返す"""
    coef = model.coef_
    intercept = model.intercept_
    r2_score = model.score(X, y)
    return coef, intercept, r2_score


def predict_spending(model, temp, steps):
    """新しいデータで予測を行う"""
    new_data = pd.DataFrame([[temp, steps]], columns=["avg_temp", "final_steps"])
    return int(round(model.predict(new_data)[0]))


def print_results(author, coef, intercept, r2_score, prediction):
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


def analyze_user(df, author, predict_temp, predict_steps):
    """ユーザーごとの分析を実行する"""
    user_df = df[df["author"] == author].copy()
    model, X, y = train_model(user_df)
    coef, intercept, r2_score = evaluate_model(model, X, y)
    prediction = predict_spending(model, predict_temp, predict_steps)
    print_results(author, coef, intercept, r2_score, prediction)


def main():
    """メイン処理"""
    df = load_data()

    # データベースからすべてのauthor名を取得
    authors = df["author"].unique()

    for author in authors:
        # ここでモジュールをインポートして気温と歩数の予測値を計算
        # マジックナンバーのところに代入
        analyze_user(df, author, 30, 8000)


if __name__ == "__main__":
    main()

# データ型
# author, analysis_date, avg_temp, final_steps, final_money
