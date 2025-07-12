from datetime import datetime, timedelta
from typing import Dict, List, Optional
import csv
import numpy as np
from enum import Enum
import pandas as pd

class DayType(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    HOLIDAY = "holiday"

class WeekdayStepAnalyzer:
    def __init__(self):
        # 曜日ごとの基本重み（デフォルト値）
        self.day_weights = {
            DayType.MONDAY: 1.2,     # 月曜日は活動的
            DayType.TUESDAY: 1.1,    # 火曜日は普通より少し多め
            DayType.WEDNESDAY: 1.0,  # 水曜日は標準
            DayType.THURSDAY: 1.1,   # 木曜日は普通より少し多め
            DayType.FRIDAY: 0.9,     # 金曜日は少し少なめ
            DayType.SATURDAY: 1.3,   # 土曜日は活動的
            DayType.SUNDAY: 0.8,     # 日曜日は休息日
            DayType.HOLIDAY: 0.7     # 祝日は最も少ない
        }
        
        # 曜日ごとの歩数データ収集用
        self.step_data = {day.value: [] for day in DayType}
    
    def get_day_type(self, date: datetime) -> DayType:
        """日付から曜日タイプを取得"""
        weekday = date.weekday()  # 0=月曜日, 6=日曜日
        
        # 祝日判定（簡易版 - 実際は祝日APIを使用）
        if self._is_holiday(date):
            return DayType.HOLIDAY
        
        day_mapping = {
            0: DayType.MONDAY,
            1: DayType.TUESDAY,
            2: DayType.WEDNESDAY,
            3: DayType.THURSDAY,
            4: DayType.FRIDAY,
            5: DayType.SATURDAY,
            6: DayType.SUNDAY
        }
        
        return day_mapping[weekday]
    
    def _is_holiday(self, date: datetime) -> bool:
        """祝日判定（簡易版）"""
        # 実際の実装では祝日APIやライブラリを使用
        holidays = [
            (1, 1),   # 元日
            (12, 25), # クリスマス
            # 他の祝日を追加
        ]
        return (date.month, date.day) in holidays
    
    def add_step_data(self, date: datetime, steps: int, paid_money: int = 0):
        """歩数データを追加"""
        day_type = self.get_day_type(date)
        
        data_entry = {
            "date": date.strftime("%Y-%m-%d"),
            "steps": steps,
            "paid_money": paid_money,
            "timestamp": int(date.timestamp())
        }
        
        self.step_data[day_type.value].append(data_entry)
    
    def calculate_day_weight(self, day_type: DayType) -> float:
        """曜日の重みを計算（実データがある場合は更新）"""
        if not self.step_data[day_type.value]:
            return self.day_weights[day_type]
        
        # 実データから平均歩数を計算
        steps_list = [entry["steps"] for entry in self.step_data[day_type.value]]
        avg_steps = np.mean(steps_list)
        
        # 全曜日の平均と比較して重みを調整
        all_steps = []
        for day_data in self.step_data.values():
            all_steps.extend([entry["steps"] for entry in day_data])
        
        if all_steps:
            overall_avg = np.mean(all_steps)
            calculated_weight = avg_steps / overall_avg if overall_avg > 0 else 1.0
            
            # デフォルト重みと実データ重みの加重平均
            return (self.day_weights[day_type] + calculated_weight) / 2
        
        return self.day_weights[day_type]
    
    def predict_steps(self, date: datetime, base_steps: int = 8000) -> int:
        """指定日の予測歩数を計算"""
        day_type = self.get_day_type(date)
        weight = self.calculate_day_weight(day_type)
        
        predicted_steps = int(base_steps * weight)
        return predicted_steps
    
    def get_weekly_prediction(self, start_date: datetime, base_steps: int = 8000) -> Dict:
        """1週間の歩数予測"""
        predictions = {}
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_type = self.get_day_type(current_date)
            predicted_steps = self.predict_steps(current_date, base_steps)
            
            predictions[current_date.strftime("%Y-%m-%d")] = {
                "day_type": day_type.value,
                "predicted_steps": predicted_steps,
                "weight": self.calculate_day_weight(day_type)
            }
        
        return predictions
    
    def analyze_step_patterns(self) -> Dict:
        """歩数パターン分析"""
        analysis = {}
        
        for day_type in DayType:
            day_data = self.step_data[day_type.value]
            
            if day_data:
                steps_list = [entry["steps"] for entry in day_data]
                analysis[day_type.value] = {
                    "count": len(steps_list),
                    "avg_steps": int(np.mean(steps_list)),
                    "max_steps": max(steps_list),
                    "min_steps": min(steps_list),
                    "weight": self.calculate_day_weight(day_type)
                }
            else:
                analysis[day_type.value] = {
                    "count": 0,
                    "avg_steps": 0,
                    "max_steps": 0,
                    "min_steps": 0,
                    "weight": self.day_weights[day_type]
                }
        
        return analysis

# 使用例
if __name__ == "__main__":
    analyzer = WeekdayStepAnalyzer()
    
    # サンプルデータ追加
    # sample_dates = [
    #     (datetime(2024, 12, 16), 12000),  # 月曜日
    #     (datetime(2024, 12, 17), 10500),  # 火曜日
    #     (datetime(2024, 12, 18), 8000),   # 水曜日
    #     (datetime(2024, 12, 19), 9500),   # 木曜日
    #     (datetime(2024, 12, 20), 7000),   # 金曜日
    #     (datetime(2024, 12, 21), 15000),  # 土曜日
    #     (datetime(2024, 12, 22), 6000),   # 日曜日
    # ]
    
    file_path = 'dammy_step_data.csv'
    sample_dates = pd.read_csv(file_path)
    
    print("hello")
    sample_dates.head()
    # with open("dammy_step_data.csv", "r") as f:
    #     sample_dates = csv.reader(f, delimiter=",")
    #     for row in sample_dates:
    #         print(row)  # 各行を表示する例

    # print(f"a:{sample_dates[0][0]}")
    # step = s[2]
    # timestamp =s[3]
    
    # for date, steps in sample_dates:
        # print(date, steps)
        # analyzer.add_step_data(date, steps)
    
    # 今日の予測
    today = datetime.now()
    predicted_steps = analyzer.predict_steps(today)
    day_type = analyzer.get_day_type(today)
    
    print(f"今日（{day_type.value}）の予測歩数: {predicted_steps:,}歩")
    
    # 1週間の予測
    print("\n=== 1週間の歩数予測 ===")
    weekly_pred = analyzer.get_weekly_prediction(today)
    for date, pred in weekly_pred.items():
        print(f"{date} ({pred['day_type']}): {pred['predicted_steps']:,}歩 (重み: {pred['weight']:.2f})")
    
    # パターン分析
    print("\n=== 曜日別歩数パターン ===")
    patterns = analyzer.analyze_step_patterns()
    for day, data in patterns.items():
        print(f"{day}: 平均{data['avg_steps']:,}歩 (重み: {data['weight']:.2f})")

# step_day_type = {
#     "Monday":[
#               {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},  {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
#     ],
# "Tuesday":[
#       {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},  {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ],
# "Wednesday":[
#       {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},  {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ],1
# "Thursday":[
#       {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},  {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ],
# "Friday":[
#      {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},   {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ],
# "Saturday":[
#      {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},   {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ],
# "Sunday":[
#     {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},    {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ],
# "holiday":[
#     {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233},    {"template":24,"steps":43225,"paid_monney":2422,"create_at":2453233}
# ]

# }



Day_type = "Monday"




# 何曜日かどうかを取得してどれくらいDateTimeが変わるのかわからない。
