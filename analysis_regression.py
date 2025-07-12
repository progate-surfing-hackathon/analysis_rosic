import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# 1. サンプルデータの作成
# 乱数のシードを固定
np.random.seed(0)
num_samples = 100

# 説明変数
temperature = np.random.uniform(20, 35, num_samples)  # 気温 (20-35℃)
steps = np.random.uniform(3000, 15000, num_samples)  # 歩数 (3000-15000歩)

# 目的変数（飲料代）
# 飲料代 = 15 * 気温 + 0.02 * 歩数 - 150 + ノイズ
beverage_spending = (
    15 * temperature + 0.02 * steps - 150 + np.random.normal(0, 50, num_samples)
)
beverage_spending[beverage_spending < 0] = 0  # 0円未満にならないように調整

# データフレームの作成
df = pd.DataFrame(
    {"Temperature": temperature, "Steps": steps, "Beverage_Spending": beverage_spending}
)

# 2. 重回帰モデルの学習
# 説明変数Xと目的変数y
X = df[["Temperature", "Steps"]]
y = df["Beverage_Spending"]

# モデルのインスタンス化と学習
model = LinearRegression()
model.fit(X, y)

# 3. モデルの評価
# 回帰係数と切片
coef = model.coef_
intercept = model.intercept_
# 決定係数 (R^2)
r2_score = model.score(X, y)

print("## 重回帰分析の結果")
print(f"回帰係数 (気温, 歩数): {coef}")
print(f"切片: {intercept:.2f}")
print(f"決定係数 (R^2): {r2_score:.3f}")
print("---")
print("回帰式:")
print(f"飲料代 = {coef[0]:.2f} * 気温 + {coef[1]:.3f} * 歩数 + ({intercept:.2f})")
print("---")


# 4. 新しいデータでの予測
# 新しいデータ (気温30℃、歩数8000歩)
new_data = pd.DataFrame([[30, 8000]], columns=["Temperature", "Steps"])
predicted_spending = model.predict(new_data)

print("## 新しいデータでの予測")
print(
    f"気温{new_data['Temperature'][0]}℃、歩数{new_data['Steps'][0]}歩の時の飲料代予測: {predicted_spending[0]:.2f}円"
)
