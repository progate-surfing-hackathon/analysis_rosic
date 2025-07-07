import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple, Optional
import json

class BeverageTimingAnalyzer:
    def __init__(self):
        # 体感温度計算用の定数
        self.HEAT_INDEX_COEFFICIENTS = {
            'c1': -42.379,
            'c2': 2.04901523,
            'c3': 10.14333127,
            'c4': -0.22475541,
            'c5': -0.00683783,
            'c6': -0.05481717,
            'c7': 0.00122874,
            'c8': 0.00085282,
            'c9': -0.00000199
        }
        
        # 飲料購入スコア計算用の重み
        self.WEIGHTS = {
            'temperature': 0.4,
            'weather': 0.3,
            'time': 0.2,
            'location': 0.1
        }
    
    def calculate_heat_index(self, temperature: float, humidity: float) -> float:
        """
        気温（摂氏）と湿度から体感温度を計算
        """
        # 摂氏を華氏に変換
        temp_f = temperature * 9/5 + 32
        
        # 体感温度計算（華氏）
        c = self.HEAT_INDEX_COEFFICIENTS
        heat_index_f = (c['c1'] + 
                       c['c2'] * temp_f + 
                       c['c3'] * humidity + 
                       c['c4'] * temp_f * humidity + 
                       c['c5'] * temp_f**2 + 
                       c['c6'] * humidity**2 + 
                       c['c7'] * temp_f**2 * humidity + 
                       c['c8'] * temp_f * humidity**2 + 
                       c['c9'] * temp_f**2 * humidity**2)
        
        # 華氏を摂氏に変換
        heat_index_c = (heat_index_f - 32) * 5/9
        
        # 簡単な体感温度計算（湿度が低い場合）
        if humidity < 40:
            return temperature
        
        return heat_index_c
    
    def get_weather_score(self, weather: str) -> float:
        """
        天気による飲料購入スコア（0-1）
        """
        weather_scores = {
            '晴れ': 0.9,
            '曇り': 0.6,
            '雨': 0.3,
            '雪': 0.2,
            '台風': 0.1,
            '快晴': 1.0,
            '薄曇り': 0.7,
            '小雨': 0.4,
            '大雨': 0.2
        }
        return weather_scores.get(weather.lower(), 0.5)
    
    def get_time_score(self, hour: int) -> float:
        """
        時間による飲料購入スコア（0-1）
        """
        # 飲み物を飲みたくなる時間帯を考慮
        if 6 <= hour <= 9:    # 朝の通勤時間
            return 0.8
        elif 11 <= hour <= 13:  # 昼食時間
            return 0.9
        elif 15 <= hour <= 17:  # 午後の休憩時間
            return 0.7
        elif 19 <= hour <= 21:  # 夕方・夜
            return 0.6
        else:
            return 0.3
    
    def get_location_score(self, location_type: str) -> float:
        """
        場所による飲料購入スコア（0-1）
        """
        location_scores = {
            '駅': 0.9,
            'オフィス': 0.7,
            '公園': 0.8,
            '商業施設': 0.6,
            '住宅地': 0.4,
            '学校': 0.8,
            '病院': 0.5,
            '運動施設': 0.9,
            '観光地': 0.8
        }
        return location_scores.get(location_type, 0.5)
    
    def calculate_purchase_score(self, data: Dict) -> float:
        """
        総合的な飲料購入スコアを計算
        """
        # 体感温度スコア（温度が高いほど高スコア）
        heat_index = self.calculate_heat_index(data['temperature'], data['humidity'])
        temp_score = min(max((heat_index - 10) / 30, 0), 1)  # 10-40度を0-1にマッピング
        
        # 各要素のスコア計算
        weather_score = self.get_weather_score(data['weather'])
        time_score = self.get_time_score(data['hour'])
        location_score = self.get_location_score(data['location_type'])
        
        # 重み付き総合スコア
        total_score = (
            temp_score * self.WEIGHTS['temperature'] +
            weather_score * self.WEIGHTS['weather'] +
            time_score * self.WEIGHTS['time'] +
            location_score * self.WEIGHTS['location']
        )
        
        return total_score
    
    def recommend_beverage_type(self, data: Dict) -> str:
        """
        条件に基づいて推奨飲料タイプを決定
        """
        heat_index = self.calculate_heat_index(data['temperature'], data['humidity'])
        
        if heat_index >= 30:
            return "冷たい飲み物（アイスコーヒー、冷茶、スポーツドリンク）"
        elif heat_index >= 20:
            return "常温または冷たい飲み物（お茶、水、ジュース）"
        elif heat_index >= 10:
            return "常温の飲み物（お茶、コーヒー）"
        else:
            return "温かい飲み物（ホットコーヒー、温茶）"
    
    def analyze_purchase_timing(self, data_list: List[Dict]) -> pd.DataFrame:
        """
        データリストから購入タイミングを分析
        """
        results = []
        
        for data in data_list:
            heat_index = self.calculate_heat_index(data['temperature'], data['humidity'])
            purchase_score = self.calculate_purchase_score(data)
            recommended_beverage = self.recommend_beverage_type(data)
            
            result = {
                'timestamp': data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'location': data.get('location_name', 'Unknown'),
                'location_type': data['location_type'],
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'heat_index': round(heat_index, 1),
                'weather': data['weather'],
                'hour': data['hour'],
                'purchase_score': round(purchase_score, 3),
                'recommended_beverage': recommended_beverage,
                'purchase_recommendation': self.get_purchase_recommendation(purchase_score)
            }
            results.append(result)
        
        return pd.DataFrame(results)
    
    def get_purchase_recommendation(self, score: float) -> str:
        """
        スコアに基づいて購入推奨度を返す
        """
        if score >= 0.8:
            return "強く推奨"
        elif score >= 0.6:
            return "推奨"
        elif score >= 0.4:
            return "やや推奨"
        else:
            return "推奨しない"

