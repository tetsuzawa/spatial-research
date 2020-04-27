#!/usr/local/bin/zsh
# -*- coding: utf-8 -*-

# ######################################################################
# SLTFとHRTFの生成
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ######################################################################
# 参照ファイル名ECTFをRSTFに変更
# Shimizu Yuya (sy19807)
# 2019.6.6
# ######################################################################
# sh make_SLTF (subject_directory : ex. hogehoge/SHIMIZU) (LSTF_directory : hogehoge/LSTF)
# ######################################################################

mkdir -p ../$1/HRTF ../$1/SLTF
Bar="" 
for LR in L R; do
    for Angle in `seq 0 5 355`; do
        clear
        echo "###################################################################"
        echo "                       Calculating SLFT ......    "
        echo "####################################################################"
        #Progress bar
        [ $((Angle%20)) = 0 ] && Bar=$Bar"█"
        Prog="$(((Angle+5)*100/360/2))% |$Bar"
        echo "$Prog\n"

        speaker_num=$((Angle/5%18+1))
        timeconvo $1/SSTF/cSSTF_${Angle}_${LR}.DDB LSTF/cinv_cLSTF_${speaker_num}.DDB $1/HRTF/HRTF_${Angle}_${LR}.DDB
        #timeconvo $1/SSTF/cSSTF_${Angle}_${LR}.DDB LSTF/cinv_cLSTF_${speaker_num}.DDB $1/HRTF/HRTF_${Angle}_${LR}.DDB
        timeconvo $1/HRTF/HRTF_${Angle}_${LR}.DDB $1/RSTF/cinv_cRSTF_${LR}.DDB $1/SLTF/SLTF_${Angle}_${LR}.DDB
        #timeconvo $1/HRTF/HRTF_${Angle}_${LR}.DDB $1/ECTF/cinv_cECTF_${LR}.DDB $1/SLTF/SLTF_${Angle}_${LR}.DDB
    done
done