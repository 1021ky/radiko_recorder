# radiko_recorder
radikoの録音をするpythonスクリプト。実行時に環境変数でエリアIDを、スクリプトへの引数でラジオ局と番組名（ファイル保存時に使用される）、録音時間を指定する。
例：東京でTBSのhoge番組を10分録音する場合。
```
RADIKO_AREA_ID=JP13 python src/app.py TBS hoge 10
```
