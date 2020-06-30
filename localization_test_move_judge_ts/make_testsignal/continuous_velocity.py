#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# フーリエ級数窓を用いたfadein-fadeout法による移動音の生成
# 
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
# ##################################################
# プログラムをリファクターした
#
# 作成者:瀧澤哲
# 作成年:2020
# ##################################################

import sys

import numpy as np


def main():
    np.set_printoptions(threshold=np.inf)  # 配列を省略しないでprint
    args = sys.argv

    if len(args) != 6:
        print("usage: fadein-fadeout.py subject inport_file(.DSB) movement_velocity end_angle outdir")
        sys.exit()

    # 移動のパラメータ
    subject = args[1]  # 被験者
    in_name = args[2]  # 音ファイル
    movement_velocity = int(args[3])  # 移動幅
    end_angle = int(args[4])  # 終了角度
    outdir = args[5]  # 出力先
    movement_angle = 60  # 移動角度

    dwell_time = int(48000 / movement_velocity)
    duration_time = int(dwell_time * 7 / 8)  # 持続時間
    overlap_time = int(dwell_time * 1 / 8)  # 切り替え時間

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
        sound = np.fromstring(sound_bin.read(), dtype=np.int16)

    for direction in ['c', 'cc']:
        for LR in ['L', 'R']:
            out = [0] * overlap_time
            angle_list = []
            for connection_number in range(movement_angle):
                if direction is 'c':
                    data_angle = connection_number - movement_angle + 1
                elif direction is 'cc':
                    data_angle = movement_angle - connection_number - 1

                # 角度が負のとき360を加算
                if data_angle < 0: data_angle += 360

                # SLTFのオープン
                with open(subject + "/SLTF/SLTF_" + str((data_angle + end_angle) * 10 % 360) + "_" + LR + ".DDB",
                          'rb') as SLTF_bin:
                    SLTF = np.fromstring(SLTF_bin.read(), dtype=np.float64)
                    angle_list.append((data_angle + end_angle) % 360)  # 使ったSLTFを最後に表示するためのリストを作成

                # 音データと伝達関数の畳込み
                sound_SLTF = np.convolve(sound[connection_number * (
                        duration_time + overlap_time):duration_time + overlap_time * 2 + (
                        duration_time + overlap_time) * connection_number + len(SLTF) * 3 + 1], SLTF)
                sound_SLTF = sound_SLTF[len(SLTF) * 2:len(sound_SLTF) - len(SLTF) * 2]  # 無音区間の切り出し

                # 前の角度のfadeout部と現在の角度のfadein部の加算
                fadein = [sound_SLTF[i] * fadein_fil[i] for i in range(overlap_time)]
                for i in range(overlap_time): out[(duration_time + overlap_time) * connection_number + i] += fadein[i]

                # 持続時間
                out.extend(sound_SLTF[overlap_time:len(sound_SLTF) - overlap_time])

                # fadeout
                fadeout = [(sound_SLTF[len(sound_SLTF) - overlap_time + i] * fadeout_fil[i]) for i in
                           range(overlap_time)]
                out.extend(fadeout)

            out = np.array(out[overlap_time:]).astype(np.float64)  # float64バイナリに変換
            # DSBファイルに書き出し
            out_file = outdir + "/continuous_v" + str(movement_velocity) + direction + "_" + str(
                end_angle) + "_" + LR + ".DDB"
            with open(out_file, 'wb') as data:
                data.write(out)
                print(out_file + ': length=' + str(len(out)))
                print('Used connection_number:' + str(angle_list))


if __name__ == '__main__':
    main()
