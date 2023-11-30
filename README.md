# NDLTSR (NDL Table Structure Recognition)

資料画像に含まれる表の構造を認識するプログラムを公開しています。

座標付きのOCRテキストデータと組み合わせることで表中に含まれるテキストデータを構造化する用途に利用できます。

[参考（外部リンク）：次世代デジタルライブラリーへの新機能（表の構造化）の追加及び新機能のソースコード及びデータセットの公開について](https://lab.ndl.go.jp/news/2023/2023-12-05)

本プログラムにより、国立国会図書館が公開している[NDLTableSet](https://github.com/ndl-lab/ndltableset)を学習した機械学習モデルによる表構造の推論を行えるほか、[LORE-TSR](https://github.com/AlibabaResearch/AdvancedLiterateMachinery/tree/main/DocumentUnderstanding/LORE-TSR)(外部リンク)と同様の方法により別途利用者が用意したデータセットによる再学習を行うことが可能です。

**注意**

本プログラムが推論できるのは、表の構造情報（各セルの矩形座標及びセル間の関係性を表す数値情報）であるので、プログラム単体でOCR処理プログラムとして利用することはできません。

次世代デジタルライブラリーの機能と同様の処理を行うためには、別途座標付きテキストデータを出力するOCR処理プログラムが必要です。

## 環境構築

### 1. リポジトリのクローン
```
git clone https://github.com/ndl-lab/ndltsr
```
### 2. ホストマシンのNVIDIA Driverのアップデート
コンテナ内でCUDA 11.8を利用します。

ホストマシンのNVIDIA Driverが

Linuxの場合: 450.80.02以上 

Windowsの場合:452.39以上

のバージョンを満たさない場合は、ご利用のGPUに対応するドライバの更新を行ってください。

（参考情報）

以下のホストマシン環境（AWS g5g.xlargeインスタンス）上で動作確認を行っています。

OS: 20.04.3 LTS

GPU: NVIDIA T4G

NVIDIA Driver: 470.82.01

Docker version： 20.10.11

### 3. dockerのインストール
https://docs.docker.com/engine/install/
に従って、OS及びディストリビューションにあった方法でdockerをインストールしてください。

### 4. dockerコンテナのビルドと起動
ndltsrディレクトリ下で次のように実行するとコンテナが起動します。
```
sh docker/dockerbuild.sh
sh docker/run_docker.sh
```

## 利用方法
コンテナ起動後、http://127.0.0.1:8080/invocations
に次のように画像をPOSTすることで推定された表構造の情報を得ることができます。
```
import urllib.request
import msgpack

data = {}
with open("tableimg.jpg", "rb") as fp:
    data["img"] = fp.read()
payload = msgpack.packb(data, use_bin_type=True)
headers = {
    "Content-Type": "application/x-msgpack",
}
req = urllib.request.Request(
        "http://127.0.0.1:8080/invocations",
    payload, headers
)

with urllib.request.urlopen(req) as res:
    print(res.read())
```
**返戻の形式**

次のjson形式です。
```
{ "logi":logi_list,
  "center":center_list}
```
* center_list：セル毎に推定した矩形座標を記述した4つの要素(x座標の最小値, y座標の最小値, x座標の最大値, y座標の最大値)を検出したセル数分持つリスト
* logi_list：セル毎に推定したセル間の関係情報を記述した4つの要素(列の開始位置, 列の終了位置, 行の開始位置, 行の終了位置)を検出したセル数分持つリスト

画像をPOSTして得た返戻と座標付きOCRテキストデータを組み合わせてHTMLやTSVのテーブルを得るサンプルコードについては[merge_sample.py](merge_sample.py)をご覧ください。

## ライセンス情報
国立国会図書館が新規に追加したソースコードについてはCC BY 4.0ライセンスとします。

なお、本プログラムはApache 2.0ライセンスで公開されている[LORE-TSR](https://github.com/AlibabaResearch/AdvancedLiterateMachinery/tree/main/DocumentUnderstanding/LORE-TSR)(外部リンク)を部分的に利用します。

[src/lib](src/lib)以下のディレクトリ、[src/_init_paths.py](src/_init_paths.py)及び[src/main.py](src/main.py)について、原則的にLORE-TSRのオリジナルのソースコードを複製していますが、
[src/lib/detectors/base_detector.py](src/lib/detectors/base_detector.py)及び[src/lib/opts.py](src/lib/opts.py)については、一部ソースコードの修正を行いました。

オリジナルのLORE-TSRのライセンス等の情報は[LICENSE_original.md](LICENSE_original.md)、[NOTICE_original](NOTICE_original)及び[README_original.md](README_original.md)を参照してください。
