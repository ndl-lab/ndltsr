# NDLTSR (NDL Table Structure Recognition)

資料画像に含まれる表の構造を認識するプログラムを公開しています。

座標付きのOCRテキストデータと組み合わせることで表中に含まれるテキストデータを構造化する用途に利用できます。

[参考（外部リンク）：次世代デジタルライブラリーへの新機能（表の構造化）の追加及び新機能のソースコード及びデータセットの公開について](https://lab.ndl.go.jp/news/2023/2023-12-05)

本プログラムにより、国立国会図書館が公開している[NDLTableSet](https://github.com/ndl-lab/ndltableset)を学習した機械学習モデルによる表構造の推論を行えるほか、独自のデータセットによる再学習を行うことが可能です。

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


## ライセンス情報

このリポジトリは、Apache 2.0ライセンスで公開されている[LORE-TSR](https://github.com/AlibabaResearch/AdvancedLiterateMachinery/tree/main/DocumentUnderstanding/LORE-TSR)(外部リンク)をもとに、国立国会図書館がソースコードを修正及び追加しています。

[src/lib](src/lib)以下のディレクトリ、[src/_init_paths.py](src/_init_paths.py)及び[src/main.py](src/main.py)については、原則的にLORE-TSRのソースコードを利用していますが、
[src/lib/detectors/base_detector.py](src/lib/detectors/base_detector.py)及び[src/lib/opts.py](src/lib/opts.py)については、ソースコードの修正を行っています。

当館が追加したソースコードについてはCC BY 4.0ライセンスで、その他の部分についてはオリジナルのLORE-TSRのライセンスに従ってください。

オリジナルのLORE-TSRのライセンス等の情報は[LICENSE_original.md](LICENSE_original.md)、[NOTICE_original](NOTICE_original)及び[README_original.md](README_original.md)を参照してください。
