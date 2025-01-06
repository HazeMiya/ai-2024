# ai-2024

## 1. 環境セットアップ
### 1-1. 必要なソフトウェア
- docker

### 1-2. 環境構築手順
1. リポジトリのクローン
```
git clone https://github.com/HazeMiya/ai-2024

// ghqなら
ghq get https://github.com/HazeMiya/ai-2024
```

3. dockerコンテナ起動
```
cd prepare
docker-compose build
docker-compose up -d
```

立ち上げたら[localhost:8000/docs](http://localhost:8000/docs)にアクセスすると今回使用するFastAPIの使用方法が閲覧できる。

<br>

## 2. pythonコンテナに関して
`docker-compose up -d`でコンテナが立ち上がっていれば、以下のコマンドでコンテナに入ることができる。
```
docker exec -it <コンテナ名> bash
```

あとは以下のように実行コマンドを打つだけ
```
python3 001_filter_list.py

# 出るときは
exit;
```

## 3. フロー
`book_list01.csv`

⬇️ 001_filter_list.py（いい感じに変形）

`book_list02.csv`

⬇️ 002_add_ISBN.py（ISBNを追加）

`book_list03.csv`

⬇️ 追加漏れしたISBNを手動で追記

`book_list04.csv`

⬇️ 003_add_wiki.py（本の概要、あらすじを追記）

`book_list05.csv`（wikiにヒットしたのは全部で182件）

⬇️ 004_add_info.py（本の詳細（季節感、場所、主人公の年齢）を加える）←今ここ

`book_list06.csv`（ジャンル、季節、主人公の年齢、舞台、要約）

⬇️ 005_add_location.py（都市名から緯度経度を取得）

`book_list07.csv`

