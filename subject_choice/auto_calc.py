##########################################################################################################
# 実験結果から偏差等を計算するプログラム
# ex)python3 auto_calc.py hogehoge 2 
# 前後誤知覚率,平均定位誤差,標本標準偏差の算出を追加(2019.7.18)
#
# ex)python3 auto_calc.py HOGEHOGE TIMEs(1,2,3....)
#
# Shimizu Yuya(sy19807@)
# 2019
##########################################################################################################
from subprocess import Popen
import glob, sys, random, os, re, csv, math, numpy
from numpy import *
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/' #このスクリプトのパス
args = sys.argv
subject = "SUBJECTS/" + args[1]
times = args[2]

test_count =  numpy.array([0]*7)
FBC_count = numpy.array([0]*7)  
FBC_rate = numpy.array([0.]*8)
LE = numpy.array([0.]*7)
LE_ave = numpy.array([0.]*8)
LE_sum = numpy.array([0.]*7)
SSD_sum = numpy.array([0.]*7)
SSD = numpy.array([0.]*8)   #8要素(30°ずつ0-180°までの角度と全角度における平均値)

# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()

##########################################################################################################
# 前後誤知覚率,平均定位誤差,標本標準偏差の計算
##########################################################################################################
os.chdir(subject + "/TS/")
test_sounds = []
for i in range(5): test_sounds.extend(glob.glob("*"))

with open(SCRIPT_DIR+subject+"/ANSWER/answer_"+args[1]+"_"+times+".csv", 'r') as answer_file:
    
    reader = csv.reader(answer_file)
    temp2 = [row for row in reader]
    data = [row[1:] for row in temp2[1:]] #[呈示方位,解答方位,時間],[],[]
    #print(data[1][2]) #こう入力すると2番目のデータ群の時間(3番目のデータ)が帰ってくる

    for m in range(len(test_sounds)):
        FBC_flag = 0
        test_direction = data[m][0]
        answer = data[m][1]
        num = int(int(test_direction)/30)

        test_count[num] += 1 #ある角度について何回試験したかをカウント

        #前後誤知覚回数のカウント
        if (int(test_direction)<90 and int(answer)>90) or (int(test_direction)>90 and int(answer)<90):
            FBC_count[num] += 1  #ある角度での前後誤知覚数のカウント
            FBC_flag = 1
            
        #ある角度での定位誤差(Localization_Error)とある角度での定位誤差の合計(LE_sum)の計算
        if FBC_flag == 1:
            LE[num] = abs(abs(180 - int(answer)) - int(test_direction)) #前後誤知覚の補正
        else:
            LE[num] = abs(int(answer) - int(test_direction))
        
        LE_sum[num] += LE[num]

for n in range(7):
    #前後誤知覚率の算出
    FBC_rate[n] = FBC_count[n]/test_count[n]

    #平均定位誤差の計算(角度につき5回行っているため、合計を5で割る) ex.LE_ave[1]=10なら30°における平均定位誤差が30°
    LE_ave[n] = LE_sum[n]/test_count[n]

with open(SCRIPT_DIR+subject+"/ANSWER/answer_"+args[1]+"_"+times+".csv", 'r') as answer_file:
    
    reader = csv.reader(answer_file)
    temp2 = [row for row in reader]
    data = [row[1:] for row in temp2[1:]] #[呈示方位,解答方位,時間],[],[]

    for p1 in range(len(test_sounds)):

        test_direction = data[p1][0]
        answer = data[p1][0]
        num = int(int(test_direction)/30)

        #前後誤知覚の判定
        if (int(test_direction)<90 and int(answer)>90) or (int(test_direction)>90 and int(answer)<90):
            LE[num] = abs(abs(180 - int(answer)) - int(test_direction)) #前後誤知覚の補正
        else:
            LE[num] = abs(int(answer) - int(test_direction))
        
        SSD_sum[num] += ( (LE[num]-LE_ave[num]) **2)#(xi-_x)^2

#標本標準偏差の算出(0-180°の7角度と平均)
for p2 in range(7):
    FBC_rate[7] += (FBC_rate[p2]/7)

    LE_ave[7] += (LE_ave[p2]/7)

    SSD[p2] = math.sqrt(SSD_sum[p2]/4)
    SSD[7] += (SSD[p2]/7) #SSDの平均値を7要素目に代入

##########################################################################################################
# 計算した角度毎の前後誤知覚率,平均定位誤差,標本標準偏差,の記憶
##########################################################################################################

with open(SCRIPT_DIR+subject+"/ANSWER/calc_"+args[1]+"_"+times+".csv", 'a') as calc_file:
    #for i in range(len(test_sounds)): calc_file.write(test_sounds[i]+"\n")
    calc_file.write("Presented_Direrction,FBC_rate,Average_LE,SSD" + "\n")
    for p3 in range(8):
        if int(p3) <= 6: calc_file.write(str(p3*30) + "," + str(FBC_rate[p3]) + "," + str(LE_ave[p3]) + "," + str(SSD[p3]) + "\n")
        else: calc_file.write("Average" + "," + str(FBC_rate[p3]) + "," + str(LE_ave[p3]) + "," + str(SSD[p3]) + "\n")

print(str(test_count)) #ok
print(str(FBC_rate)) #ok
print(str(LE_ave)) #ok
print(str(SSD)) #ok

if (FBC_rate[7]<=0.25) and (LE_ave[7]<=20) and (SSD[7]<=20):
    subprocess("say おめでとうございます あなたは被験者に採用されました")
    print(">採用!!")
else:
    subprocess("say 残念ながら あなたは被験者に採用されませんでした")
    print(">不採用!!")

#subprocess("say お疲れさまでした 以上で試験は終了です")
