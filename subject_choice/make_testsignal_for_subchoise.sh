#!/usr/local/bin/zsh
# -*- coding: utf-8 -*-

##########################################################################################################
# 被験者選定用試験音作成シェルスクリプト
# TFMeasureで生成された被験者ファイルをSUBJECTS内にコピーして使用
# 
# 内容:
#  SLTFの算出，線形補間，白色雑音との畳込み，参照音の作成
#
# 実行例: 
#  sh make_testsignal_for_subchoise.sh HOGEHOGE(被験者名)
# 
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
##########################################################################################################
# 参照ファイル名をECTFからRSTFへ変更
#
# Shimizu Yuya (sy19807@)
# 2019.6.19
##########################################################################################################
# windowサイズを調整するapplescriptを削除
# 外部ファイルの存在を確認するプログラムを追加
# プログラムがエラーになった場合、実行を停止するオプションを追加
#
# Tetsu Takizawa (tt15219@)
# 2020.2.19
##########################################################################################################
set -eu

if [ $# -ne 1 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: SUBJECT\e[m \n\n"
  exit
fi

SUBJECT_DIR=$1
OUT_SUBJECT_DIR
mkdir -p ${OUT_SUBJECT_DIR}/SLTF ${OUT_SUBJECT_DIR}/TSP ${OUT_SUBJECT_DIR}/stationary_TS ${OUT_SUBJECT_DIR}/TS ${OUT_SUBJECT_DIR}/ANSWER

Move_Angle=(2 4 8 16 32)
sound=w4s.DSB

if [ ! -e $sound ];then
  echo "Error: file not exists: \`$sound\`"
  exit
fi

#--------------------------------------------SLTFの算出--------------------------------------------#
for LR in L R; do
  Bar="" 
  for ANGLE in `seq 0 5 355`; do
    clear
    echo "###################################################################"
    echo "                       Calculating SLFT ......    "
    echo "####################################################################"
    #Progress bar
    [ $((ANGLE%10)) = 0 ] && Bar=$Bar"█"
    Prog="$(((ANGLE+5)*100/360))% |$Bar"
    echo "$Prog\n"

    SPEAKER_NUM=$((ANGLE/5%18+1)) #
    #自身のSSTF
    timeconvo ${SUBJECT_DIR}/SSTF/cSSTF_${ANGLE}_${LR}.DDB LSTF/cinv_cLSTF_${SPEAKER_NUM}.DDB ${SUBJECT_DIR}/HRTF/HRTF_${ANGLj}_${LR}.DDB
    timeconvo ${SUBJECT_DIR}/HRTF/HRTF_${ANGLE}_${LR}.DDB ${SUBJECT_DIR}/RSTF/cinv_cRSTF_${LR}.DDB ${SUBJECT_DIR}/SLTF/SLTF_${ANGLj}_${LR}.DDB
  done
done
#-------------------------------------------------------------------------------------------------#  

#---------------------------------静止音の作成---------------------------------#
Bar=""
for END_ANGLE in `seq 0 30 180`; do
  clear
  echo "###################################################################"
  echo "              Making stationary sounds : $END_ANGLE deg."
  echo "###################################################################"
  Bar=$Bar"████"; Prog="$(((END_ANGLE+30)*100/210))% |$Bar"; echo "$Prog\n"
  for LR in L R; do
    timeconvo ${SUBJECT_DIR}/SLTF/SLTF_${END_ANGLE}_${LR}.DDB $sound ${SUBJECT_DIR}/stationary_TS/stationary_${END_ANGLE}_${LR}.DDB
    cutout_anyfile ${OUT_SUBJECT_DIR}/stationary_TS/stationary_${END_ANGLE}_${LR}.DDB 4001 28000 ${OUT_SUBJECT_DIR}/stationary_TS/stationary_${END_ANGLE}_${LR}.DDB
  done
done

clear
scaling_max_instant_amp input_files/input_file_stationary.dat 30000 ${OUT_SUBJECT_DIR}/
for END_ANGLE in `seq 0 30 180`; do
  clear
  arg=${OUT_SUBJECT_DIR}/stationary_TS/stationary_${END_ANGLE}
  for LR in L R; do
    cosine_windowing ${arg}_${LR}.DDB 48 0 30 ${arg}_${LR}.DDB
    dv ${arg}_${LR}.DDB ${arg}_${LR}.DSB
    # rm ${arg}_${LR}.DDB > /dev/null
  done
  mono2LR ${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB
  cp ${arg}.DSB ${OUT_SUBJECT_DIR}/TS/${arg##*/}.DSB
  # rm ${arg}_L.DSB ${arg}_R.DSB > /dev/null
done
#---------------------------------------------------------------------------------------#

#---------------------------------------方向確認用音源----------------------------------------------#
clear
for END_ANGLE in `seq 0 30 180`; do
  for LR in L R; do
    clear
    echo "###################################################################"
    echo "              Making sounds for direction confirmation : $END_ANGLE deg."
    echo "###################################################################"
    timeconvo ${SUBJECT_DIR}/SLTF/SLTF_${END_ANGLE}_${LR}.DDB $sound /tmp/tmp_${LR}.DDB
    cutout_anyfile /tmp/tmp_${LR}.DDB 4001 28000 ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_${LR}.DDB
    cosine_windowing ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_${LR}.DDB 48 0 30 ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_${LR}.DDB
  done
done
clear
if [ ! -e input_files/input_file_tsp.dat ];then
  echo "Error: file not exists: \`input_files/input_file_tsp.dat\`"
  exit
fi
scaling_max_instant_amp input_files/input_file_tsp.dat 30000 ${OUT_SUBJECT_DIR}/TSP/ > /dev/null
for END_ANGLE in `seq 0 30 180`; do
  for LR in L R; do
    dv ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_${LR}.DDB ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_${LR}.DSB
  done
  mono2LR ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_L.DSB ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_R.DSB ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGEj}.DSB
  rm ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_L.DSB ${OUT_SUBJECT_DIR}/TSP/TSP_${END_ANGLE}_R.DSB
done
#---------------------------------------------------------------------------------------#

echo "completed!!"

