import pandas as pd
import requests
import time
import json

def get_coordinates(location):
    """
    国土地理院APIを使用して場所の緯度経度を取得する
    
    Args:
        location (str): 場所の名前
    
    Returns:
        tuple: (緯度, 経度) もしくは取得失敗時は (None, None)
    """
    if pd.isna(location):
        return None, None
        
    # APIのベースURL
    base_url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    
    try:
        # APIリクエストパラメータ
        params = {
            "q": location
        }
        
        # APIリクエスト実行
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # レスポンスをJSONとしてパース
        results = response.json()
        
        # 結果が存在する場合は最初の結果の緯度経度を返す
        if results and len(results) > 0:
            # 国土地理院APIは [経度, 緯度] の順で返すので注意
            longitude, latitude = results[0]["geometry"]["coordinates"]
            return latitude, longitude
            
        return None, None
        
    except Exception as e:
        print(f"Error getting coordinates for {location}: {str(e)}")
        return None, None

def main():
    print("地理情報変換処理を開始します...")
    
    # CSVファイルを読み込む
    df = pd.read_csv('book_list06.csv')
    total_rows = len(df)
    processed_rows = 0
    skipped_rows = 0
    
    print(f"総処理件数: {total_rows}件")
    
    # 緯度・経度を格納する新しい列を作成
    df['latitude'] = None
    df['longitude'] = None
    
    # 各場所に対して緯度経度を取得
    for idx, row in df.iterrows():
        location = row['場所']
        
        # 場所が空白または不明の場合はスキップ
        if pd.isna(location) or location == '不明':
            print(f"スキップ: {row['受賞作']} - 場所情報なし")
            skipped_rows += 1
            continue
            
        print(f"処理中 ({processed_rows + 1}/{total_rows}): {location}")
        latitude, longitude = get_coordinates(location)
        
        if latitude and longitude:
            df.at[idx, 'latitude'] = latitude
            df.at[idx, 'longitude'] = longitude
            print(f"✓ 成功: {location} -> 緯度: {latitude}, 経度: {longitude}")
        else:
            print(f"× 失敗: {location} - 座標を取得できませんでした")
            
        processed_rows += 1
        
        # APIの負荷を考慮して1秒待機
        time.sleep(1)
    
    # 結果を新しいCSVファイルに保存
    df.to_csv('book_list07.csv', index=False, encoding='utf-8')
    
    print("\n処理完了!")
    print(f"総件数: {total_rows}")
    print(f"処理件数: {processed_rows}")
    print(f"スキップ件数: {skipped_rows}")
    print(f"結果を book_list07.csv に保存しました")

if __name__ == "__main__":
    main()