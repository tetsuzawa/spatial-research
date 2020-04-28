#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# ######################################################################
# 移動音像作成と音圧調整，ステレオ化
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################

mkdir -p ../$1/continuous_TS
sound=../w4s.DSB
Bar=""
for End_Angle in `seq 0 200 1800`; do
  clear
  echo "###################################################################"
  echo "              Making movement sounds : $End_Angle deg."
  echo "###################################################################"
  Bar=$Bar"██"; Prog="$((End_Angle+10))% |$Bar"; echo "$Prog\n"
  for velocity in 16 32 64 128; do
    python3 continuous_velocity.py ../$1 $sound $velocity $End_Angle ../$1/continuous_TS
  done
done

echo "\c" > input_files/input_file_continuous.dat
for LR in L R; do
	for rotation in c cc; do
		for v in 16 32 64 128; do
			for End_Angle in `seq 0 200 1800`; do
				echo "continuous_TS/continuous_v${v}${rotation}_${End_Angle}_${LR}.DDB" >> input_files/input_file_continuous.dat
			done
		done
	done
done

clear
scaling_max_instant_amp input_files/input_file_continuous.dat 30000 ../$1/continuous_TS
for End_Angle in `seq 0 200 1800`; do
  for velocity in 16 32 64 128; do  
    clear
    for arg in ../$1/continuous_TS/continuous_v${velocity}c_${End_Angle} \
                ../$1/continuous_TS/continuous_v${velocity}cc_${End_Angle}; do
      for LR in L R; do
        cosine_windowing ${arg}_${LR}.DDB 48 0 30 ${arg}_${LR}.DSB
      done
      mono2LR ${arg}_L.DSB ${arg}_R.DSB ${arg}.DSB
      rm ${arg}_L.DSB ${arg}_R.DSB > /dev/null
      cp ${arg}.DSB ../$1/TS/${arg##*/}.DSB
    done
  done
done