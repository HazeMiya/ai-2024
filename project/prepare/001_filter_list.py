import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv('book_list01.csv')

# 不要なカラムを削除
columns_to_drop = ['受賞者名', '刊行作名', '複数受賞', '発表日', '並べ順日付']
df = df.drop(columns=columns_to_drop)

# カラム名の変更
df = df.rename(columns={'一番新しいkey': '賞名'})

# "候補"と"該当"と""高校生が含まれる行を削除
df = df[~df['賞名'].str.contains('候補|該当|高校生', na=False)]

# 指定された賞名を含む行を抽出
mask = (
    df['賞名'].str.contains('直木賞') |
    df['賞名'].str.contains('芥川賞') |
    df['賞名'].str.contains('本屋大賞') |
    df['賞名'].str.contains('江戸川乱歩賞') |
    df['賞名'].str.contains('山本周五郎賞') |
    df['賞名'].str.contains('このミステリーがすごい！')
)
df = df[mask]

# 新しいCSVファイルとして保存
df.to_csv('book_list02.csv', index=False, encoding='utf-8')