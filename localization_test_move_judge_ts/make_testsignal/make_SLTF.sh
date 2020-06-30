#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ######################################################################
# SLTFとHRTFの生成
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################
# 参照ファイル名ECTFをRSTFに変更
# Shimizu Yuya (sy19807)
# 2019.6.6
# ######################################################################
# sh make_SLTF (subject_directory : ex. hogehoge/SHIMIZU) (LSTF_directory : hogehoge/LSTF)
# ######################################################################
# 処理を並列化
# Takizawa Tetsu (tt20805)
# 2020.5
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

NUM_CPU_CORE=4

mkdir -p ${SUBJECT_DIR}/HRTF ${SUBJECT_DIR}/SLTF

#--------------------------------- HRTFを生成 ---------------------------------#
clear
echo "####################################################################"
echo "                       Calculating HRTF ......    "
echo "####################################################################"

(
for LR in L R; do
  for Angle in `seq 0 5 355`; do
    speaker_num=$((Angle/5%18+1))
    echo "${SUBJECT_DIR}/SSTF/cSSTF_${Angle}_${LR}.DDB ${LSTF_DIR}/cinv_cLSTF_${speaker_num}.DDB ${SUBJECT_DIR}/HRTF/HRTF_${Angle}_${LR}.DDB"
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} timeconvo


#--------------------------------- SLTFを生成 ---------------------------------#
clear
echo "####################################################################"
echo "                       Calculating SLFT ......    "
echo "####################################################################"

(
for LR in L R; do
  for Angle in `seq 0 5 355`; do
    speaker_num=$((Angle/5%18+1))
    echo "${SUBJECT_DIR}/HRTF/HRTF_${Angle}_${LR}.DDB ${SUBJECT_DIR}/RSTF/cinv_cRSTF_${LR}.DDB ${SUBJECT_DIR}/SLTF/SLTF_$((Angle*10))_${LR}.DDB"
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} timeconvo
#-----------------------------------------------------------------------------#
