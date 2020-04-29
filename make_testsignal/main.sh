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

if [ $# -ne 2 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: SUBJECT mode(0/1)\e[m \n\n"
  exit
fi

SUBJECT_DIR=$1
LSTF_DIR=$2

mkdir -p ${SUBJECT_DIR}/TS ${SUBJECT_DIR}/ANSWER

echo "Running make_SLTF.sh ..."
bash make_SLTF.sh ${SUBJECT_DIR} ${LSTF_DIR} # HRTFとSLTFの生成
echo "Running liner_interpolation.sh ..."
bash liner_interpolation.sh ${SUBJECT_DIR} # SLTFの線形補間
echo "Running make_testsignal_move_judge0_msdv.sh ..."
bash make_testsignal_move_judge0_msdv.sh ${SUBJECT_DIR} # 移動音の生成
echo "Running make_testsignal_move_judge45_msdv.sh ..."
bash make_testsignal_move_judge45_msdv.sh ${SUBJECT_DIR} # 移動音の生成
echo "Running make_testsignal_move_judge90_msdv.sh ..."
bash make_testsignal_move_judge90_msdv.sh ${SUBJECT_DIR} # 移動音の生成

echo "completed!!"