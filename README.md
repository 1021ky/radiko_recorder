# radiko_recorder

Radikoの番組を録音するpythonスクリプトと実行用のdockerコンテナ。

## Description

### radikoの録音をするpythonスクリプト
実行時に環境変数でエリアIDを、スクリプトへの引数でラジオ局と番組名（ファイル保存時に使用される）、録音時間を指定する。
例：東京でTBSのhoge番組を10分録音する場合。
```
RADIKO_AREA_ID=JP13 python src/app.py TBS hoge 10
```

### dockerコンテナ

imageをビルドして実行すると8080ポートでHTTPリクエストを受け付けるようになる。
例：TBSのhoge番組を10分録音する場合。
```
curl '127.0.0.1:8080/record?station=TBS&program=hoge&rtime=10'
```
エリアはimageビルド時に環境変数RADIKO_AREA_IDで指定されている。必要に応じて変えてビルドする。


## Author

[keisuke yamanaka](https://github.com/1012ky)


