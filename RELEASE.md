# リリース作業

testPyPI、PyPIへパッケージをアップロードする

## 準備

### testPyPI、PyPIへそれぞれログインし、Trusted Publisherを追加する

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

### GitHubリポジトリにworkflowを作成する

(1)
GitHubにログインしてリポジトリを開き、ブランチをmainに変更する

(2)
Actionsをクリックする

(3)
Choose a workflowでPublish Python PackageのConfigureボタンをクリックする

(4)
workflowのファイル名を「release.yml」に変更し、以下の内容をEdit部に張り付ける

```yml
name: Publish package to PyPI

on:
    push:
        tags:
            - 'v*.*.*'  # バージョンタグにマッチするパターン

jobs:
    publish-testpypi:
        runs-on: ubuntu-latest
        permissions:
            id-token: write   # OIDCトークン発行に必要
            contents: read

        steps:
            - uses: actions/checkout@v4
            - uses: actions/setup-python@v5
              with:
                    python-version: '3.11.9'
            - run: pip install build
            - run: python -m build
            - uses: pypa/gh-action-pypi-publish@release/v1
              with:
                    repository-url: https://test.pypi.org/legacy/
    publish-pypi:
        runs-on: ubuntu-latest
        needs: publish-testpypi
        permissions:
            id-token: write   # OIDCトークン発行に必要
            contents: read
        steps:
            - uses: actions/checkout@v4
            - uses: actions/setup-python@v5
              with:
                python-version: '3.11.9'
            - run: pip install build
            - run: python -m build
            - uses: pypa/gh-action-pypi-publish@release/v1
              with:
                repository-url: https://upload.pypi.org/legacy/
```

(5)
右上の「Commit changes」ボタンをクリックする

(6)
Commit messageは自動で挿入されるので、「Commit changes」ボタンをクリックする（release.ymlがmainブランチにプッシュされる）

### ホストにtbumpをインストールする

(1)
以下のコマンドを実行する

```shell
$pip install tbump
```

## リリース手順

■pushまで自動で実施する手順

(1)
tbumpを実行する

```shell
$tbump <バージョン番号>
```

■pushせずにローカルリポジトリまでの変更に留め、タグを手動でpushする手順

(1)
tbumpを実行する

```shell
$tbump <バージョン番号> --no-push
```

バージョン番号例：2.0.3
コマンドを実行するとpyproject.tomlのversionが自動で書き換えてコミットまで実施する
--no-pushを指定しない場合はversionの書き換え⇒コミットまで実施しプッシュ待ちの
状態となる

(2)
タグをpushする

```shell
$git push origin v<バージョン番号>
```
