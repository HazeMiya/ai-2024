#================================================================
# リストのフィルタリングスクリプト
#================================================================
# 概要
#   - CSVファイルを読み込む
#   - 特定の文字列を含む行を削除
#   - 特定のカラムを削除
#   - 特定の賞名を含む行を抽出
#   - 重複を処理
#   - カラム名を変更
#   - 新しいCSVファイルとして保存
#
# 使用方法
#   - $ docker-compose up -d
#   - $ docker-compose exec <コンテナ名> bash
#   - $ python3 001_filter_list.py
#================================================================

import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('book_list01.csv')

# "候補"と"該当"と"高校生"が含まれる行を削除 
df = df[~df['賞タイトル'].str.contains('高校生', na=False)]
df = df[~df['受賞・最終候補作'].str.contains('該当', na=False)]
df = df[~df['賞タイプ'].str.contains('候補', na=False)]

# 指定されたカラムを削除
columns_to_drop = ['年', '賞', '出版', 'key', '追加日時', '発表日', '複数受賞', '並べ順日付', '賞タイプ']
df = df.drop(columns=columns_to_drop)

# 指定された賞名を含む行を抽出
mask = (
    df['賞タイトル'].str.contains('直木賞') |
    df['賞タイトル'].str.contains('芥川賞') |
    df['賞タイトル'].str.contains('本屋大賞') |
    df['賞タイトル'].str.contains('江戸川乱歩賞') |
    df['賞タイトル'].str.contains('山本周五郎賞') |
    df['賞タイトル'].str.contains('このミステリーがすごい！')
)
df = df[mask]

# カラム名の変更
df = df.rename(columns={'受賞・最終候補作': '受賞作'})

# 重複を処理する
# 作品ごとにグループ化して賞をまとめる
grouped_df = df.groupby('受賞作').agg({
    '賞タイトル': lambda x: ' | '.join(sorted(set(x))),  # 重複を除去して賞をパイプで結合
    '著者': 'first',  # 著者は同じはずなので最初の値を使用
    '著者__受賞・最終候補作': 'first',
    'ISBN10': 'first',
    'calil': 'first',
    'ImageURL': 'first'
}).reset_index()

# カラム順序を整理
column_order = [
    '受賞作',
    '著者',
    '賞タイトル',  # 結合された賞情報
    '著者__受賞・最終候補作',
    'ISBN10',
    'calil',
    'ImageURL'
]
grouped_df = grouped_df[column_order]

# 新しいCSVファイルとして保存
grouped_df.to_csv('book_list02.csv', index=False, encoding='utf-8')

print("データ処理が完了しました。'book_list02.csv'として保存されました。")