# 使用例
def main():
    analyzer = BeverageTimingAnalyzer()
    
    # サンプルデータ
    sample_data = [
        {
            'timestamp': '2024-07-15 12:30:00',
            'location_name': '新宿駅',
            'location_type': '駅',
            'temperature': 32.0,
            'humidity': 70.0,
            'weather': '晴れ',
            'hour': 12
        },
        {
            'timestamp': '2024-07-15 15:45:00',
            'location_name': 'オフィス',
            'location_type': 'オフィス',
            'temperature': 28.0,
            'humidity': 65.0,
            'weather': '曇り',
            'hour': 15
        },
        {
            'timestamp': '2024-07-15 09:15:00',
            'location_name': '代々木公園',
            'location_type': '公園',
            'temperature': 25.0,
            'humidity': 55.0,
            'weather': '快晴',
            'hour': 9
        },
        {
            'timestamp': '2024-07-15 20:00:00',
            'location_name': '住宅地',
            'location_type': '住宅地',
            'temperature': 18.0,
            'humidity': 45.0,
            'weather': '雨',
            'hour': 20
        }
    ]
    
    # 分析実行
    results_df = analyzer.analyze_purchase_timing(sample_data)
    
    # 結果表示
    print("=== 飲料購入タイミング分析結果 ===")
    print(results_df.to_string(index=False))
    
    # 最適な購入タイミングの特定
    best_timing = results_df.loc[results_df['purchase_score'].idxmax()]
    print(f"\n=== 最適な購入タイミング ===")
    print(f"時刻: {best_timing['timestamp']}")
    print(f"場所: {best_timing['location']} ({best_timing['location_type']})")
    print(f"体感温度: {best_timing['heat_index']}°C")
    print(f"購入スコア: {best_timing['purchase_score']}")
    print(f"推奨: {best_timing['purchase_recommendation']}")
    print(f"推奨飲料: {best_timing['recommended_beverage']}")

if __name__ == "__main__":
    main()
