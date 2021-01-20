#!/usr/bin/env bash

#########################################################################################################
# 必要データ: 被験者のSSTFとECTF，LSTF
# 出力データ: 被験者正面から左右に移動して正面まで帰ってくる移動音(移動振幅と移動時間は可変)

# 作成者:下川原 綾汰
# 作成日:2018年 12月
#########################################################################################################
# プログラムを並列化した
#
# 作成者:瀧澤哲
# 作成年:2020
#########################################################################################################

# ファイルの上書き防止 && エラーが起きたら停止 && 変数の空文字列防止
set -Ceu

# 引数が間違っている場合終了
if [ $# -ne 2 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: bash make_testsignal_move_judge450_msdv.sh SUBJECT_DIR OUT_SUBJECT_DIR\e[m \n\n"
  exit 1
fi

SUBJECT_DIR=$1
OUT_SUBJECT_DIR=$2

WHITE_NOISE=input_files/w35s.DSB
# seq の -w オプションは桁合わせのゼロ埋めを有効化
move_width_list=`seq -w 10 10 500`
move_velocity_list=(020 040 080 160 320)
end_angle=450

# データ保存用ディレクトリの作成
mkdir -p ${OUT_SUBJECT_DIR}/end_angle_${end_angle}/TS ${OUT_SUBJECT_DIR}/end_angle_${end_angle}/ANSWER input_files

NUM_CPU_CORE=4

#---------------------------------連続音の作成---------------------------------#
clear
echo "###################################################################"
echo "      Creating continuous movement sounds ...                      "
echo "###################################################################"
echo

(
for move_width in ${move_width_list[@]}; do
  for move_velocity in ${move_velocity_list[@]}; do
    echo "${OUT_SUBJECT_DIR} ${WHITE_NOISE} ${move_width} ${move_velocity} ${end_angle} ${OUT_SUBJECT_DIR}/end_angle_${end_angle}/TS"
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} overlap-add-middle
#---------------------------------------------------------------------------------------#

#---------------------------------最大音圧の調整---------------------------------#
clear
echo "###################################################################"
echo "      Adjusting max sound pressure ...                             "
echo "###################################################################"
echo

printf "" >| input_files/input_file_move_judge.dat
for move_width in ${move_width_list[@]}; do
  for move_velocity in ${move_velocity_list[@]}; do
    for rotation_direction in c cc; do
      for LR in L R; do
        printf "end_angle_${end_angle}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}_${LR}.DDB\n" >> input_files/input_file_move_judge.dat
      done
    done
  done
done
scaling_max_instant_amp input_files/input_file_move_judge.dat 30000 ${OUT_SUBJECT_DIR}/
#---------------------------------------------------------------------------------------#

# -----------------------------------------コサイン窓----------------------------------------------#
clear
echo "###################################################################"
echo "      Multiplying cosine window ...                                "
echo "###################################################################"
echo

(
for move_width in ${move_width_list[@]}; do
  for move_velocity in ${move_velocity_list[@]}; do
    for rotation_direction in c cc; do
      arg=$(printf "${OUT_SUBJECT_DIR}/end_angle_${end_angle}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}")
      for LR in L R; do
        echo "${arg}_${LR}.DDB 48 0 5 ${arg}_${LR}.DDB"
      done
    done
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} cosine_windowing
# -----------------------------------------コサイン窓----------------------------------------------#

# ---------------------------------------dv------------------------------------------------------#
clear
echo "###################################################################"
echo "      Executing dv ...                                             "
echo "###################################################################"
echo

(
for move_width in ${move_width_list[@]}; do
  for move_velocity in ${move_velocity_list[@]}; do
    for rotation_direction in c cc; do
      arg=$(printf "${OUT_SUBJECT_DIR}/end_angle_${end_angle}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}")
      for LR in L R; do
        echo "${arg}_${LR}.DDB ${arg}_${LR}.DSB"
      done
     done
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} dv
# ---------------------------------------dv------------------------------------------------------#

# ---------------------------------------ステレオ化-----------------------------------------------#
clear
echo "###################################################################"
echo "      Converting sounds to stereo ...                             "
echo "###################################################################"
echo

(
for move_width in ${move_width_list[@]}; do
  for move_velocity in ${move_velocity_list[@]}; do
    for rotation_direction in c cc; do
      arg=$(printf "${OUT_SUBJECT_DIR}/end_angle_${end_angle}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}")
      echo "${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB"
    done
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} mono2LR
# ---------------------------------------ステレオ化-----------------------------------------------#

# ---------------------------------------無駄なファイルの削除--------------------------------------#
clear
echo "###################################################################"
echo "      Removing useless files ...                             "
echo "###################################################################"

(
for move_width in ${move_width_list[@]}; do
  for move_velocity in ${move_velocity_list[@]}; do
    for rotation_direction in c cc; do
      arg=$(printf "${OUT_SUBJECT_DIR}/end_angle_${end_angle}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}")
      echo "${arg}_L.DDB ${arg}_R.DDB ${arg}_L.DSB ${arg}_R.DSB"
    done
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} rm
# ---------------------------------------無駄なファイルの削除--------------------------------------#

echo
echo "completed!!"
