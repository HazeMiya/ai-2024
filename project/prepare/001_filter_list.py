import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('book_list01.csv')

# 不要なカラムを削除
columns_to_drop = ['受賞者名', '刊行作名', '複数受賞', '発表日', '並べ順日付']
df = df.drop(columns=columns_to_drop)

# カラム名の変更
df = df.rename(columns={'一番新しいkey': '賞名'})

# "候補"と"該当"が含まれる行を削除
df = df[~df['賞名'].str.contains('候補|該当', na=False)]

# 新しいCSVファイルとして保存
df.to_csv('book_list02.csv', index=False, encoding='utf-8')
