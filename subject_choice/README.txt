
【説明】
被験者選定ディレクトリの例

【作成者】
下川原綾汰(sr17805@tomakomai.kosen-ac.jp)

【作成年】
2018年

【ディレクトリ構成】
subject_choise
|--README.txt
|--input_files (音圧調整用入力ファイル）
|  |--input_file_stationary.dat
|  |--input_file_tsp.dat
|--LSTF (測定したLSTF)
|--SUBJECTS (被検者ディレクトリ)
|  |--SIMO (例)
|     |--ANSWER (回答ファイル用ディレクトリ)
|     |--RSTF
|     |--HRTF
|     |--SLTF
|     |--SSTF
|     |--stationary_TS (生成された静止音像が保存されるディレクトリ)
|     |--TS (定位実験で使用する試験音全てを格納するディレクトリ)
|     |--TSP (方向確認用参照音を格納するディレクトリ)
|--localization_test_subject_choise.py (音像定位試験用Pythonスクリプト)
|--make_testsignal_for_subchoise.sh (試験音作成用シェルスクリプト)
|--p4s.DSB (ピンクノイズ)
|--w4s.DSB (白色雑音 (make_whitenoiseで生成したもの))

【注意事項】
書き換える場合は元のファイルの書き換えるのではなくコピーすること

