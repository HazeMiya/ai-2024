#================================================================
# 本の概要からLLMを使用して、ジャンル、季節、主人公の年齢、舞台、要約を抽出するスクリプト
#================================================================
# 概要:
# Wikipediaから取得した本の概要を元にLLMを使用して、「ジャンル」「季節」「主人公の年齢」「舞台」「要約」を抽出する。
#
# ライブラリ:
#   - google-generativeai: https://pypi.org/project/google-generativeai/
#
# 手順:
#   1. Wikipediaから取得した本の概要を読み込む
#   2. LLMを使用して、以下の情報を抽出する：
#       - ジャンル
#       - 季節
#       - 主人公の年齢
#       - 舞台
#       - 要約
#   3. 抽出した情報をCSVファイルに保存する
#
# 使用方法:
#   - $ docker-compose up -d
#   - $ python3 004_add_info.py
#================================================================

import os
import json
import time
import pandas as pd
import google.generativeai as genai

# APIキーを直接記述 (本番環境では絶対に避けてください！)
API_KEY = "AIzaSyBPFFSkXc_-OzJRVjwcX3N7wsHecDQSsOE"  # 取得したAPIキーに置き換えてください
genai.configure(api_key=API_KEY)

def extract_book_features(text: str) -> dict:
    if not text:
        return {}

    prompt = f"""
    次の文章から、以下の情報を抽出してください：

    1. ジャンル（以下から最も近いものを1つ選んでください）：
    - 恋愛小説
    - ミステリー
    - SF
    - ファンタジー
    - 歴史小説
    - 文学
    - 青春小説
    - ホラー
    - その他

    2. 季節（以下から1つ選んでください。備考など入れないでください。複数の季節がある場合は、最も重要な季節を選択）：
    - 春
    - 夏
    - 秋
    - 冬
    - 不明
    
    3. 主人公の年齢（以下の形式をかならず使用してください）：
    - 12歳
    - 14歳~16歳
    - 高校生
    - 大学生
    - 80代の場合は、80歳~89歳

    4. 主な舞台となる場所（具体的な都市名や地名を1つ。例：東京、京都、札幌など）
    ※架空の場所の場合は「架空」と記載
    ※場所が特定できない場合は「不明」と記載

    5. 要約
    一行程度で、本の内容を要約してください。
    
    フォーマット：
    ジャンル：[上記の選択肢から1つ]
    季節：[上記の選択肢から1つ]
    主人公の年齢：[抽出結果]
    場所：[具体的な都市名/架空/不明]
    本の要約：[本の要約]
    
    文章:
    {text}
    """

    max_retries = 3  # 最大リトライ回数
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            if not response.text:
                print(f"警告: 応答が空でした。再試行 {attempt + 1}/{max_retries}")
                time.sleep(2)  # 2秒待機
                continue

            output_text = response.text.strip()
            features = {}
            for line in output_text.split('\n'):
                if '：' in line:
                    key, value = line.split('：', 1)
                    features[key.strip()] = value.strip()
            return features

        except Exception as e:
            print(f"エラー（試行 {attempt + 1}/{max_retries}）: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # 2秒待機
            else:
                return {"error": str(e)}

def process_csv(input_file: str, output_file: str = "book_list06.csv"):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{input_file}' が見つかりません。")
        return

    wikipedia_info_list = df['Wikipedia情報'].tolist()
    all_features = []
    
    for i, info in enumerate(wikipedia_info_list):
        # Wikipedia情報が空の場合はスキップ
        if pd.isna(info) or info == '' or info == '{}':
            print(f"スキップ: {i+1}行目 - Wikipedia情報が空です")
            all_features.append({})
            continue
            
        print(f"処理中: {i+1}/{len(wikipedia_info_list)}")
        try:
            text = json.loads(info).get('概要', '')
            if not text:  # 概要が空の場合もスキップ
                print(f"スキップ: {i+1}行目 - 概要情報が空です")
                all_features.append({})
                continue
                
            features = extract_book_features(text)
            all_features.append(features)
        except json.JSONDecodeError:
            print(f"スキップ: {i+1}行目 - JSONの解析に失敗しました")
            all_features.append({})
            continue
            
        time.sleep(1)  # 1秒待機

    # 結果の保存
    df['ジャンル'] = [features.get('ジャンル', '') for features in all_features]
    df['季節'] = [features.get('季節', '') for features in all_features]
    df['主人公の年齢'] = [features.get('主人公の年齢', '') for features in all_features]
    df['場所'] = [features.get('場所', '') for features in all_features]
    df['本の要約'] = [features.get('本の要約', '') for features in all_features]
    df['LLM処理エラー'] = [features.get('error', '') for features in all_features]

    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\nCSVファイル '{output_file}' に保存しました。")

def main():
    process_csv("book_list05.csv")

if __name__ == "__main__":
    main()