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
if [ $# -ne 1 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: SUBJECT\e[m \n\n"
  exit
fi

SUBJECT_DIR=$1

# データ保存用ディレクトリの作成
mkdir -p ${SUBJECT_DIR}/TS ${SUBJECT_DIR}/ANSWER input_files

WHITE_NOISE=w21s.DSB
move_width_list=`seq 1 30`
move_velocity_list=`seq 1 50`
end_angle_list=(45)

#---------------------------------連続音の作成---------------------------------#
echo "###################################################################"
echo "      Creating continuous movement sounds ...                      "
echo "###################################################################"
echo

for move_width in ${move_width_list}; do
  for move_velocity in ${move_velocity_list}; do
    for end_angle in ${end_angle_list}; do
      python3 continuous_move_judge_dv.py ${SUBJECT_DIR} ${WHITE_NOISE} ${move_width} ${move_velocity} ${end_angle} ${SUBJECT_DIR}/TS &
    done
  done
done
wait
echo "finished!"
echo "${SECONDS}sec elapsed ..."
SECONDS=0
#---------------------------------------------------------------------------------------#

#---------------------------------最大音圧の調整---------------------------------#
echo "###################################################################"
echo "      Adjusting max sound pressure ...                             "
echo "###################################################################"
echo

echo "" >| input_files/input_file_move_judge.dat
for move_width in ${move_width_list}; do
  for move_velocity in ${move_velocity_list}; do
    for end_angle in ${end_angle_list}; do
      for rotation_direction in c cc; do
        for LR in L R; do
          echo "TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}_${LR}.DDB" >> input_files/input_file_move_judge.dat
        done
      done
    done
  done
done
scaling_max_instant_amp input_files/input_file_move_judge.dat 30000 ${SUBJECT_DIR}/
echo "finished!"
echo "${SECONDS}sec elapsed ..."
SECONDS=0
#---------------------------------------------------------------------------------------#

# ---------------------------------------ステレオ化----------------------------------------------#
clear
echo "###################################################################"
echo "      Converting sounds to stereo ...                             "
echo "###################################################################"
echo

for move_width in ${move_width_list}; do
  for move_velocity in ${move_velocity_list}; do
    for end_angle in ${end_angle_list}; do
      for rotation_direction in c cc; do
        arg=${SUBJECT_DIR}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}
        for LR in L R; do
          cosine_windowing ${arg}_${LR}.DDB 48 0 30 ${arg}_${LR}.DDB &
        done
      done
    done
  done
done
wait

for move_width in ${move_width_list}; do
  for move_velocity in ${move_velocity_list}; do
    for end_angle in ${end_angle_list}; do
      for rotation_direction in c cc; do
        arg=${SUBJECT_DIR}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}
        for LR in L R; do
           dv ${arg}_${LR}.DDB ${arg}_${LR}.DSB &
        done
       done
     done
  done
done
wait

for move_width in ${move_width_list}; do
  for move_velocity in ${move_velocity_list}; do
    for end_angle in ${end_angle_list}; do
      for rotation_direction in c cc; do
        arg=${SUBJECT_DIR}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}
        mono2LR ${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB &
      done
    done
  done
done
wait

for move_width in ${move_width_list}; do
  for move_velocity in ${move_velocity_list}; do
    for end_angle in ${end_angle_list}; do
      for rotation_direction in c cc; do
        arg=${SUBJECT_DIR}/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}
        rm ${arg}_L.DDB ${arg}_R.DDB ${arg}_L.DSB ${arg}_R.DSB &
      done
    done
  done
done
wait
echo "finished!"
echo "${SECONDS}sec elapsed ..."
SECONDS=0
# ---------------------------------------------------------------------------------------#

echo
echo "completed!!"