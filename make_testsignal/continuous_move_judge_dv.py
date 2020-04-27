#!/usr/local/bin/python3

# ##################################################
# フーリエ級数窓を用いたfadein-fadeout法による移動音の生成
# 
# 作成者:下川原綾汰
# 作成年:2018
# ##################################################

from numpy import *
import sys

set_printoptions(threshold=inf)  # 配列を省略しないでprint
args = sys.argv

if len(args) != 7:
    print("usage: fadein-fadeout.py subject import_file(.DSB) movement_width move_velocity end_angle outdir")
    sys.exit()

# 移動のパラメータ
subject = args[1]  # 被験者
in_name = args[2]  # 音ファイル
movement_width = int(args[3])  # 移動幅
repeat_times = 1  # 繰り返し回数
move_velocity = int(args[4])
move_time = int(movement_width * 1000 / move_velocity)  # 終了角度
end_angle = int(args[5])
outdir = args[6]  # 出力先
movement_angle = movement_width * repeat_times + 1  # 移動角度

dwell_time = move_time * 48 / (movement_width * repeat_times * 2 + 1)  # 1度動くのに必要な時間　速度の逆数
duration_time = int(dwell_time * 63 / 64)  # 持続時間
overlap_time = int(dwell_time * 1 / 64)  # 切り替え時間

present_time = int(movement_angle * dwell_time)  # 提示時間

# フーリエ級数窓の係数
a0 = (1 + sqrt(2)) / 4
a1 = 0.25 + 0.25 * sqrt((5 - 2 * sqrt(2)) / 2)
a2 = (1 - sqrt(2)) / 4
a3 = 0.25 - 0.25 * sqrt((5 - 2 * sqrt(2)) / 2)

# フーリエ級数窓
fadein_fil = [(a0 - a1 * cos(pi / overlap_time * i) + a2 * cos(2.0 * pi / overlap_time * i) - a3 * cos(
    3.0 * pi / overlap_time * i)) for i in range(overlap_time)]
fadeout_fil = [(a0 + a1 * cos(pi / overlap_time * i) + a2 * cos(2.0 * pi / overlap_time * i) + a3 * cos(
    3.0 * pi / overlap_time * i)) for i in range(overlap_time)]

# 音データの読み込み
with open(in_name, 'rb') as sound_bin: sound = frombuffer(sound_bin.read(), dtype=int16)

for direction in ['c', 'cc']:
    for LR in ['L', 'R']:
        move_out = [0] * overlap_time
        angle_list = []

        for angle in range(movement_angle * 2 - 1):
            data_angle = angle % ((movement_width * 2) * 2)  # ノコギリ波を作成
            if data_angle > (movement_width * 2): data_angle = (movement_width * 2) * 2 - data_angle  # ノコギリ波から三角波を作成
            if direction is 'cc': data_angle = -data_angle
            data_angle = data_angle / 2
            if data_angle < 0: data_angle += 360  # 角度が負のとき360を加算

            # SLTFの読み込み
            with open(subject + "/SLTF/SLTF_" + str(int((end_angle + data_angle) * 10) % 3600) + "_" + LR + ".DDB",
                      'rb') as SLTF_bin:
                SLTF = frombuffer(SLTF_bin.read(), dtype=float64)
                angle_list.append(str(int((end_angle + data_angle) * 10) % 3600))  # 使ったSLTFを最後に表示するためのリストを作成
               
            # Fadein-Fadeout #####################################################################################
            # 音データと伝達関数の畳込み
            sound_SLTF = convolve(sound[angle * (duration_time + overlap_time):duration_time + overlap_time * 2 + (
                        duration_time + overlap_time) * angle + len(SLTF) * 3 + 1], SLTF)
            sound_SLTF = sound_SLTF[len(SLTF) * 2:len(sound_SLTF) - len(SLTF) * 2]  # 無音区間の切り出し

            # 前の角度のfadeout部と現在の角度のfadein部の加算
            fadein = [sound_SLTF[i] * fadein_fil[i] for i in range(overlap_time)]
            for i in range(overlap_time): move_out[(duration_time + overlap_time) * angle + i] += fadein[i]

            # 持続時間
            move_out.extend(sound_SLTF[overlap_time:len(sound_SLTF) - overlap_time])

            # fadeout
            fadeout = [(sound_SLTF[len(sound_SLTF) - overlap_time + i] * fadeout_fil[i]) for i in range(overlap_time)]
            move_out.extend(fadeout)

        # 先頭のFadein部をカット(インデントに注意!)
        out = move_out[overlap_time:]
        ######################################################################################################

        # DDBへ出力 ###############################################################################################
        # data_max = max(out)
        # out = [(out[n]/data_max*28000) for n in range(len(out))]
        out = array(out).astype(float64)  # float64バイナリに変換
        # DDBファイルに書き出し
        out_file = outdir + "/move_judge_w" + str(movement_width) + "_mt" + str(
            move_velocity) + "_" + direction + "_" + str(end_angle) + "_" + LR + ".DDB"
        with open(out_file, 'wb') as data:
            data.write(out)
            print(out_file + ': length=' + str(len(out)))
            print('Used angle:' + str(angle_list))
        ##########################################################################################################
