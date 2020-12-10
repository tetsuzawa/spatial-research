#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ######################################################################
# 試験音作成
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################
# bash main (subject_directory : ex. ../SUBJECTS/TETSU) (LSTF_directory : ../LSTF)
# ######################################################################

# ファイルの上書き防止 && エラーが起きたら停止 && 変数の空文字列防止
set -Ceu

if [ $# -ne 3 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: bash main.sh SUBJECT_DIR LSTF_DIR OUT_SUBJECT_DIR\e[m \n\n"
  exit 1
fi

SUBJECT_DIR=$1
LSTF_DIR=$2
OUT_SUBJECT_DIR=$3

echo "Running make_SLTF.sh ..."
bash make_SLTF.sh ${SUBJECT_DIR} ${LSTF_DIR} ${OUT_SUBJECT_DIR} # HRTFとSLTFの生成
echo "Running liner_interpolation.sh ..."
bash linear_interpolation.sh ${OUT_SUBJECT_DIR} # SLTFの線形補間
#echo "Running make_testsignal_move_judge0_msdv.sh ..."
#bash make_testsignal_move_judge0_msdv.sh ${SUBJECT_DIR} ${OUT_SUBJECT_DIR} # 移動音の生成
echo "Running make_testsignal_move_judge450_msdv.sh ..."
bash make_testsignal_move_judge450_msdv.sh ${SUBJECT_DIR} ${OUT_SUBJECT_DIR} # 移動音の生成
#echo "Running make_testsignal_move_judge900_msdv.sh ..."
#bash make_testsignal_move_judge900_msdv.sh ${SUBJECT_DIR} ${OUT_SUBJECT_DIR} # 移動音の生成

echo ""
echo "$((SECONDS/60))min $((SECONDS%60))sec elapsed"
echo ""
echo "completed!!"
