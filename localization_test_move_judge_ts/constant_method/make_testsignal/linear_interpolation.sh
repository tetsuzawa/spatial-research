#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ######################################################################
# 線形補間(5°間隔=>1°間隔)
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################

# ファイルの上書き防止 && エラーが起きたら停止 && 変数の空文字列防止
set -Ceu

if [ $# -ne 1 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: bash linear_interpolation.sh SUBJECT_DIR\e[m \n\n"
  exit 1
fi

SUBJECT_DIR=$1

NUM_CPU_CORE=4

clear
echo "###################################################################"
echo "                      Linear interpolating ...                     "
echo "###################################################################"

(
for LR in L R; do
  for Angle in `seq 0 50 3550`; do
    for i in `seq 1 9`; do
      echo "${SUBJECT_DIR}/SLTF/SLTF_${Angle}_${LR}.DDB ${SUBJECT_DIR}/SLTF/SLTF_$(((Angle+50)%3600))_${LR}.DDB 0.$((10-i)) ${SUBJECT_DIR}/SLTF/SLTF_$((Angle+i*10/2))_${LR}.DDB"
    done
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} linear_inpo_hrir_using_ATD
