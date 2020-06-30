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

subdir=SUBJECTS/$1
mkdir -p ${subdir}/HRTF ${subdir}/SLTF ${subdir}/TSP ${subdir}/stationary_TS ${subdir}/TS ${subdir}/ANSWER

Move_Angle=(2 4 8 16 32)
sound=w4s.DSB

if [ ! -e $sound ];then
  echo "Error: file not exists: \`$sound\`"
  exit
fi

#--------------------------------------------SLTFの算出--------------------------------------------#
for LR in L R; do
  Bar="" 
  for Angle in `seq 0 5 355`; do
    clear
    echo "###################################################################"
    echo "                       Calculating SLFT ......    "
    echo "####################################################################"
    #Progress bar
    [ $((Angle%10)) = 0 ] && Bar=$Bar"█"
    Prog="$(((Angle+5)*100/360))% |$Bar"
    echo "$Prog\n"

    speaker_num=$((Angle/5%18+1)) #
    #自身のSSTF
    timeconvo ${subdir}/SSTF/cSSTF_${Angle}_${LR}.DDB LSTF/cinv_cLSTF_${speaker_num}.DDB ${subdir}/HRTF/HRTF_${Angle}_${LR}.DDB
    timeconvo ${subdir}/HRTF/HRTF_${Angle}_${LR}.DDB ${subdir}/RSTF/cinv_cRSTF_${LR}.DDB ${subdir}/SLTF/SLTF_${Angle}_${LR}.DDB
  done
done
#-------------------------------------------------------------------------------------------------#  

#---------------------------------静止音の作成---------------------------------#
Bar=""
for End_Angle in `seq 0 30 180`; do
  clear
  echo "###################################################################"
  echo "              Making stationary sounds : $End_Angle deg."
  echo "###################################################################"
  Bar=$Bar"████"; Prog="$(((End_Angle+30)*100/210))% |$Bar"; echo "$Prog\n"
  for LR in L R; do
    timeconvo ${subdir}/SLTF/SLTF_${End_Angle}_${LR}.DDB $sound ${subdir}/stationary_TS/stationary_${End_Angle}_${LR}.DDB
    cutout_anyfile ${subdir}/stationary_TS/stationary_${End_Angle}_${LR}.DDB 4001 28000 ${subdir}/stationary_TS/stationary_${End_Angle}_${LR}.DDB
  done
done

clear
scaling_max_instant_amp input_files/input_file_stationary.dat 30000 ${subdir}/
for End_Angle in `seq 0 30 180`; do
  clear
  arg=${subdir}/stationary_TS/stationary_${End_Angle}
  for LR in L R; do
    cosine_windowing ${arg}_${LR}.DDB 48 0 30 ${arg}_${LR}.DDB
    dv ${arg}_${LR}.DDB ${arg}_${LR}.DSB
    # rm ${arg}_${LR}.DDB > /dev/null
  done
  mono2LR ${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB
  cp ${arg}.DSB ${subdir}/TS/${arg##*/}.DSB
  # rm ${arg}_L.DSB ${arg}_R.DSB > /dev/null
done
#---------------------------------------------------------------------------------------#

#---------------------------------------方向確認用音源----------------------------------------------#
clear
for End_Angle in `seq 0 30 180`; do
  for LR in L R; do
    clear
    echo "###################################################################"
    echo "              Making sounds for direction confirmation : $End_Angle deg."
    echo "###################################################################"
    timeconvo ${subdir}/SLTF/SLTF_${End_Angle}_${LR}.DDB $sound /tmp/tmp_${LR}.DDB
    cutout_anyfile /tmp/tmp_${LR}.DDB 4001 28000 ${subdir}/TSP/TSP_${End_Angle}_${LR}.DDB
    cosine_windowing ${subdir}/TSP/TSP_${End_Angle}_${LR}.DDB 48 0 30 ${subdir}/TSP/TSP_${End_Angle}_${LR}.DDB
  done
done
clear
if [ ! -e input_files/input_file_tsp.dat ];then
  echo "Error: file not exists: \`input_files/input_file_tsp.dat\`"
  exit
fi
scaling_max_instant_amp input_files/input_file_tsp.dat 30000 ${subdir}/TSP/ > /dev/null
for End_Angle in `seq 0 30 180`; do
  for LR in L R; do
    dv ${subdir}/TSP/TSP_${End_Angle}_${LR}.DDB ${subdir}/TSP/TSP_${End_Angle}_${LR}.DSB
  done
  mono2LR ${subdir}/TSP/TSP_${End_Angle}_L.DSB ${subdir}/TSP/TSP_${End_Angle}_R.DSB ${subdir}/TSP/TSP_${End_Angle}.DSB
  rm ${subdir}/TSP/TSP_${End_Angle}_L.DSB ${subdir}/TSP/TSP_${End_Angle}_R.DSB
done
#---------------------------------------------------------------------------------------#

echo "completed!!"

