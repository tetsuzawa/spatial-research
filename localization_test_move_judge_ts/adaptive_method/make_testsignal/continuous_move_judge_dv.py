#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# フーリエ級数窓を用いたfadein-fadeout法による移動音の生成
#
# 作成者:下川原綾汰
# 作成年:2018
# ##################################################
# プログラムをリファクタした
#
# 作成者:瀧澤哲
# 作成年:2020
# ##################################################

import sys

import numpy as np


def main():
    np.set_printoptions(threshold=np.inf)  # 配列を省略しないでprint
    args = sys.argv

    if len(args) != 7:
        print(
            "usage: continuous_move_judge_dv.py subject import_file(.DSB) movement_width move_velocity end_angle outdir")
        sys.exit()

    # 移動のパラメータ
    subject = args[1]  # 被験者
    in_name = args[2]  # 音ファイル
    movement_width = int(args[3])  # 移動幅
    move_velocity = int(args[4])
    move_time = int(movement_width * 1000 / move_velocity)  # 終了角度
    end_angle = int(args[5])
    outdir = args[6]  # 出力先
    sampling_freq = 48  # サンプリング周波数[kHz]

    dwell_time = move_time * sampling_freq / movement_width   # 1度動くのに必要な時間　速度の逆数
    duration_time = int(dwell_time * 63 / 64)  # 持続時間 (63/64)
    overlap_time = int(dwell_time * 1 / 64)  # 切り替え時間 (1/64)

    # フーリエ級数窓の係数
    a0 = (1 + np.sqrt(2)) / 4
    a1 = 0.25 + 0.25 * np.sqrt((5 - 2 * np.sqrt(2)) / 2)
    a2 = (1 - np.sqrt(2)) / 4
    a3 = 0.25 - 0.25 * np.sqrt((5 - 2 * np.sqrt(2)) / 2)

    # フーリエ級数窓
    fadein_fil = [
        (a0 - a1 * np.cos(np.pi / overlap_time * i) + a2 * np.cos(2.0 * np.pi / overlap_time * i) - a3 * np.cos(
            3.0 * np.pi / overlap_time * i)) for i in range(overlap_time)]
    fadeout_fil = [
        (a0 + a1 * np.cos(np.pi / overlap_time * i) + a2 * np.cos(2.0 * np.pi / overlap_time * i) + a3 * np.cos(
            3.0 * np.pi / overlap_time * i)) for i in range(overlap_time)]

    # 音データの読み込み
    with open(in_name, 'rb') as sound_bin:
        sound = np.frombuffer(sound_bin.read(), dtype=np.int16)

    for direction in ['c', 'cc']:
        for LR in ['L', 'R']:
            move_out = [0] * overlap_time
            angle_list = []

            for angle in range(movement_width):
                data_angle = angle % (movement_width * 2)
                if data_angle > movement_width:
                    data_angle = movement_width*2 - data_angle
                if direction == "cc":
                    data_angle = -data_angle
                if data_angle < 0:
                    data_angle += 3600

                # SLTFの読み込み
                with open(subject + "/SLTF/SLTF_" + str(int(end_angle + data_angle) % 3600) + "_" + LR + ".DDB",
                          'rb') as SLTF_bin:
                    SLTF = np.frombuffer(SLTF_bin.read(), dtype=np.float64)
                    # 使ったSLTFを最後に表示するためのリストを作成
                    angle_list.append(str(int(end_angle + data_angle) % 3600))

                # Fadein-Fadeout #####################################################################################
                # 音データと伝達関数の畳込み
                # range_l = angle * (duration_time + overlap_time)
                # range_r = duration_time + overlap_time * 2 + (
                #         duration_time + overlap_time) * angle + len(SLTF) * 3 + 1
                # cut_sound = sound[angle * (duration_time + overlap_time):duration_time + overlap_time * 2 + (
                #         duration_time + overlap_time) * angle + len(SLTF) * 3 + 1]
                sound_SLTF = np.convolve(
                    sound[angle * (duration_time + overlap_time):duration_time + overlap_time * 2 + (
                        duration_time + overlap_time) * angle + len(SLTF) * 3 + 1], SLTF)
                # no_sound_l = len(SLTF) * 2
                # no_sound_r = len(sound_SLTF) - len(SLTF) * 2
                sound_SLTF = sound_SLTF[len(
                    SLTF) * 2:len(sound_SLTF) - len(SLTF) * 2]  # 無音区間の切り出し

                # 前の角度のfadeout部と現在の角度のfadein部の加算
                fadein = [sound_SLTF[i] * fadein_fil[i]
                          for i in range(overlap_time)]
                for i in range(overlap_time):
                    move_out[(duration_time + overlap_time)
                             * angle + i] += fadein[i]

                # 持続時間
                move_out.extend(
                    sound_SLTF[overlap_time:len(sound_SLTF) - overlap_time])

                # fadeout
                fadeout = [(sound_SLTF[len(sound_SLTF) - overlap_time + i] * fadeout_fil[i]) for i in
                           range(overlap_time)]
                move_out.extend(fadeout)

            # 先頭のFadein部をカット(インデントに注意!)
            out = move_out[overlap_time:]
            ######################################################################################################

            # DDBへ出力 ###############################################################################################
            # data_max = max(out)
            # out = [(out[n]/data_max*28000) for n in range(len(out))]
            out = np.array(out).astype(np.float64)  # float64バイナリに変換
            # DDBファイルに書き出し
            out_file = outdir + "/move_judge_w" + str(movement_width).zfill(3) + "_mt" + str(
                move_velocity).zfill(3) + "_" + direction + "_" + str(end_angle) + "_" + LR + ".DDB"
            with open(out_file, 'wb') as data:
                data.write(out.tobytes())
                print(out_file + ': length=' + str(len(out)))
                print('Used angle:' + str(angle_list))
            ##########################################################################################################


if __name__ == '__main__':
    main()
