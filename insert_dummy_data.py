import pandas as pd
from sqlalchemy import create_engine

# --- 1. データベースへの接続設定 ---
# ご自身のRDSの接続情報に書き換えてください (MySQLの場合)
db_url = (
    "mysql+mysqlconnector://<ユーザー名>:<パスワード>@<エンドポイント>:<ポート>/<DB名>"
)
engine = create_engine(db_url)

# --- 2. CSVファイルの読み込み ---
try:
    df = pd.read_csv("dummy_activity.csv")
    print("✅ CSVファイルの読み込みに成功しました。")
    print(df)
except FileNotFoundError:
    print("❌ エラー: dummy_activity.csv が見つかりません。")
    exit()

# --- 3. DataFrameをデータベースにインサート ---
# テーブル名: 'activity'
# if_exists='append': テーブルが既に存在する場合、データを追加する
# index=False: DataFrameのインデックスをDBのカラムとして保存しない
try:
    df.to_sql("activity", con=engine, if_exists="append", index=False)
    print("\n✅ データベースへのデータインサートが完了しました。")
except Exception as e:
    print(f"\n❌ データベースへのインサート中にエラーが発生しました: {e}")
