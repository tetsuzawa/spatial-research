#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ######################################################################
# 参照音作成用シェル
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################

# ファイルの上書き防止 && エラーが起きたら停止 && 変数の空文字列防止
set -Ceu

mkdir -p $1/TS
 End_Angle=90
 for LR in L R; do
   clear
   timeconvo $1/SLTF/SLTF_${End_Angle}_${LR}.DDB ../w4s.DSB /tmp/tmp_${LR}.DDB
   cutout_anyfile /tmp/tmp_${LR}.DDB 4001 $((320*48+4000)) $1/TS/TS_${End_Angle}_${LR}.DDB
 done

 clear
scaling_max_instant_amp input_files/input_file_tsp.dat 20000 ../$1/TS/ > /dev/null
for LR in L R; do
   cosine_windowing $1/TS/TS_${End_Angle}_${LR}.DDB 48 0 30 $1/TS/TS_${End_Angle}_${LR}.DSB
 done
 mono2LR $1/TS/TS_${End_Angle}_L.DSB $1/TS/TS_${End_Angle}_R.DSB $1/TS/TS_${End_Angle}.DSB
 rm $1/TS/TS_${End_Angle}_L.DSB $1/TS/TS_${End_Angle}_R.DSB