# SRW Alpha ROM Editor — スーパーロボット大戦α ROM エディター

[![Python](https://img.shields.io/badge/Python-≥3.14-blue?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython-6/)
[![PlayStation](https://img.shields.io/badge/PlayStation-1-003791?logo=playstation&logoColor=white&style=flat&labelColor=013243)](https://www.playstation.com/)
[![Windows](https://img.shields.io/badge/Windows-10%2B-00A4EF?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iODgiIHdpZHRoPSI4OCIgeG1sbnM6dj0iaHR0cHM6Ly92ZWN0YS5pby9uYW5vIj48cGF0aCBkPSJNMCAxMi40MDJsMzUuNjg3LTQuODYuMDE2IDM0LjQyMy0zNS42Ny4yMDN6bTM1LjY3IDMzLjUyOWwuMDI4IDM0LjQ1M0wuMDI4IDc1LjQ4LjAyNiA0NS43em00LjMyNi0zOS4wMjVMODcuMzE0IDB2NDEuNTI3bC00Ny4zMTguMzc2em00Ny4zMjkgMzkuMzQ5bC0uMDExIDQxLjM0LTQ3LjMxOC02LjY3OC0uMDY2LTM0LjczOXoiIGZpbGw9IiMwMGFkZWYiLz48L3N2Zz4=&logoColor=white&style=flat&labelColor=013243)](https://www.microsoft.com/windows)
[![GitHub Release](https://img.shields.io/github/v/release/hamano0813/SRW_Alpha?label=Release&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDI0IDEwMjQiPjxwYXRoIGQ9Ik01MTIgNTEybS01MTIgMGE1MTIgNTEyIDAgMSAwIDEwMjQgMCA1MTIgNTEyIDAgMSAwLTEwMjQgMFoiIGZpbGw9IiNGQTg5MTkiPjwvcGF0aD48cGF0aCBkPSJNNzk4LjcyIDM3MC4zMzZjLTIwLjczNiAxOS41Mi00MC42NCA0My4yLTU5LjYxNiA3MS4xMDQtMi41Ni0zNS41Mi05LjA1Ni02NS42LTE5LjQyNC05MC4xNDQgMTMuODI0LTE2Ljg5NiAyNy42NDgtMzEuNzEyIDQxLjQ3Mi00NC40MTYgOC42NCAxMS44NCAyMS4xMiAzMi45OTIgMzcuNTY4IDYzLjQ1Nm0tMTk1LjYxNiAyNTAuMDhjMCAyMS4xODQgNS4xODQgNDUuMjggMTUuNTUyIDcyLjM1MmwyLjU2IDguODk2Yy0zNy4xMiAzOS44MDgtODMuMzI4IDYxLjc2LTEzOC41NiA2Ni4wMTZhMTk3Ljc2IDE5Ny43NiAwIDAgMS04Ny40NTYtMTUuMjMyIDIxNS4xMzYgMjE1LjEzNiAwIDAgMS03NS43NzYtNTIuMDY0Yy0yMy4yOTYtMjUuMzc2LTQwLjM1Mi01NS42MTYtNTEuMTY4LTkwLjc1Mi0xMC43ODQtMzUuMTA0LTE0LjQ2NC03My40MDgtMTEuMDA4LTExNC44OCA2LjkxMi02MC4wNjQgMjguNzA0LTExMS40ODggNjUuNDQtMTU0LjI0IDM2LjY3Mi00Mi43MiA4MC45Ni02OS4xODQgMTMyLjc2OC03OS4zNiA1NC40LTExLjg0IDEwNy41Mi0zLjM2IDE1OS4zMjggMjUuNDA4IDI3LjYxNiAxNi45NiA0OC43NjggMzguNzIgNjMuNDU2IDY1LjM3NiAxNC42ODggMjYuNjU2IDIzLjc0NCA1OC4yMDggMjcuMiA5NC41OTIgMS43MjggOS4yOCAyLjE0NCAyMy4yNjQgMS4yOCA0MS44ODhsLTEuMjggNTkuNjQ4YzAgMzEuMzI4IDEuNzI4IDU1LjQ1NiA1LjE4NCA3Mi4zNTIgNC4zMiAyNC41NzYgMTMuMzc2IDQxLjkyIDI3LjIgNTIuMDY0IDEwLjM2OCA4LjQ0OCAyMi44OCAxMi4yNTYgMzcuNTY4IDExLjQyNCAxMS4yIDAgMTkuNDI0LTIuNTYgMjQuNjA4LTcuNjE2LTExLjIzMiAyNC41NDQtMjUuNDcyIDQyLjMwNC00Mi43NTIgNTMuMzEyLTE0LjY4OCA5LjMxMi0zMC4yNCAxMy4xMi00Ni42MjQgMTEuNDI0LTEzLjgyNC0xLjY5Ni0yNS4wNTYtNi4zMzYtMzMuNjY0LTEzLjk1Mi0xNC43Mi0xMy41MzYtMjUuOTItMzguNTI4LTMzLjY5Ni03NC45MTItNy43NzYtMzQuNjg4LTExLjY0OC03NC4wNDgtMTEuNjQ4LTExOC4wOHYtMTMuOTUyYzAtMjguNzM2LTAuODY0LTUwLjc1Mi0yLjU5Mi02NS45ODQtMi41OTItMjUuNDA4LTguMjI0LTQ2LjMzNi0xNi44MzItNjIuODQ4YTEwNS4zNzYgMTA1LjM3NiAwIDAgMC0zNi4yODgtNDBjLTI2Ljc4NC0xNC4zNjgtNTMuNTM2LTIxLjEyLTgwLjMyLTIwLjI4OGExNDAuNjA4IDE0MC42MDggMCAwIDAtNzUuMTA0IDI0LjczNiAxOTQuNTI4IDE5NC41MjggMCAwIDAtNTguMzA0IDYyLjIwOCAyMDYuNzIgMjA2LjcyIDAgMCAwLTI4LjQ4IDg0LjQxNmMtNi4wOCA2MS43NiA4LjE5MiAxMTAuODggNDIuNzIgMTQ3LjI2NCAxMy44MjQgMTQuNCAyOS43OTIgMjUuMzc2IDQ3LjkzNiAzMi45OTIgMTguMTQ0IDcuNjE2IDM1Ljg0IDExLjAwOCA1My4xMiAxMC4xNDQgMjUuMDI0LTEuNjY0IDQ0LjY3Mi01LjY5NiA1OC45NDQtMTIuMDMyIDE0LjI0LTYuMzY4IDI4LjY3Mi0xNi43MDQgNDMuMzkyLTMxLjEwNCA2Ljg4LTYuNzg0IDE0LjY1Ni0xNi41MTIgMjMuMjk2LTI5LjIxNiIgZmlsbD0iI0ZGRkZGRiI+PC9wYXRoPjwvc3ZnPg==&style=flat&labelColor=013243)](https://github.com/hamano0813/SRW_Alpha/releases)


**PySide6** ベースの ROM 静的エディター。**PS 版『スーパーロボット大戦α』** 専用に設計

ゲーム内のユニット、パイロット、武器、テキスト、戦場設定、敵 AI、ストーリーブランチなどのデータ編集に対応。
現在は日本版のみ対応。中国語ローカライズ版はフォントの制約により未対応ですが、ゲームデータ自体は共通です。

---

## 機能一覧

### 実装済み

- **ユニットデータ編集** — パラメータ、地形適応、特殊能力、武装パラメータ、BGM、変形/分離、シリーズ
- **パイロットデータ編集** — 能力、地形適応、スキル、育成、シリーズ
- **シナリオテキスト編集** — ゲームステージ内のテキスト編集
- **イメージファイル解析** — ISO の展開と再構築
- **多言語UI** — English / 简体中文 / 日本語

### 計画中

- シナリオフロー編集 — ストーリーイベント、敵配置、AI
- スクリプトフロー編集 — 幕前・幕中・幕後の流れ
- ゲームパラメータ編集 — 改造幅、精神消費、チップ属性など
- 全角文字再描画 — ゲームフォントを再描画する機能

---

## ダウンロードと使用方法

[Releases](https://github.com/hamano0813/SRW_Alpha/releases) ページから最新のインストーラーをダウンロードし、インストール後すぐに使用できます。

---

## ROMの準備

1. 『スーパーロボット大戦α』日本版の PS1 ディスクイメージ（.bin/.cue）を用意
2. 設定画面で読み込み元と保存先の ROM ファイルパスを設定

編集に必要な各モジュールファイルは、エディターがキャッシュディレクトリに自動的に展開するため、手動での設定は不要です。

---

## 操作説明

> 編集は自己責任で行ってください。必ず異なるバージョンのファイルをバックアップしておいてください。

- **概要 > ROMを展開** — ROM をキャッシュファイルに展開し、エディターのディレクトリに保存
- **概要 > キャッシュを解析** — キャッシュファイルからゲームデータを解析し、編集機能を有効化
- **概要 > キャッシュを構築** — 編集済みデータをキャッシュファイルに書き戻し
- **概要 > ROMを再構築** — キャッシュファイルを設定した保存先パスに ROM ファイルとして再パッケージ
- **ユニット > ユニット名、ユニットデータ、変形/合体、換装システム、地形適応、特殊能力、乗換システム、BGM** — すべて編集可能
  - 変形：変形グループ番号によって決定。同一グループ番号のユニット間で相互変形可能。変形順序は変形番号で決定。最小グループ番号は1、上限は不明。番号範囲0-2、3段変形に対応。それ以上の変形は未テスト
  - 合体：2つのモードがあります
    - コアファイターモード：合体グループ番号0。ベースユニットのみ設定が必要で、コアファイター側の設定は不要。ベースユニットの合体数は1、コアファイターをコア機体として選択
    - パーツ合体モード：合体グループ番号によって決定。各パーツユニットごとに設定が必要。同一グループ番号のパーツが合体可能。合体順序は合体番号で決定。最小グループ番号1、上限不明。番号範囲0-4、5機合体に対応。別途ベースユニットにコア機体と合体数の設定が必要
  - 換装：ゲーム内で2つの換装システムのみ存在（V2ガンダムとヒュッケバインMK-Ⅲ）。勝手に変更しないでください
  - 地形：タイプと適応の2部分で構成。タイプは該当マップに出撃可能かどうかを決定。適応は移動力やその他の計算に影響
  - 特殊能力：ユニットに表示される能力と非表示の能力の両方を含む。チェックするだけ。選択しすぎによるフリーズは未検証
  - 乗換システム：チェックすると、同じシステムをチェックしたパイロットが乗り換え可能
  - BGM：ユニット戦闘時に切り替わるBGMを選択。一部のBGMには複数のバージョンがあるか、ミュージックプレイヤーに表示されない隠しBGMあり
- **ユニット > 武器 > 武器名、タイプ、攻撃力、属性、命中率、クリティカル率、消費、必要値、改造タイプ、改造追加武器、マップ兵器属性、地形適応** — すべて編集可能
  - タイプ：格闘/射撃を切り替え可能
  - 属性：P（移動後攻撃）可否、ビーム兵器かどうか、カット可能かなどを含む。誘導兵器はビットやファンネルを含む。分離はVガンダム系のBOTTOM ATTACK専用。突撃は推測項目で、Vガンダムの光の翼のみに使用。水中武器は陸上攻撃不可
  - 必要値：気力と技能レベルの要件を含む。技能レベルは0-3、それ以上のレベルは未定義
  - 改造タイプ：パラメータ編集（未実装）の4セットの改造設定に対応。攻撃力上昇幅と必要資金を含む
  - 改造追加：当該ユニットの1つの武器を改造完了時の隠し武器として追加可能。対象武器の隠しを解除するには、ここでの選択を解除するだけ
  - マップ兵器：3タイプ — 方向指定、自機中心、着弾指定。任意のタイプ選択時、マップ兵器の演出を選択可能。一部の演出はストーリー専用で武器の使用はない。エディターで範囲を制限してフリーズを防止
    - 方向指定：武器属性の射程は表示のみ。実際のダメージ範囲は右側で選択可能なマップ兵器範囲によって決定。爆導索は面積カスタムのため例示のみ
    - 自機中心：武器属性の遠射程でダメージ範囲を決定
    - 着弾指定：武器属性の遠射程で起爆中心点距離を決定。殺傷半径枠内の数値で起爆中心点からのダメージ範囲を決定。起爆中心点は1、最小有意数値は2
  - 地形適応：武器の地形適応
- **パイロット > パイロット名、フルネーム、パイロットデータ、性格、二回行動レベル、初期SP、気力グループ、精神コマンド、特殊スキル、乗換システム、レベル制スキル、地形適応** — すべて編集可能
  - 気力グループ：同じ数値のパイロットが同一気力グループとなり、互いに近づくことで隠し気力ボーナスを獲得
  - 精神コマンド：使用可能な精神と習得レベルの編集に対応
  - 特殊スキル：ゲーム内でレベルアップしないパイロットスキル。一部の隠しスキルを含む。王子・王女の用途は不明。エース・二回行動はパイロット画面のアイコンを直接点灯。主人公は全主人公キャラをマーク。AIは全雑魚と人造ボスをマーク — 機能は不明
  - 乗換システム：ユニットの乗換システムと同様。チェックすると同じオプションをチェックしたユニットに乗り換え可能
  - レベル制スキル：ニュータイプや聖戦士などのレベルアップ可能スキルと、習得レベルを定義可能
  - 地形：前述の通り
- **テキスト > 戦闘マップ内で使用されるすべてのシナリオテキストを編集可能。ステージの勝利/敗北条件、マップ上の選択肢テキスト、キャラクター会話などを含む
  - 右側に簡易検索フィルター機能、16進数シーケンス番号による位置指定機能、特定の発言者を選択してその発言のみをフィルター表示する機能を搭載

---

## 寄付

このプロジェクトは約5年にわたって続いています。以前のバージョンは書き上げた後に破棄しました — 主にプロジェクトが大きくなるにつれてリファクタリングが困難になり、当時の自分の技術力が追いつかなかったためで、ずっと悔やまれていました。

5年後の再開は完全にVIBE CODINGのおかげであり、自身の技術向上も相まって、ようやくこのエディターを少しずつ作り上げることができています。もちろん、まだ最終版ではありません — 徐々にさまざまな編集機能を追加しているところです。

このエディターが役に立ったなら、下のQRコードをスキャンしてAIの継続購入をサポートしていただけると幸いです。寄付は無条件で、追加機能や約束は一切ありません — 純粋な支援と励ましです。

</br>

<img src="res/bill.png" width="400" alt="QRコード">

---

## ライセンス

このプロジェクトは学習および研究目的でのみ提供されています。本ソフトウェアを使用する前に、『スーパーロボット大戦α』の正規コピーを所有していることを確認してください。
