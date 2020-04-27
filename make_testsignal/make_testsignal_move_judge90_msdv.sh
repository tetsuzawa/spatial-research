#!/usr/bin/env bash

#########################################################################################################
# 必要データ: 被験者のSSTFとECTF，LSTF
# 出力データ: 被験者正面から左右に移動して正面まで帰ってくる移動音(移動振幅と移動時間は可変)

# 作成者:下川原 綾汰
# 作成日:2018年 12月
#########################################################################################################

# 引数が間違っている場合終了
if [ $# -ne 1 ]; then
  printf "\e[31;1m error: bad commandline format \n"
  printf " usage: SUBJECT\e[m \n\n"
  exit
fi

# データ保存用ディレクトリの作成
mkdir -p $1/HRTF $1/SLTF $1/TS $1/ANSWER input_files

sound=w35s.DSB
move_width_list=(4 8 16 32 64)
move_velocity_list=(4 8 16 32 64)
end_angle_list=(90)

# #--------------------------------------------SLTFの算出--------------------------------------------#
# for LR in L R; do
#   Bar="" 
#   for Angle in `seq 0 5 355`; do
#     clear
#     echo "###################################################################"
#     echo "                       Calculating SLFT ......   $Angle  : $LR"
#     echo "####################################################################"
#     #Progress bar
#     [ $((Angle%100)) = 0 ] && Bar=$Bar"█"
#     Prog="$(((Angle+50)*100/3600))% |$Bar"
#     echo "$Prog\n"

#     speaker_num=$((Angle/5%18+1)) #
#     #自身のSSTF
#     timeconvo $1/SSTF/cSSTF_${Angle}_${LR}.DDB LSTF/cinv_cLSTF_${speaker_num}.DDB $1/HRTF/HRTF_${Angle}_${LR}.DDB
#     timeconvo $1/HRTF/HRTF_${Angle}_${LR}.DDB $1/ECTF/cinv_cECTF_${LR}.DDB $1/SLTF/SLTF_$((Angle*10))_${LR}.DDB
#   done
# done
# # #-------------------------------------------------------------------------------------------------#  

# #------------------------------------線形補間(5deg.=>1deg.)------------------------------------#
# Bar=""
# for LR in L R; do
#   for Angle in `seq 0 50 3550`; do
#     clear
#     echo "###################################################################"
#     echo "      Linear interpolation : $Angle - $(((Angle+50)%3600)) deg. : $LR"
#     echo "###################################################################"
#     [ $((Angle%100)) = 0 ] && Bar=$Bar"█"
#     Prog="$(((Angle+500)*100/3600))% |$Bar"
#     echo "$Prog\n"
#     for i in `seq 1 9`; do
#     echo "0.$((10-i))"
#       linear_inpo_hrir_using_ATD $1/SLTF/SLTF_${Angle}_${LR}.DDB $1/SLTF/SLTF_$(((Angle+50)%3600))_${LR}.DDB \
#         0.$((10-i)) $1/SLTF/SLTF_$((Angle+i*10/2))_${LR}.DDB > /dev/null
#     done
#   done
# done
# #--------------------------------------------------------------------------------------------#

#---------------------------------連続音の作成---------------------------------#
Bar=""
for move_width in 4 8 16 32 64; do
  for move_velocity in 4 8 16 32 64; do
    for end_angle in 90; do  
      clear
      echo "###################################################################"
      echo "              move width : $move_width deg."
      echo "              move velocity  : $move_velocity °"
      echo "              end angle  : $end_angle deg."
      echo "###################################################################"
      python3 continuous_move_judge_dv.py $1 $sound $move_width $move_velocity $end_angle $1/TS
    done
  done
done
#---------------------------------------------------------------------------------------#

#---------------------------------最大音圧の調整---------------------------------#
echo "" > input_files/input_file_move_judge.dat
for move_width in 4 8 16 32 64; do
  for move_velocity in 4 8 16 32 64; do
   for end_angle in 90; do 
		for rotation_direction in c cc; do
      for LR in L R; do
        echo "TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}_${LR}.DDB" >> input_files/input_file_move_judge.dat
      done
    done  
   done
 	done
done
clear
scaling_max_instant_amp input_files/input_file_move_judge.dat 30000 $1/
#---------------------------------------------------------------------------------------#

# ---------------------------------------ステレオ化----------------------------------------------#
for move_width in 4 8 16 32 64; do
  for move_velocity in 4 8 16 32 64; do
   for end_angle in 90; do 
    for rotation_direction in c cc; do
        clear
        arg=$1/TS/move_judge_w${move_width}_mt${move_velocity}_${rotation_direction}_${end_angle}
        for LR in L R; do
          cosine_windowing ${arg}_${LR}.DDB 48 0 30 ${arg}_${LR}.DDB
          dv ${arg}_${LR}.DDB ${arg}_${LR}.DSB
        done
        mono2LR ${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB
        rm ${arg}_L.DDB ${arg}_R.DDB ${arg}_L.DSB ${arg}_R.DSB

      done
    done
  done
done
# ---------------------------------------------------------------------------------------#

 echo "completed!!"