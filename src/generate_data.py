import math

import numpy as np
import pandas as pd


def generate_cumulative_data():
    """
    日次でリセットされる累積データを生成し、CSVファイルとして出力します。
    """
    # 1. 基本設定
    authors = [
        "Taro Yamada",
        "Hanako Sato",
        "Jiro Suzuki",
        "Yoshiko Watanabe",
    ]
    start_date = "2025-06-28 00:00:00"
    end_date = "2025-07-12 00:00:00"
    timestamps = pd.date_range(start=start_date, end=end_date, freq="h")

    # 著者ごとのその日の累積データを保持する辞書
    author_daily_stats = {author: {"steps": 0, "paid_monney": 0} for author in authors}

    all_data = []

    # 2. データ生成ループ
    for ts in timestamps:
        # --- 日付が変わったら累積データをリセット ---
        if ts.hour == 0:
            author_daily_stats = {
                author: {"steps": 0, "paid_monney": 0} for author in authors
            }

        # --- 気温 (temp) の生成 (ロジックは前回と同じ) ---
        day_progress = ts.timetuple().tm_yday
        daily_base_temp = 22 + (day_progress - 179) * 0.2
        hourly_fluctuation = 5 * math.sin((ts.hour - 9) * math.pi / 12)
        temp = round(
            daily_base_temp + hourly_fluctuation + np.random.uniform(-1.5, 1.5), 1
        )

        # 4人の著者ごとにデータを生成
        for author in authors:
            # --- stepsの計算 ---
            # 時間帯に応じて1時間あたりの歩数増加量の上限を設定
            hour = ts.hour
            if 7 <= hour <= 9:
                max_hourly_steps = 800  # 朝
            elif 10 <= hour <= 16:
                max_hourly_steps = 1000  # 日中
            elif 17 <= hour <= 21:
                max_hourly_steps = 600  # 夕方〜夜
            else:
                max_hourly_steps = 50  # 深夜

            hourly_steps_increase = np.random.randint(0, max_hourly_steps + 1)
            # 1時間前の値に加算
            current_steps = author_daily_stats[author]["steps"] + hourly_steps_increase

            # --- paid_monneyの計算 ---
            # 支出期待値(0-150)を計算
            temp_factor = max(0, temp - 24) * 3  # 気温が高いと支出増
            steps_factor = current_steps * 0.005  # たくさん歩いていると支出増

            # 時間帯による支出傾向（ランチ、ディナーなど）
            if hour in [12, 13]:
                time_factor = 40  # 昼食
            elif hour in [18, 19, 20]:
                time_factor = 60  # 夕食
            else:
                time_factor = 5

            expected_hourly_spend = np.clip(
                temp_factor + steps_factor + time_factor, 0, 150
            )

            # 期待値から±10の範囲でその時間の利用額を決定
            hourly_spend = np.random.randint(
                max(0, expected_hourly_spend - 10), expected_hourly_spend + 11
            )
            # 1時間前の値に加算
            current_paid_monney = (
                author_daily_stats[author]["paid_monney"] + hourly_spend
            )

            # --- データの記録と更新 ---
            all_data.append(
                {
                    "author": author,
                    "temp": temp,
                    "steps": current_steps,
                    "paid_monney": current_paid_monney,
                    "created_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            # 辞書の累積データを更新
            author_daily_stats[author]["steps"] = current_steps
            author_daily_stats[author]["paid_monney"] = current_paid_monney

    # 3. DataFrameに変換してCSVに出力
    df = pd.DataFrame(all_data)
    df.to_csv("dummy_activity.csv", index=False)

    print("✅ `dummy_activity.csv`の生成が完了しました。（新ロジック版）")
    print(f"Total records generated: {len(df)}")
    print("--- First 5 rows ---")
    print(df.head())
    print("\n--- A look at data around midnight (to confirm reset) ---")
    print(df[df["created_at"].str.contains("2025-06-28 23:00:00|2025-06-29 00:00:00")])


if __name__ == "__main__":
    generate_cumulative_data()
