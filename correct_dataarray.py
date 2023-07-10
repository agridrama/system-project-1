import serial
import numpy as np

global data_array
global concent_score
data_array = []
concent_score = 80

def serial_to_array():      ##マルチスレッド前提。data_arrayに12列でデータを送り続ける、
    global data_array       ##集中力を計算する関数の頭でもこれを書く
    global concent_score

    # シリアルポートの設定
    ser = serial.Serial('COM4', 9600)  # ポート名とボーレートを指定してください
    row_count = 0
    accum_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    prev_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    history = []
    sum_history = 0

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().rstrip()  # 改行文字を削除
            data = [int(x) for x in data.split(',') if x.strip() != '']

            data_array.append(data)
            row_count += 1
            for i in range(12):
                accum_values[i] *= 0.9
                accum_values[i] += abs(data[i]-prev_values[i])/9
                prev_values[i] = data[i]

            history.append(accum_values)
            sum_history += sum(accum_values)/len(accum_values)
            if row_count > 200:
                sum_history -= sum(history[row_count-200])/len(history[row_count-200])
                concent_score = 100/(1+sum_history/4e3)
            ##if row_count == 10:#行数はここ
            ##    break
    ##return data_array


print(serial_to_array())














