#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ######################################################################
# 試験音作成
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################
# sh main (subject_directory : ex. hogehoge/SHIMIZU) (LSTF_directory : hogehoge/LSTF)
# ######################################################################
if [ $# -ne 2 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: SUBJECT mode(0/1)\e[m \n\n"
  exit
fi

mkdir -p $1/TS $1/ANSWER

sh make_SLTF.sh $1 $2 # HRTFとSLTFの生成
sh make_SLTF.sh $1 # HRTFとSLTFの生成
sh liner_interpolation.sh $1 # SLTFの線形補間
sh make_stationary_sound_images $1 # 静止音像の作成
sh make_moving_sound_images.sh $1 # 移動音像の作成
sh direction_confirm_sound.sh $1 # 方向確認用の静止音像の作成

echo "completed!!"