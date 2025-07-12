# Pay Stoper - 飲料購入分析エンジン

NWWシステムの核となる分析エンジン。気象データと行動パターンから最適な飲料購入タイミングを予測します。

## 🧠 概要

体感温度計算とスマートアラートシステムにより、熱中症予防と効率的な水分補給をサポートする分析エンジンです。

## 🚀 クイックスタート

```bash
pip install -r requirements.txt
python analysis.py
```

## 📊 主要機能

### 体感温度計算
Heat Index アルゴリズムで正確な体感温度を算出：
```python
analyzer = BeverageTimingAnalyzer()
heat_index = analyzer.calculate_heat_index(temperature=30, humidity=70)
```

### 購入スコア算出
4要素の重み付き評価で購入推奨度を計算：
```python
data = {
    'temperature': 30,
    'humidity': 70,
    'weather': '晴れ',
    'hour': 14,
    'location_type': '駅'
}
score = analyzer.calculate_purchase_score(data)
```

### アラートシステム
4段階の危険度判定：
- **緊急 (0.85+)**: 🚨 熱中症の危険
- **高 (0.7+)**: 🔥 水分補給推奨  
- **中 (0.55+)**: 💧 軽い水分補給
- **低 (0.4+)**: 🍹 休憩時の水分補給

## 🔧 使用方法

### 基本的な分析
```python
from analysis import BeverageTimingAnalyzer

analyzer = BeverageTimingAnalyzer()

# データ準備
data = {
    'temperature': 32,
    'humidity': 65,
    'weather': '晴れ',
    'hour': 15,
    'location_type': '公園',
    'has_air_conditioning': False
}

# 分析実行
score = analyzer.calculate_purchase_score(data)
beverage = analyzer.recommend_beverage_type(data)
alert_level = analyzer.get_alert_level(score)

print(f"購入スコア: {score:.3f}")
print(f"推奨飲料: {beverage}")
print(f"アラートレベル: {alert_level.value if alert_level else 'なし'}")
```

### バッチ分析
```python
data_list = [
    {'temperature': 25, 'humidity': 60, 'weather': '曇り', 'hour': 10, 'location_type': 'オフィス'},
    {'temperature': 35, 'humidity': 80, 'weather': '晴れ', 'hour': 14, 'location_type': '駅'}
]

results_df = analyzer.analyze_purchase_timing(data_list)
print(results_df)
```

## 📈 アルゴリズム詳細

### Heat Index 計算式
```python
heat_index = (c1 + c2*T + c3*H + c4*T*H + 
              c5*T² + c6*H² + c7*T²*H + 
              c8*T*H² + c9*T²*H²)
```

### スコア重み配分
- **温度スコア**: 40% - 体感温度ベース
- **天気スコア**: 30% - 天候条件
- **時間スコア**: 20% - 時間帯パターン
- **場所スコア**: 10% - 立地・環境

## 🛠️ 依存関係

```
pandas>=1.5.0
numpy>=1.24.0
```

## 📝 API リファレンス

### BeverageTimingAnalyzer

#### calculate_heat_index(temperature, humidity)
気温と湿度から体感温度を計算

#### calculate_purchase_score(data)
総合的な購入スコアを算出

#### recommend_beverage_type(data)
条件に応じた推奨飲料タイプを返す

#### get_alert_level(score)
スコアからアラートレベルを判定

#### analyze_purchase_timing(data_list)
複数データの一括分析

## 🔍 デバッグ

ログレベルを設定してデバッグ情報を確認：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 出力例

```
購入スコア: 0.742
推奨飲料: 冷たい飲み物（アイスコーヒー、冷茶、スポーツドリンク）
アラートレベル: 高
体感温度: 36.2°C
推奨度: 強く推奨
```

---

**Pay Stoper** - Smart Analysis for Smart Hydration 🧠💧