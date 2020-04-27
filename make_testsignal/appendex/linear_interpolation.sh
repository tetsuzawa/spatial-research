#!/usr/local/bin/zsh
# -*- coding: utf-8 -*-

# ######################################################################
# 線形補間(5°間隔=>1°間隔)
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################

  Bar=""
  for LR in L R; do
    for Angle in `seq 0 5 355`; do
      clear
      echo "###################################################################"
      echo "      Linear interpolation : $Angle - $(((Angle+5)%360)) deg."
      echo "###################################################################"
      [ $((Angle%20)) = 0 ] && Bar=$Bar"█"
      Prog="$(((Angle+5)*100/360/2))% |$Bar"
      echo "$Prog\n"

      for i in `seq 4 1`; do
        linear_inpo_hrir_using_ATD ../$1/SLTF/SLTF_${Angle}_${LR}.DDB ../$1/SLTF/SLTF_$(((Angle+5)%360))_${LR}.DDB \
          0.$((i*2)) ../$1/SLTF/SLTF_$((Angle+5-i))_${LR}.DDB > /dev/null
          echo "interpolation ${Angle} - $(((Angle+5)%360)) => $((5-i))"
      done
    done
  done