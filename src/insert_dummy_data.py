import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. 環境変数の読み込みとデータベースへの接続設定 ---
load_dotenv()  # .envファイルから環境変数を読み込む

# 環境変数からデータベース接続情報を取得
db_url = os.environ["DB_URL"]

# db_urlが設定されていない場合はエラーメッセージを表示して終了
if not db_url:
    print("❌ エラー: 環境変数 'DB_URL' が設定されていません。")
    exit()

try:
    engine = create_engine(db_url)
    print("✅ データベースへの接続設定が完了しました。")
except Exception as e:
    print(f"❌ データベース接続中にエラーが発生しました: {e}")
    exit()


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
    df.to_sql("activity", con=engine, if_exists="replace", index=False)
    print("\n✅ データベースへのデータインサートが完了しました。")
except Exception as e:
    print(f"\n❌ データベースへのインサート中にエラーが発生しました: {e}")
