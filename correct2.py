import serial
import numpy as np
import time

global concent_score
concent_score = 80


def serial_to_array():  # マルチスレッド前提。data_arrayに12列でデータを送り続ける、
    global concent_score

    # シリアルポートの設定
    ser = serial.Serial('COM4', 9600)  # ポート名とボーレートを指定してください
    row_count = 0
    accums = 0
    prev_data = np.zeros(12)
    history = []
    sum_history = 0
    init = time.time()

    def accum_signal(sen_vals: np.array, prev_vals: np.array, accum_vals: np.array):
        accum_vals *= 0.7
        accum_vals += np.abs(sen_vals-prev_vals)*0.3
        return accum_vals

    while True:
        # if ser.in_waiting > 0:

        data = ser.readline().decode().rstrip()  # 改行文字を削除
        data = np.array([int(x)
                        for x in data.split(',') if x.strip() != ''])
        # print(data)
        row_count += 1
        accums = accum_signal(data, prev_data, accums)
        history.append(max(accums.sum()-30, 0))
        sum_history += history[len(history)-1]
        if len(history) > 200:
            sum_history -= history[len(history)-201]
        # print(time.time()-init)
        concent_score = 100-np.sqrt(max(sum_history,0))/3
        print(concent_score)
        prev_data = data
        # if row_count == 10:#行数はここ
        # break
        # else:
        #     print("sleep")
        #     time.sleep(0.1)
        # print(sum_history)
    # return data_array
        if concent_score < 60:
            data = "on"  # 送信する数値を設定します
            # ser.readline()
            ser.write(data.encode("ascii") + b'\n')
        if concent_score > 60:
            data = "off"  # 送信する数値を設定します
            # ser.readline()
            ser.write(data.encode() + b'\n')


        #if event ="end":
        #    data ="off"
        #    ser.write(data.encode() + b'\n')
print(serial_to_array())
