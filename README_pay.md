# Analysis Pay - 飲料購入金額予測エンジン

条件に基づいて実際の飲料購入金額と確率を予測するシンプルな分析ツールです。

## 💰 概要

気温・活動レベル・場所・時間から「今日はいくら使いそうか？」を予測します。

## 🚀 クイックスタート

```python
from analysis_pay import BeveragePurchasePredictor

predictor = BeveragePurchasePredictor()
prediction = predictor.predict_purchase_amount(32, '高', '駅', 14)
print(f"予測金額: ¥{prediction['predicted_amount']}")
```

## 📊 主要機能

### 購入金額予測
```python
prediction = predictor.predict_purchase_amount(
    temperature=32,      # 気温
    activity_level='高', # 活動レベル
    location_type='駅',  # 場所
    time_hour=14        # 時間
)

# 結果
{
    'predicted_amount': 288,           # 予測金額
    'beverage_type': 'スポーツドリンク', # 推奨飲料
    'purchase_probability': 0.64,      # 購入確率
    'multiplier': 1.6                  # 価格倍率
}
```

### 購入推奨メッセージ
```python
recommendation = predictor.get_purchase_recommendation(32, '高', '駅', 14)
# → "推奨: スポーツドリンクの購入を検討してください"
```

### 複数シナリオ分析
```python
scenarios = [
    {'temperature': 35, 'activity_level': '激しい', 'location_type': 'ジム', 'time_hour': 16},
    {'temperature': 25, 'activity_level': '軽い', 'location_type': 'オフィス', 'time_hour': 10}
]

analysis = predictor.analyze_purchase_scenario(scenarios)
print(f"平均予測金額: ¥{analysis['avg_predicted_amount']:.0f}")
```

## 🔧 価格設定

### 基本価格
- **水**: ¥100
- **お茶**: ¥120  
- **コーヒー**: ¥150
- **スポーツドリンク**: ¥180
- **ジュース**: ¥130
- **エナジードリンク**: ¥200

### 倍率要素

#### 気温倍率
- **35度以上**: 1.8倍
- **30-34度**: 1.5倍
- **25-29度**: 1.2倍
- **10度以下**: 0.8倍

#### 活動レベル倍率
- **激しい**: 2.0倍
- **高**: 1.6倍
- **中程度**: 1.3倍
- **軽い**: 1.0倍
- **なし**: 0.8倍

#### 場所倍率
- **ジム**: 1.5倍
- **駅**: 1.4倍
- **公園**: 1.3倍
- **コンビニ**: 1.2倍
- **オフィス**: 0.9倍
- **自宅**: 0.7倍

#### 時間倍率
- **昼食時間 (11-13時)**: 1.2倍
- **午後休憩 (15-17時)**: 1.1倍

## 📈 予測例

```
条件: 32度、高活動、駅、14時
→ スポーツドリンク (¥180) × 1.6倍 = ¥288
→ 購入確率: 64%
→ 推奨: "スポーツドリンクの購入を検討してください"

条件: 15度、なし、自宅、20時  
→ コーヒー (¥150) × 0.56倍 = ¥84
→ 購入確率: 22%
→ 推奨: "購入の必要性は低いです"
```

## 🎯 使用場面

- **日次予算計画**: 今日の飲料代予測
- **行動最適化**: 購入タイミングの判断
- **コスト管理**: 月間支出の事前把握
- **健康管理**: 適切な水分補給の促進

## 📝 API リファレンス

### predict_purchase_amount(temperature, activity_level, location_type, time_hour)
購入金額と確率を予測

### get_purchase_recommendation(temperature, activity_level, location_type, time_hour)  
購入推奨メッセージを生成

### analyze_purchase_scenario(scenarios)
複数シナリオの一括分析

---

**Analysis Pay** - Smart Purchase Prediction 💰📊