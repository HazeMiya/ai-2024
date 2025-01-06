import pandas as pd
import json

def csv_to_json(csv_file, json_file):
    """
    CSVデータをJSONに変換する関数

    Args:
        csv_file (str): 入力CSVファイルのパス
        json_file (str): 出力JSONファイルのパス
    """
    # CSVファイルを読み込む
    df = pd.read_csv(csv_file)
    
    # 各行を辞書に変換
    data = []
    for index, row in df.iterrows():
        # 必須フィールドのみを抽出し、欠損値は空文字列に変換
        book_data = {
            "id": str(row.get('ISBN10', '')),
            "title": str(row.get('受賞作', '')),
            "author": str(row.get('著者', '')),
            "award": str(row.get('賞タイトル', '')),
            "location": str(row.get('場所', '')),
            "season": str(row.get('季節', '')),
            "genre": str(row.get('ジャンル', '')),
            "image": str(row.get('ImageURL', '')),
            "summary": str(row.get('本の要約', '')),
            "characters_age": str(row.get('主人公の年齢', '')),
            "characters": str(row.get('主人公の属性', '')),
            "latitude": float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
            "longitude": float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
        }
        
        # NaN値を空文字列に変換
        for key, value in book_data.items():
            if pd.isna(value):
                book_data[key] = ''
                
        data.append(book_data)

    # JSONファイルに出力（日本語文字化けを防ぐためにensure_ascii=Falseを指定）
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # CSVファイルと出力するJSONファイルのパスを指定
    csv_file = "book_list07.csv"
    json_file = "book_list.json"
    
    try:
        csv_to_json(csv_file, json_file)
        print(f"Successfully converted {csv_file} to {json_file}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")