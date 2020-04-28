# -*- coding: utf-8 -*-

# ######################################################################
# 静止音像作成と音圧調整，ステレオ化
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################

# ファイルの上書き防止 && エラーが起きたら停止 && 変数の空文字列防止
set -Ceu

mkdir -p ../$1/stable_TS
sound=../w4s.DSB
echo "\c" > input_files/input_file_stable.dat
Bar=""
for End_Angle in `seq 0 200 1800`; do
  clear
  echo "###################################################################"
  echo "              Making stable sounds : $End_Angle deg."
  echo "###################################################################"
  Bar=$Bar"██"; Prog="$((End_Angle+10))% |$Bar"; echo "$Prog\n"
  for LR in L R; do
    timeconvo ../$1/SLTF/SLTF_${End_Angle}_${LR}.DDB $sound ../$1/stable_TS/stable_${End_Angle}_${LR}.DDB
    cutout_anyfile ../$1/stable_TS/stable_${End_Angle}_${LR}.DDB 4001 $((320*48+4000)) ../$1/stable_TS/stable_cut_${End_Angle}_${LR}.DDB
    echo "stable_TS/stable_cut_${End_Angle}_${LR}.DDB" >> input_files/input_file_stable.dat
 
  done
done
clear
scaling_max_instant_amp input_files/input_file_stable.dat 30000 ../$1/stable_TS
for End_Angle in `seq 0 200 1800`; do
clear
    arg=../$1/stable_TS/stable_cut_${End_Angle}
    for LR in L R; do
      cosine_windowing ${arg}_${LR}.DDB 48 0 2 ${arg}_${LR}.DSB
    done
    mono2LR ${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB
    rm ${arg}_L.DSB ${arg}_R.DSB
    cp ${arg}.DSB ../$1/TS/${arg##*/}.DSB
done