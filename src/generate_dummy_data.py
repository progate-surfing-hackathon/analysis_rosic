import csv
import random
from datetime import datetime, timedelta

from type.step import DayType


def generate_dummy_step_data(sample_count: int = 1200):
    """step.py用のダミーデータを生成"""

    # 曜日ごとの歩数範囲設定
    step_ranges = {
        DayType.MONDAY.value: (8000, 12000),
        DayType.TUESDAY.value: (7500, 11500),
        DayType.WEDNESDAY.value: (7000, 10000),
        DayType.THURSDAY.value: (7500, 11000),
        DayType.FRIDAY.value: (6000, 9000),
        DayType.SATURDAY.value: (10000, 15000),
        DayType.SUNDAY.value: (5000, 8000),
        DayType.HOLIDAY.value: (4000, 7000),
    }

    step_day_type = {day: [] for day in step_ranges.keys()}

    # ダミーデータ生成
    start_date = datetime.now() - timedelta(days=sample_count)

    for i in range(sample_count):
        current_date = start_date + timedelta(days=i)
        weekday = current_date.weekday()

        # 曜日判定
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_type = day_names[weekday]

        # 祝日判定（10%の確率）
        if random.random() < 0.1:
            day_type = "holiday"

        # 歩数とお金の生成
        min_steps, max_steps = step_ranges[day_type]
        steps = random.randint(min_steps, max_steps)
        paid_money = random.randint(0, 500) if steps > 8000 else random.randint(0, 200)

        data_entry = {
            "template": random.randint(20, 30),
            "steps": steps,
            "paid_money": paid_money,
            "create_at": int(current_date.timestamp()),
        }

        step_day_type[day_type].append(data_entry)

    return step_day_type


def print_dummy_data(data, max_display=3):
    """生成されたダミーデータを表示"""
    print("step_day_type = {")
    for day, entries in data.items():
        print(f'    "{day}": [')
        display_count = min(len(entries), max_display)
        for i in range(display_count):
            entry = entries[i]
            print(f"        {entry},")
        if len(entries) > max_display:
            print(f"        # ... 他{len(entries) - max_display}件")
        print("    ],")
    print("}")


def save_to_csv(data, filename="dammy_step_data.csv"):
    """ダミーデータをCSVファイルに保存"""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["day_type", "template", "steps", "paid_money", "create_at", "date"]
        )

        for day_type, entries in data.items():
            for entry in entries:
                date_str = datetime.fromtimestamp(entry["create_at"]).strftime(
                    "%Y-%m-%d"
                )
                writer.writerow(
                    [
                        day_type,
                        entry["template"],
                        entry["steps"],
                        entry["paid_money"],
                        entry["create_at"],
                        date_str,
                    ]
                )


if __name__ == "__main__":
    # サンプル数を選択
    sample_count = int(input("サンプル数を入力してください (デフォルト: 100): ") or 100)

    # ダミーデータ生成
    dummy_data = generate_dummy_step_data(sample_count)

    # CSVファイルに保存
    save_to_csv(dummy_data)
    print(f"\n=== dammy_step_data.csvに保存しました ===")

    # 結果表示
    print(f"\n=== {sample_count}件のダミーデータを生成しました ===")
    print_dummy_data(dummy_data)

    # 統計情報
    print("\n=== 統計情報 ===")
    for day, entries in dummy_data.items():
        if entries:
            avg_steps = sum(e["steps"] for e in entries) / len(entries)
            print(f"{day}: {len(entries)}件, 平均歩数: {avg_steps:.0f}歩")
