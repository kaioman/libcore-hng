# リリース作業

testPyPI、PyPIへパッケージをアップロードする

## 準備

testPyPI、PyPIへそれぞれログインし、Trusted Publisherを追加する

(1)
左側にある「あなたのアカウント」内のPublishingをクリックする

(2)
ページ下部にて、Trusted Publisherを追加する場所をタブで選択する。(今回はGitHubを選択)

(3)
必要項目を入力する

PyPI Project Name：パッケージ名を入力する(libcore-hng)
Owner：GitHubアカウント名を入力する
Repository name：リポジトリ名を入力する(libcore-hng)
Workflow name：ワークフローファイル名を指定する(release.yml)
Environment name：省略可

(4)
Addボタンをクリックする

## リリース手順

以下のコマンドを実行する

```shell
$.\env\Scripts\tbump <バージョン番号> --no-push
```

バージョン番号例：2.0.3
コマンドを実行するとpyproject.tomlのversionが自動で書き換えてコミットまで実施する
--no-pushを指定しない場合はversionの書き換え⇒コミットまで実施しプッシュ待ちの
状態となる
