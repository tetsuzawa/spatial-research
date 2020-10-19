#!/bin/bash

sub=$1 #　引数１を変数sub(被験者)に代入

#　必要なファイルのコピー
#cp -r ~/Desktop/2019/LSTF ${sub}/LSTF
# 　各ファイルの作成
mkdir -p ${sub}/STIMULI ${sub}/STIMULI_LL ${sub}/STIMULI_RR ${sub}/STIMULI_reverse ${sub}/test

rm input_files.dat

present_time=500


for angle in 0 15 30 45 60 75 90 105 120 135 150 165 180 ; do
    for LR in L R; do 
        # SLTFとw1s.DSBの畳み込み
         timeconvo ~/Desktop/2019/measure_kit/w1s.DSB ${sub}/SLTF/SLTF_${angle}_${LR}.DDA ${sub}/STIMULI/w1s_${angle}_${LR}.DDB
         cutout_anyfile ${sub}/STIMULI/w1s_${angle}_${LR}.DDB 4001 $((present_time*48+4000)) ${sub}/STIMULI/w1s_${angle}_${LR}.DDB
        echo ${sub}/STIMULI/w1s_${angle}_${LR}.DDB >> input_files.dat
        echo ""
    done
   # mono2LR ${sub}/STIMULI/w1s_${angle}_L.DSB ${sub}/STIMULI/w1s_${angle}_R.DSB ${sub}/STIMULI/w1s_${angle}_LR.DSB
done
#input_files内の振幅を32767で最大にする
scaling_max_instant_amp input_files.dat 32767 ""
#DSBは16bitで表現できる幅が狭いので､一旦64bitあるDDBに変換
for angle in 0 15 30 45 60 75 90 105 120 135 150 165 180; do
    for LR in L R; do 
    dv ${sub}/STIMULI/w1s_${angle}_${LR}.DDB ${sub}/STIMULI/w1s_${angle}_${LR}.DSB
    rm ${sub}/STIMULI/w1s_${angle}_${LR}.DDB
    done
    #バイノーラル音源の作成LL
    mono2LR ${sub}/STIMULI/w1s_${angle}_L.DSB ${sub}/STIMULI/w1s_${angle}_L.DSB ${sub}/STIMULI_LL/w1s_${angle}_LL.DSB
    #バイノーラル音源の作成RR
    mono2LR ${sub}/STIMULI/w1s_${angle}_R.DSB ${sub}/STIMULI/w1s_${angle}_R.DSB ${sub}/STIMULI_RR/w1s_${angle}_RR.DSB
    #バイノーラル音源の作成
    mono2LR ${sub}/STIMULI/w1s_${angle}_L.DSB ${sub}/STIMULI/w1s_${angle}_R.DSB ${sub}/STIMULI/w1s_${angle}_LR.DSB
    #バイノーラル音源の作成(反転)
    mono2LR ${sub}/STIMULI/w1s_${angle}_R.DSB ${sub}/STIMULI/w1s_${angle}_L.DSB ${sub}/STIMULI_reverse/w1s_${angle}_RL.DSB
    rm ${sub}/STIMULI/w1s_${angle}_L.DSB
    rm ${sub}/STIMULI/w1s_${angle}_R.DSB
done
cp ${sub}/STIMULI/*.DSB ${sub}/test
cp ${sub}/STIMULI_reverse/*.DSB ${sub}/test
cp ${sub}/STIMULI_RR/*.DSB ${sub}/test
cp ${sub}/STIMULI_LL/*.DSB ${sub}/test
#異常があれば消す
cp -r ~/Desktop/2019/${sub} ~/Desktop/2019