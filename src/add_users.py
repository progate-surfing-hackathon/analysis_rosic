import os
import uuid

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --- 1. 環境変数の読み込みとデータベースへの接続設定 ---
load_dotenv()  # .envファイルから環境変数を読み込む

# 環境変数からデータベース接続URLを取得
db_url = os.getenv("DB_URL")

# db_urlが設定されていない場合はエラーメッセージを表示して終了
if not db_url:
    print("❌ エラー: 環境変数 'DB_URL' が設定されていません。")
    exit()

try:
    # SQLAlchemyのengineを作成して接続を準備
    engine = create_engine(db_url)
    print("✅ データベースへの接続設定が完了しました。")
except Exception as e:
    print(f"❌ データベース接続中にエラーが発生しました: {e}")
    exit()


# --- 2. 挿入するデータの準備 ---
authors_to_add = [
    "Taro Yamada",
    "Hanako Sato",
    "Jiro Suzuki",
    "Yoshiko Watanabe",
]

# DataFrame用のデータリストを作成 (辞書のリスト)
data_for_df = [
    {
        "id": str(uuid.uuid4()),  # 各authorにユニークなIDを生成
        "author": author,
        "notification_token": str(uuid.uuid4()),  # 各authorにユニークなtokenを生成
    }
    for author in authors_to_add
]

# Pandas DataFrameを作成
df = pd.DataFrame(data_for_df)
print("\n📝 挿入するデータ:")
print(df)


# --- 3. DataFrameをデータベースにインサート ---
try:
    # to_sqlを使用してDataFrameを'users'テーブルに追加
    # if_exists='append': テーブルが存在する場合、データを追加する
    # index=False: DataFrameのインデックス(0, 1, 2...)をDBに保存しない
    df.to_sql("users", con=engine, if_exists="append", index=False)
    print("\n✅ データベースへのデータインサートが完了しました。")

except Exception as e:
    print(f"\n❌ データベースへのインサート中にエラーが発生しました: {e}")
