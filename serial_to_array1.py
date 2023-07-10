def serial_to_array():      ##マルチスレッド前提。data_arrayに12列でデータを送り続ける、
    global data_array       ##集中力を計算する関数の頭でもこれを書く
    global concent_score

    # シリアルポートの設定
    ser = serial.Serial('/dev/cu.usbmodem11401', 9600)  # ポート名とボーレートを指定してください
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
            if len(history) > 200:
                sum_history -= sum(history[0])/len(history[0])
                del history[0]
            concent_score = 100*np.exp(-sum_history/2e3)
            ##if row_count == 10:#行数はここ
            ##    break
    ##return data_array
        if event == "end":
            break
