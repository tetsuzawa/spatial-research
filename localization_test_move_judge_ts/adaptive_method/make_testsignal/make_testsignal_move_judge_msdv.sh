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
if [ $# -ne 6 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: bash make_testsignal_move_judge_msdv.sh SUBJECT_DIR OUT_SUBJECT_DIR WHITE_NOISE MOVE_WIDTH_LIST MOVE_VELOCITY_LIST ANGLE\e[m \n\n"
  exit 1
fi

SUBJECT_DIR=$1
OUT_SUBJECT_DIR=$2
WHITE_NOISE=$3
MOVE_WIDTH_LIST=$4
MOVE_VELOCITY_LIST=$5
ANGLE=$6

echo "SUBJECT_DIR=${SUBJECT_DIR}"
echo "OUT_SUBJECT_DIR=${OUT_SUBJECT_DIR}"
echo "WHITE_NOISE=${WHITE_NOISE}"
echo "MOVE_WIDTH_LIST=${MOVE_WIDTH_LIST[@]}"
echo "MOVE_VELOCITY_LIST=${MOVE_VELOCITY_LIST[@]}"
echo "ANGLE=${ANGLE}"

# データ保存用ディレクトリの作成
mkdir -p ${OUT_SUBJECT_DIR}/angle_${ANGLE}/TS ${OUT_SUBJECT_DIR}/angle_${ANGLE}/ANSWER input_files

NUM_CPU_CORE=4

#---------------------------------連続音の作成---------------------------------#
clear
echo "###################################################################"
echo "      Creating continuous movement sounds ...                      "
echo "###################################################################"
echo

(
for MOVE_WIDTH in ${MOVE_WIDTH_LIST[@]}; do
  for MOVE_VELOCITY in ${MOVE_VELOCITY_LIST[@]}; do
    echo "${OUT_SUBJECT_DIR} ${WHITE_NOISE} ${MOVE_WIDTH} ${MOVE_VELOCITY} ${ANGLE} ${OUT_SUBJECT_DIR}/angle_${ANGLE}/TS"
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
for MOVE_WIDTH in ${MOVE_WIDTH_LIST[@]}; do
  for MOVE_VELOCITY in ${MOVE_VELOCITY_LIST[@]}; do
    for ROTATION_DIRECTION in c cc; do
      for LR in L R; do
        printf "angle_${ANGLE}/TS/move_judge_w${MOVE_WIDTH}_mt${MOVE_VELOCITY}_${ROTATION_DIRECTION}_${ANGLE}_${LR}.DDB\n" >> input_files/input_file_move_judge.dat
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
for MOVE_WIDTH in ${MOVE_WIDTH_LIST[@]}; do
  for MOVE_VELOCITY in ${MOVE_VELOCITY_LIST[@]}; do
    for ROTATION_DIRECTION in c cc; do
      ARG=$(printf "${OUT_SUBJECT_DIR}/angle_${ANGLE}/TS/move_judge_w${MOVE_WIDTH}_mt${MOVE_VELOCITY}_${ROTATION_DIRECTION}_${ANGLE}")
      for LR in L R; do
        echo "${ARG}_${LR}.DDB 48 0 5 ${ARG}_${LR}.DDB"
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
for MOVE_WIDTH in ${MOVE_WIDTH_LIST[@]}; do
  for MOVE_VELOCITY in ${MOVE_VELOCITY_LIST[@]}; do
    for ROTATION_DIRECTION in c cc; do
      ARG=$(printf "${OUT_SUBJECT_DIR}/angle_${ANGLE}/TS/move_judge_w${MOVE_WIDTH}_mt${MOVE_VELOCITY}_${ROTATION_DIRECTION}_${ANGLE}")
      for LR in L R; do
        echo "${ARG}_${LR}.DDB ${ARG}_${LR}.DSB"
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
for MOVE_WIDTH in ${MOVE_WIDTH_LIST[@]}; do
  for MOVE_VELOCITY in ${MOVE_VELOCITY_LIST[@]}; do
    for ROTATION_DIRECTION in c cc; do
      ARG=$(printf "${OUT_SUBJECT_DIR}/angle_${ANGLE}/TS/move_judge_w${MOVE_WIDTH}_mt${MOVE_VELOCITY}_${ROTATION_DIRECTION}_${ANGLE}")
      echo "${ARG}_L.DSB ${ARG}_R.DSB ${ARG}.DSB"
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
for MOVE_WIDTH in ${MOVE_WIDTH_LIST[@]}; do
  for MOVE_VELOCITY in ${MOVE_VELOCITY_LIST[@]}; do
    for ROTATION_DIRECTION in c cc; do
      ARG=$(printf "${OUT_SUBJECT_DIR}/angle_${ANGLE}/TS/move_judge_w${MOVE_WIDTH}_mt${MOVE_VELOCITY}_${ROTATION_DIRECTION}_${ANGLE}")
      echo "${ARG}_L.DDB ${ARG}_R.DDB ${ARG}_L.DSB ${ARG}_R.DSB"
    done
  done
done
) | xargs -t -L 1 -P ${NUM_CPU_CORE} rm
# ---------------------------------------無駄なファイルの削除--------------------------------------#

echo
echo "completed!!"
