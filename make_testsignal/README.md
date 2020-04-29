# make_testsignal

2019 年度 牧下の実験を恒常法から適応法に置き換えたものです。

## プログラムの依存

- make_testsignal_move_judge_all_msdv.sh
  - make_testsignal_move_judge0_msdv.sh
  - make_testsignal_move_judge45_msdv.sh
  - make_testsignal_move_judge90_msdv.sh
    - continuous_move_judge_dv.py

## 適応法

- 範囲は予備実験から考える
- 変数
  - width
  - velocity
  - start_position
- 右か左かで判定

## 回答数

### 恒常法の場合、

- 0, 45, 90 それぞれにおいて
  - width _ velocity _ direction = 5 _ 56 _ 2 = 50
- 1 セッション 50 \* 3 = 150
- 総数 10 セッション \* 150 = 1500

### 適応法の場合

- 前提として収束の度合いによって回数が変わる
- まず width から求める。
- width は予備実験・先行研究から正答率が TODO%のやつを使う
- 強化学習？
- 最急降下法？
- 極小値が一つしか無いと仮定すれば、width, velocity それぞれの最適値から関数を予測できる。
- 一方で、極小値が複数存在すると仮定すれば、

# 質問したいこと

- 対数間隔にするのか
