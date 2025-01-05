# ai-2024

## 環境セットアップ

```
cd prepare
docker-compose build
docker-compose up -d
```

立ち上げたら[localhost:8000/docs](http://localhost:8000/docs)にアクセスすると今回使用するFastAPIの使用方法が閲覧できる。

## pythonコンテナに関して
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
