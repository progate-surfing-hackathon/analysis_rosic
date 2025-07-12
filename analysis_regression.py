import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def load_data(filename):
    """データセットを読み込み、日付を変換する"""
    df = pd.read_csv(filename)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["date"] = df["created_at"].dt.date
    return df


def aggregate_daily_data(user_df):
    """毎時データを日ごとのデータに集約する"""
    return user_df.groupby('date').agg({
        'temp': 'mean',
        'steps': 'last',
        'paid_monney': 'last'
    }).reset_index()


def train_model(daily_df):
    """重回帰モデルを学習する"""
    X = daily_df[["temp", "steps"]]
    y = daily_df["paid_monney"]
    
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
    new_data = pd.DataFrame([[temp, steps]], columns=["temp", "steps"])
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


def analyze_user(df, author):
    """ユーザーごとの分析を実行する"""
    user_df = df[df['author'] == author].copy()
    daily_df = aggregate_daily_data(user_df)
    model, X, y = train_model(daily_df)
    coef, intercept, r2_score = evaluate_model(model, X, y)
    prediction = predict_spending(model, 30, 8000)
    print_results(author, coef, intercept, r2_score, prediction)


def main():
    """メイン処理"""
    df = load_data("dummy_activity.csv")
    
    # データベースからすべてのauthor名を取得
    authors = df['author'].unique()
    
    for author in authors:
        analyze_user(df, author)


if __name__ == "__main__":
    main()
