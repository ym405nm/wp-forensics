# WordPress セキュリティ事故調査用ツール

## これは何？

ご自身が管理されているWordPressのサイトが何らかのセキュリティ事故に巻き込まれたとき、その影響度をチェックします。

CUI環境でWordPressを設定している場合に使用できます。

主な機能

* 改ざんチェックツール（公開されている公式サイトから差分を検出する）
* アップロードディレクトリの調査（アップロードディレクトリにバイナリファイルやテキストファイルが置かれていなかどうか調査する）

## 作成した経緯

セキュリティツール系 Advent Calendar 2018 ( https://adventar.org/calendars/2968 )　の 12/17 分の記事として作成しました。

WordPressのセキュリティ対策は様々なものがありますが、被害を受けているサイトはこのような対策をとっているものが少なく、
被害を受けてからの発覚が遅れて状況把握が難しいことがありました。

本ツールでは、簡易的な状況把握をすばやく行い、インシデント対応の初期調査などに使用するために開発しました。

## 使い方

引数に既存のWordPressディレクトリを指定して実行することで調査が可能です。

```
$ ./wp_forensics.py {WordPressのディレクトリ}
```

### アウトプットイメージ

```
WordPress is found : ver -> 4.9.8
Download WordPress...
Success
Extract WordPress...

Added File(s)...
hacked.txt

Modifed File(s)...
wp-includes/functions.php

Unknown File(s)...
2018/12/b.png

```

こちらの出力結果から、「hacked.txt」が追加されている、「wp-includes/functions.phpのファイルが変更されている」
「アップロードディレクトリの2018/12/b.png」が予期していないファイル形式であることがわかります。

このため、これらのファイルが元々運用上必要なものか、意図して変更したものかを調査する必要があります。

## その他

Special Thanks : @junk_coken (調査・開発などでご協力いただきました)

WordPress のセキュリティ対策などはこちらから楽しく学べます（宣伝）

https://secure-brigade.booth.pm/items/1042809

