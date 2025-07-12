import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple, Optional
import json
import threading
import time
from enum import Enum

class AlertLevel(Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "緊急"

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
        
        # アラート設定
        self.alert_thresholds = {
            'critical': 0.85,  # 緊急（熱中症の危険性）
            'high': 0.7,       # 高（強く推奨）
            'medium': 0.55,    # 中（推奨）
            'low': 0.4         # 低（やや推奨）
        }
        
        # アラート履歴
        self.alert_history = []
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5分間のクールダウン（秒）
    
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
    
    def get_location_score(self, location_type: str, has_air_conditioning: bool = True, 
                          from_outdoor: bool = False) -> float:
        """
        場所による飲料購入スコア（0-1）
        エアコンの有無と屋外からの移動を考慮
        """
        base_scores = {
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
        
        base_score = base_scores.get(location_type, 0.5)
        
        # 室内でエアコンがある場合はスコアを下げる
        indoor_locations = ['オフィス', '商業施設', '住宅地', '学校', '病院']
        if location_type in indoor_locations and has_air_conditioning:
            base_score *= 0.5  # エアコンがある室内では需要が半減
            
            # ただし、屋外から戻ってきた直後なら補正
            if from_outdoor:
                base_score *= 1.6  # 外回りから戻った場合は需要増加
        
        return min(base_score, 1.0)
    
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
        location_score = self.get_location_score(
            data['location_type'], 
            data.get('has_air_conditioning', True),
            data.get('from_outdoor', False)
        )
        
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
    
    def get_alert_level(self, score: float) -> AlertLevel:
        """
        スコアに基づいてアラートレベルを決定
        """
        if score >= self.alert_thresholds['critical']:
            return AlertLevel.CRITICAL
        elif score >= self.alert_thresholds['high']:
            return AlertLevel.HIGH
        elif score >= self.alert_thresholds['medium']:
            return AlertLevel.MEDIUM
        elif score >= self.alert_thresholds['low']:
            return AlertLevel.LOW
        else:
            return None
    
    def should_send_alert(self, score: float) -> bool:
        """
        アラートを送信すべきかどうか判定
        """
        # 最低閾値を超えているか
        if score < self.alert_thresholds['low']:
            return False
        
        # クールダウン期間中かチェック
        if self.last_alert_time:
            time_diff = (datetime.now() - self.last_alert_time).total_seconds()
            if time_diff < self.alert_cooldown:
                return False
        
        return True
    
    def create_alert_message(self, data: Dict, score: float, alert_level: AlertLevel) -> Dict:
        """
        アラートメッセージを生成
        """
        heat_index = self.calculate_heat_index(data['temperature'], data['humidity'])
        recommended_beverage = self.recommend_beverage_type(data)
        
        # アラートレベルに応じたメッセージ
        level_messages = {
            AlertLevel.CRITICAL: "🚨 緊急：熱中症の危険があります！すぐに水分補給してください",
            AlertLevel.HIGH: "🔥 高温注意：水分補給をお勧めします",
            AlertLevel.MEDIUM: "💧 水分補給タイム：飲み物はいかがですか？",
            AlertLevel.LOW: "🍹 休憩時間：軽い水分補給をどうぞ"
        }
        
        alert_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'alert_level': alert_level.value,
            'score': round(score, 3),
            'message': level_messages[alert_level],
            'location': data.get('location_name', 'Unknown'),
            'temperature': data['temperature'],
            'heat_index': round(heat_index, 1),
            'recommended_beverage': recommended_beverage,
            'details': {
                'weather': data['weather'],
                'humidity': data['humidity'],
                'has_air_conditioning': data.get('has_air_conditioning', True),
                'from_outdoor': data.get('from_outdoor', False)
            }
        }
        
        return alert_data
    
    def send_alert(self, alert_data: Dict):
        """
        アラートを送信（実際の実装では通知サービスに送信）
        """
        print(f"\n{'='*50}")
        print(f"🚨 飲料購入アラート 🚨")
        print(f"{'='*50}")
        print(f"時刻: {alert_data['timestamp']}")
        print(f"場所: {alert_data['location']}")
        print(f"アラートレベル: {alert_data['alert_level']}")
        print(f"メッセージ: {alert_data['message']}")
        print(f"購入スコア: {alert_data['score']}")
        print(f"現在温度: {alert_data['temperature']}°C")
        print(f"体感温度: {alert_data['heat_index']}°C")
        print(f"推奨飲料: {alert_data['recommended_beverage']}")
        
        # 詳細情報
        details = alert_data['details']
        print(f"\n--- 詳細情報 ---")
        print(f"天気: {details['weather']}")
        print(f"湿度: {details['humidity']}%")
        print(f"エアコン: {'あり' if details['has_air_conditioning'] else 'なし'}")
        print(f"屋外から: {'はい' if details['from_outdoor'] else 'いいえ'}")
        print(f"{'='*50}\n")
        
        # 履歴に追加
        self.alert_history.append(alert_data)
        self.last_alert_time = datetime.now()
    
    def check_and_alert(self, data: Dict) -> bool:
        """
        条件をチェックしてアラートを送信
        """
        score = self.calculate_purchase_score(data)
        alert_level = self.get_alert_level(score)
        
        if alert_level and self.should_send_alert(score):
            alert_data = self.create_alert_message(data, score, alert_level)
            self.send_alert(alert_data)
            return True
        
        return False
    
    def monitor_conditions(self, data_stream: List[Dict], interval: int = 60):
        """
        継続的に条件をモニタリング（実際の実装では別スレッドで実行）
        """
        print("🔍 飲料購入条件の監視を開始します...")
        
        for data in data_stream:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 条件チェック中...")
            print(f"場所: {data.get('location_name', 'Unknown')}")
            print(f"温度: {data['temperature']}°C, 湿度: {data['humidity']}%")
            
            alert_sent = self.check_and_alert(data)
            
            if not alert_sent:
                score = self.calculate_purchase_score(data)
                print(f"購入スコア: {score:.3f} - アラート閾値未満")
            
            # 実際の実装では time.sleep(interval) を使用
            time.sleep(1)  # デモ用に短縮
    
    def get_alert_summary(self) -> Dict:
        """
        アラート履歴の要約を取得
        """
        if not self.alert_history:
            return {"total_alerts": 0, "by_level": {}}
        
        level_counts = {}
        for alert in self.alert_history:
            level = alert['alert_level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            "total_alerts": len(self.alert_history),
            "by_level": level_counts,
            "latest_alert": self.alert_history[-1] if self.alert_history else None
        }

# 使用例
def main():
    analyzer = BeverageTimingAnalyzer()
    
    # アラート機能のデモ
    print("=== 飲料購入アラートシステム デモ ===\n")
    
    # 監視用データストリーム（実際にはセンサーやAPIから取得）
    monitoring_data = [
        {
            'timestamp': '2024-07-15 08:30:00',
            'location_name': 'JR新宿駅南口改札付近',
            'location_type': '駅',
            'temperature': 24.5,
            'humidity': 85.0,
            'weather': '曇り',
            'hour': 8,
            'has_air_conditioning': False,
            'from_outdoor': True
        },
        {
            'timestamp': '2024-07-15 09:00:00',
            'location_name': '西新宿オフィスビル（15階）',
            'location_type': 'オフィス',
            'temperature': 26.8,
            'humidity': 78.0,
            'weather': '曇り',
            'hour': 9,
            'has_air_conditioning': True,
            'from_outdoor': True  # 屋外から到着した直後で、外の湿気と熱が残っている状態
        },
        {
            'timestamp': '2024-07-15 12:15:00',
            'location_name': '新宿中央公園',
            'location_type': '公園',
            'temperature': 27.7,
            'humidity': 72.0,
            'weather': '曇り',
            'hour': 12,
            'has_air_conditioning': False,
            'from_outdoor': True # 昼休憩で屋外にいる状態
        },
        {
            'timestamp': '2024-07-15 15:00:00',
            'location_name': '西新宿オフィスビル（15階）',
            'location_type': 'オフィス',
            'temperature': 26.0,
            'humidity': 65.0,
            'weather': '小雨', # 天気概況の「一時雨」を反映
            'hour': 15,
            'has_air_conditioning': True,
            'from_outdoor': False # オフィス内で安定した環境
        },
        {
            'timestamp': '2024-07-15 15:30:00',
            'location_name': '甲州街道沿い（移動中）',
            'location_type': '路上',
            'temperature': 26.5,
            'humidity': 92.0,
            'weather': '雨', # 雨が本降りになった状況
            'hour': 15,
            'has_air_conditioning': False,
            'from_outdoor': True
        },
        {
            'timestamp': '2024-07-15 19:30:00',
            'location_name': 'ルミネエスト新宿 レストランフロア',
            'location_type': '商業施設',
            'temperature': 27.5,
            'humidity': 70.0,
            'weather': '曇り', # 外は雨が上がった設定
            'hour': 19,
            'has_air_conditioning': True,
            'from_outdoor': False # 人の熱気でやや温度・湿度が高い屋内
        },
        {
            'timestamp': '2024-07-15 23:00:00',
            'location_name': '新宿区内の住宅',
            'location_type': '住宅地',
            'temperature': 25.0,
            'humidity': 80.0,
            'weather': '曇り',
            'hour': 23,
            'has_air_conditioning': True, # 自宅の空調が効いている状態
            'from_outdoor': False
        }
    ]
    
    # 監視開始
    analyzer.monitor_conditions(monitoring_data)
    
    # アラート履歴の確認
    summary = analyzer.get_alert_summary()
    print("\n=== アラート履歴 ===")
    print(f"総アラート数: {summary['total_alerts']}")
    if summary['by_level']:
        print("レベル別:")
        for level, count in summary['by_level'].items():
            print(f"  {level}: {count}回")
    
    # 単発チェックのデモ
    print("\n=== 単発条件チェック ===")
    test_data = {
        'location_name': '代々木公園',
        'location_type': '公園',
        'temperature': 38.0,
        'humidity': 80.0,
        'weather': '快晴',
        'hour': 14,
        'has_air_conditioning': False,
        'from_outdoor': True
    }
    
    analyzer.check_and_alert(test_data)

if __name__ == "__main__":
    main()