import pandas as pd
import json

def validate_category(value, valid_categories):
    """
    値が有効なカテゴリに含まれているかチェックし、含まれていない場合はNoneを返す

    Args:
        value (str): チェックする値
        valid_categories (list): 有効なカテゴリのリスト
    """
    if pd.isna(value) or value.strip() == '' or value not in valid_categories:
        return None
    return value

def csv_to_json(csv_file, json_file):
    """
    CSVデータをJSONに変換する関数

    Args:
        csv_file (str): 入力CSVファイルのパス
        json_file (str): 出力JSONファイルのパス
    """
    # 有効なカテゴリを定義
    valid_genres = ['恋愛小説', 'ミステリー', 'SF', 'ファンタジー', '歴史小説', '文学', '青春小説', 'ホラー']
    valid_seasons = ['春', '夏', '秋', '冬']
    valid_characters = ['小学生', '中学生', '高校生', '大学生', '社会人', '主婦', '高齢者']

    # CSVファイルを読み込む
    df = pd.read_csv(csv_file)
    
    # 各行を辞書に変換
    data = []
    for index, row in df.iterrows():
        # ジャンル、季節、属性をバリデーション
        genre = validate_category(str(row.get('ジャンル', '')), valid_genres)
        season = validate_category(str(row.get('季節', '')), valid_seasons)
        characters = validate_category(str(row.get('主人公の属性', '')), valid_characters)

        # 必須フィールドのみを抽出
        book_data = {
            "id": str(row.get('ISBN10', '')),
            "title": str(row.get('受賞作', '')),
            "author": str(row.get('著者', '')),
            "award": str(row.get('賞タイトル', '')),
            "location": str(row.get('場所', '')),
            "season": 'nan' if season is None else season,
            "genre": 'nan' if genre is None else genre,
            "image": str(row.get('ImageURL', '')),
            "summary": str(row.get('本の要約', '')),
            "characters_age": str(row.get('主人公の年齢', '')),
            "characters": 'nan' if characters is None else characters,
            "latitude": float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
            "longitude": float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
        }
        
        # 各フィールドの値を処理（ジャンル、季節、属性以外）
        for key, value in book_data.items():
            # 特別な処理をする項目はスキップ
            if key in ['latitude', 'longitude', 'genre', 'season', 'characters']:
                continue
                
            # 空白、「不明」、「架空」を"nan"に変換
            if pd.isna(value) or value.strip() == '' or value == '不明' or value == '架空':
                book_data[key] = 'nan'
                
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