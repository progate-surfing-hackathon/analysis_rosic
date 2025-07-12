import os

import boto3

# 他のpyファイルから関数をインポートする場合
from analysis_regression import *

ssm = boto3.client("ssm")


def get_parameter(name):
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]


def lambda_handler(event, context):
    """
    この関数がLambdaの実行起点（ハンドラ）です。
    event: Lambdaへの入力データ（API Gatewayからのリクエストなど）
    context: 実行環境の情報
    """
    print("Lambda function started.")

    db_url = get_parameter("/my-app/database-url")
    main(db_url)

    # 処理結果を返す
    return {"statusCode": 200, "body": "Analysis completed successfully."}


# --- 以下、既存のanalysis.pyのコードが続く ---
