TODO memo

# TODO ffmpegができることを調べる

インストール方法はhttps://www.deb-multimedia.org/をみればわかった

```
ffmpeg -i 'https://rpaa.smartstream.ne.jp/medialist?session=f9LSrJhnxmaobQW4avKax3&_=1573451907710' \
     -headers 'Connection: keep-alive'\
     -headers 'Origin: http://radiko.jp' \
     -headers 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36' \
     -headers 'Accept: */*' \
     -headers 'Sec-Fetch-Site: cross-site' \
     -headers 'Sec-Fetch-Mode: cors' \
     -headers 'Referer: http://radiko.jp/' \
     -headers 'Accept-Encoding: gzip, deflate, br'\
     -headers 'Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7' \
     radio.mp3
これはなんか1:40ぐらい録音できた
```

# TODO radikoにブラウザでアクセスしたときの流れをみる
auth1, auth2で認証する
```
curl 'https://rpaa.smartstream.ne.jp/so/playlist.m3u8?station_id=TBS&l=15&lsid=34622035824246322054536239676708224608&type=b' -X OPTIONS -H 'Connection: keep-alive' -H 'Access-Control-Request-Method: GET' -H 'Origin: http://radiko.jp' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36' -H 'Access-Control-Request-Headers: x-radiko-areaid,x-radiko-authtoken' -H 'Accept: */*' -H 'Sec-Fetch-Site: cross-site' -H 'Sec-Fetch-Mode: cors' -H 'Referer: http://radiko.jp/' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7' --compressed
# curl 'https://rpaa.smartstream.ne.jp/so/playlist.m3u8?station_id=TBS&l=15&lsid=34622035824246322054536239676708224608&type=b' -H 'Connection: keep-alive' -H 'X-Radiko-AuthToken: 9vSv7OaQab1mEni8sVePww' -H 'Origin: http://radiko.jp' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36' -H 'X-Radiko-AreaId: JP13' -H 'Accept: */*' -H 'Sec-Fetch-Site: cross-site' -H 'Sec-Fetch-Mode: cors' -H 'Referer: http://radiko.jp/' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7' --compressed
# curl 'https://rpaa.smartstream.ne.jp/medialist?session=ZTSZ9GNPxgmMupdJ3BN9hK&_=1573453321852' -H 'Connection: keep-alive' -H 'Origin: http://radiko.jp' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36' -H 'Accept: */*' -H 'Sec-Fetch-Site: cross-site' -H 'Sec-Fetch-Mode: cors' -H 'Referer: http://radiko.jp/' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7' --compressed
```

playlist.m3u8にstation_idを指定してなんかをとる
medialistから音声ファイルのURLをとって、

# TODO rtmpdumpができることを調べる

 RTMPでやりとりしている音声動画データをflvファイルで取得する（Adobe Flashが標準で利用するファイル形式の一つで、動画データの格納形式を定めたもの。）

# TODO radiko 簡易スクリプトをコンテナで動かして録音再生する
rtmpdumpはflv用、今は使えるかもしれないけど、radikoは今aacファイルで配布している。aacは音声圧縮フォーマットととして決められている。たぶんだけど、adobe flash必須でないようにオープンなフォーマットにしたのかなと。これはchromeのdeveloper toolでhttps://rpaa.smartstream.ne.jp/medialist?session=f9LSrJhnxmaobQW4avKax3&_=1573451907710 とmedialistと含まれてURLのレスポンスからわかった。response headerはapplication/x-mpegURLとなっている。
なので簡易スクリプトは今は動くかもしれないけど、2020年末にflashが終わることを考えるとそのうち使えなくなる →しばらく使いたいし、aacでファイルは配布されているから、つくろう

# TODO pythonでradiko録音再生する


# TODO gcloudコマンドでgoogle driveにアップロードをする
# TODO pythonでgoogle driveにアップロードをする
# TODO pythonで録音+アップロードをする
# TODO ローカルからコンテナ起動して録音+アップロードする
