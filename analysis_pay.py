import numpy as np
from typing import Dict

class BeveragePurchasePredictor:
    def __init__(self):
        # 基本価格設定
        self.base_prices = {
            '水': 100,
            'お茶': 120,
            'コーヒー': 150,
            'スポーツドリンク': 180,
            'ジュース': 130,
            'エナジードリンク': 200
        }
    
    def get_beverage_type(self, temperature: float, activity_level: str) -> str:
        """条件に基づいて推奨飲料を決定"""
        if temperature >= 30:
            if activity_level in ['高', '激しい']:
                return 'スポーツドリンク'
            return 'お茶'
        elif temperature >= 20:
            if activity_level in ['高', '激しい']:
                return 'スポーツドリンク'
            return 'コーヒー'
        else:
            return 'コーヒー'
    
    def calculate_purchase_multiplier(self, temperature: float, activity_level: str, 
                                    location_type: str, time_hour: int) -> float:
        """購入確率と価格倍率を計算"""
        multiplier = 1.0
        
        # 気温による倍率
        if temperature >= 35:
            multiplier *= 1.8
        elif temperature >= 30:
            multiplier *= 1.5
        elif temperature >= 25:
            multiplier *= 1.2
        elif temperature <= 10:
            multiplier *= 0.8
        
        # 活動レベルによる倍率
        activity_multipliers = {
            'なし': 0.8,
            '軽い': 1.0,
            '中程度': 1.3,
            '高': 1.6,
            '激しい': 2.0
        }
        multiplier *= activity_multipliers.get(activity_level, 1.0)
        
        # 場所による倍率
        location_multipliers = {
            '駅': 1.4,
            'コンビニ': 1.2,
            'オフィス': 0.9,
            '公園': 1.3,
            'ジム': 1.5,
            '自宅': 0.7
        }
        multiplier *= location_multipliers.get(location_type, 1.0)
        
        # 時間による倍率
        if 11 <= time_hour <= 13:  # 昼食時間
            multiplier *= 1.2
        elif 15 <= time_hour <= 17:  # 午後の休憩
            multiplier *= 1.1
        
        return multiplier
    
    def predict_purchase_amount(self, temperature: float, activity_level: str, 
                              location_type: str, time_hour: int) -> Dict:
        """購入予測金額を計算"""
        # 推奨飲料タイプを決定
        beverage_type = self.get_beverage_type(temperature, activity_level)
        
        # 基本価格を取得
        base_price = self.base_prices.get(beverage_type, 150)
        
        # 購入倍率を計算
        multiplier = self.calculate_purchase_multiplier(
            temperature, activity_level, location_type, time_hour
        )
        
        # 最終予測金額
        predicted_amount = int(base_price * multiplier)
        
        # 購入確率を計算
        purchase_probability = min(multiplier * 0.4, 0.95)  # 最大95%
        
        return {
            'predicted_amount': predicted_amount,
            'beverage_type': beverage_type,
            'base_price': base_price,
            'multiplier': round(multiplier, 2),
            'purchase_probability': round(purchase_probability, 2)
        }
    
    def get_purchase_recommendation(self, temperature: float, activity_level: str, 
                                  location_type: str, time_hour: int) -> str:
        """購入推奨メッセージを生成"""
        prediction = self.predict_purchase_amount(temperature, activity_level, location_type, time_hour)
        
        if prediction['purchase_probability'] >= 0.8:
            return f"強く推奨: {prediction['beverage_type']}を購入することをお勧めします"
        elif prediction['purchase_probability'] >= 0.6:
            return f"推奨: {prediction['beverage_type']}の購入を検討してください"
        elif prediction['purchase_probability'] >= 0.4:
            return f"軽い推奨: {prediction['beverage_type']}があると良いでしょう"
        else:
            return "購入の必要性は低いです"
    
    def analyze_purchase_scenario(self, scenarios: list) -> Dict:
        """複数シナリオの購入予測分析"""
        results = []
        
        for scenario in scenarios:
            prediction = self.predict_purchase_amount(
                scenario['temperature'],
                scenario['activity_level'],
                scenario['location_type'],
                scenario['time_hour']
            )
            
            results.append({
                'scenario': scenario,
                'prediction': prediction,
                'recommendation': self.get_purchase_recommendation(
                    scenario['temperature'],
                    scenario['activity_level'],
                    scenario['location_type'],
                    scenario['time_hour']
                )
            })
        
        return {
            'scenarios': results,
            'avg_predicted_amount': np.mean([r['prediction']['predicted_amount'] for r in results]),
            'max_predicted_amount': max([r['prediction']['predicted_amount'] for r in results]),
            'high_probability_count': len([r for r in results if r['prediction']['purchase_probability'] >= 0.7])
        }

# 使用例
if __name__ == "__main__":
    predictor = BeveragePurchasePredictor()
    
    # 単一予測
    print("=== 購入予測 ===")
    prediction = predictor.predict_purchase_amount(
        temperature=32,
        activity_level='高',
        location_type='駅',
        time_hour=14
    )
    
    print(f"予測購入金額: ¥{prediction['predicted_amount']}")
    print(f"推奨飲料: {prediction['beverage_type']}")
    print(f"購入確率: {prediction['purchase_probability']*100:.0f}%")
    print(f"価格倍率: {prediction['multiplier']}")
    
    # 推奨メッセージ
    recommendation = predictor.get_purchase_recommendation(32, '高', '駅', 14)
    print(f"推奨: {recommendation}")
    
    # 複数シナリオ分析
    print("\n=== シナリオ分析 ===")
    scenarios = [
        {'temperature': 35, 'activity_level': '激しい', 'location_type': 'ジム', 'time_hour': 16},
        {'temperature': 25, 'activity_level': '軽い', 'location_type': 'オフィス', 'time_hour': 10},
        {'temperature': 15, 'activity_level': 'なし', 'location_type': '自宅', 'time_hour': 20}
    ]
    
    analysis = predictor.analyze_purchase_scenario(scenarios)
    print(f"平均予測金額: ¥{analysis['avg_predicted_amount']:.0f}")
    print(f"最大予測金額: ¥{analysis['max_predicted_amount']}")
    print(f"高確率購入シナリオ数: {analysis['high_probability_count']}/3")