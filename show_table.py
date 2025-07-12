import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


def main():
    """
    データベースに接続し、指定したテーブルの内容を読み込んで表示する。
    """
    # --- 1. 環境変数の読み込みとデータベースへの接続設定 ---
    load_dotenv()
    db_url = os.getenv("DB_URL")

    if not db_url:
        print("❌ エラー: 環境変数 'DB_URL' が設定されていません。")
        return  # 関数を終了

    try:
        engine = create_engine(db_url)
        print("✅ データベースへの接続に成功しました。")
    except Exception as e:
        print(f"❌ データベース接続中にエラーが発生しました: {e}")
        return

    # --- 2. データベースからデータを読み込む ---
    # 確認したいテーブル名を指定
    table_name = "activity"

    try:
        print(f"\nテーブル '{table_name}' の内容を読み込んでいます...")
        # pandasのread_sql関数でテーブル全体をDataFrameとして読み込む
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)

        # --- 3. 読み込んだデータを表示 ---
        if df.empty:
            print(f"✅ テーブル '{table_name}' は存在しますが、データは空です。")
        else:
            print(f"✅ テーブル '{table_name}' の内容:")
            print(df)

    except Exception as e:
        print(f"\n❌ データの読み込み中にエラーが発生しました: {e}")
        print("ヒント: テーブル名が正しいか、テーブルが存在するか確認してください。")


if __name__ == "__main__":
    main()
