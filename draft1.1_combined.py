import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
# import cv2 as cv
import io
import os
import time
import random
import threading
import volume_control
import pyaudio
import wave
import pydub
import sys
# volume_control.py
freq = 60  # 60秒おきに集中力を計算
excert_range = 5  # その５倍の時間の姿勢データを計算に使う
global position
position = [4] * freq*excert_range  # 集中力を計算するために姿勢を格納する配列(最初は非集中なので姿勢4を入れてる)


def get_position_seq():
    global position
    n = len(position)
    i = 0
    while True:
        position[i] = 1  # ここに姿勢を入れる####################
        print("姿勢は", position[i])
        i += 1
        if (i == n):
            i = 0
        time.sleep(1)  # 1秒ディレイを入れてる(多分いらない)


def concentration_rate(sequence):  # 集中力を計算する(関数は適当)
    counts = [0, 0, 0, 0]
    for num in sequence:
        if num == 1:
            counts[0] += 1
        elif num == 2:
            counts[1] += 1
        elif num == 3:
            counts[2] += 1
        elif num == 4:
            counts[3] += 1
    concentrate_raw = (counts[0]+counts[1]*0.2)/(len(sequence))
    if concentrate_raw >= 0.7:  # 集中力はせいぜい0.7が最大と仮定
        concentrate = 1
    else:
        concentrate = concentrate_raw/0.7
    print("集中力は", concentrate)
    return concentrate


def choose_music(concentration, threshold):  # 集中力に応じて音楽を選ぶ
    folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 上がる方
    if concentration < threshold:
        mp3_folder_path = os.path.join(folder_path, "no_concentrate_music")
        mp3_files = [file for file in os.listdir(
            mp3_folder_path) if file.endswith(".mp3")]
        random_file = random.choice(mp3_files)
        file_path = os.path.join(mp3_folder_path, random_file)
        print("上がる音楽", file_path, "を再生します")
    # 集中できる方
    else:
        mp3_folder_path = os.path.join(folder_path, "concentrate_music")
        mp3_files = [file for file in os.listdir(
            mp3_folder_path) if file.endswith(".mp3")]
        random_file = random.choice(mp3_files)
        file_path = os.path.join(mp3_folder_path, random_file)
        print("集中できる音楽", file_path, "を再生します")
    return file_path


def volume(raw_volume):  # dBに基づいて適切な音量に変える
    min_volume = 0.1
    return (10**(raw_volume*-0.5)-10**-0.5+min_volume)/(1-10**-0.5+min_volume)


def play_audio(freq):  # 音楽を再生する、音量は1秒おきに少しずつ滑らかに変わるようになってる(中断ボタンに合わせて再生を終了するとかは未実装)
    global position
    global event
    decay = int(freq/2)
    threshold_0 = 0.1  # これを下回ったら非集中と仮定
    threshold_1 = 0.5  # これを上回ったら集中と仮定
    n = 0
    concentration_1 = 0
    while True:
        if event == "end":
            break
        file_path = choose_music(concentration_1, threshold_0)
        # WAV形式に変換
        wav_file = file_path[:-4] + ".wav"
        sound = pydub.AudioSegment.from_mp3(file_path)
        sound.export(wav_file, format="wav")

        # WAVファイルを再生
        wf = wave.open(wav_file, 'rb')
        chunk = wf.getframerate()

        # PyAudioの初期化
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=chunk,
                        output=True)

        # 音声のストリームを再生
        data = wf.readframes(chunk)
        concentration_origin = concentration_1
        print("最初の集中力は", concentration_origin)
        while data:

            # 入力値に基づいて音量を調整
            concentration_0 = concentration_1
            concentration_1 = concentration_rate(position)
            n += freq

            if concentration_origin < threshold_0 and concentration_1 > threshold_1:
                break

            elif concentration_origin > threshold_1 and concentration_1 < threshold_0:
                break

            concentration_step = (concentration_1 - concentration_0)/decay
            raw_volume = concentration_0
            raw_volume += concentration_step
            for i in range(decay):
                # バイナリデータをnumpy配列に変換
                audio_array = np.frombuffer(data, dtype=np.int16)
                volume_factor = volume(raw_volume)
                print("音量は", volume_factor)
                adjusted_array = (audio_array * volume_factor).astype(np.int16)

                # 音声データをバイナリに戻す
                adjusted_data = adjusted_array.tobytes()

                # 調整済みの音声を再生

                stream.write(adjusted_data)

                # 次のデータを読み込む
                data = wf.readframes(chunk)

                raw_volume += concentration_step

                # ここに中断ボタンを押されたらループを抜けるコード??
                if event == "end":
                    break
            if event == "end":
                break
            volume_factor = volume(raw_volume)

            for i in range(freq - decay):
                # バイナリデータをnumpy配列に変換
                audio_array = np.frombuffer(data, dtype=np.int16)
                print("音量は", volume_factor)
                adjusted_array = (audio_array * volume_factor).astype(np.int16)

                # 音声データをバイナリに戻す
                adjusted_data = adjusted_array.tobytes()

                # 調整済みの音声を再生

                stream.write(adjusted_data)

                # 次のデータを読み込む
                data = wf.readframes(chunk)

                # ここに中断ボタンを押されたらループを抜けるコード??
                if event == "end":
                    break
            if event == "end":
                break

        # ストリームを閉じる
        stream.stop_stream()
        stream.close()

        # PyAudioを終了する
        p.terminate()

        # 一時的に作成したWAVファイルを削除
        os.remove(wav_file)

        # ここに中断ボタンを押されたらループを抜けるコード??
        if event == "end":
            break


# カレントディレクトリのパスを取得
current_directory = os.getcwd()
# ファイルのパスを作成
file_name = "image.jfif"
file_path = os.path.join(current_directory, "samplerec.png")
file_path2 = os.path.join(current_directory, "sin.png")
sg.theme("Systemdefault")
itm = []  # todoリスト

# todoリストの保存先からの読み込み
if os.path.isfile('mytext.txt'):
    f = open('mytext.txt', 'r')

    itm = f.read().splitlines()

    f.close()


# 使い方を説明するテキストは画像で渡しているけどそれ以外にいい方法が思いつかなかった
# このテキスト、ある程度詳しく書かないといけない気もするので説明だけで独立させてタブにさせてもよさそう
layout1 = [[sg.Listbox(itm, size=(60, 7), key="todolist", enable_events=True),
            sg.Button("やること追加", key="taskadd"),
            sg.Button("開始", size=(10, 2), key="start", disabled=True),
           sg.Button(image_filename=file_path, key="nowrec", disabled=True, visible=False)],
           [sg.Button("終了", key="end", disabled=True)],
           [sg.Text("録音が完了しました。上のタブを切り替えて結果を確認してください", key="afterrec", visible=False)]]
# 2つ目のタブ、結果表示ページ(リアルタイムで動かしたい)


cv1 = sg.Canvas(size=(400, 300), key="-CANVAS-")
layout2 = [[cv1]]
# layout2 = [[sg.Image(filename =file_path2)]]


layout = [
    [sg.TabGroup([[sg.Tab('起動', layout1), sg.Tab('結果', layout2, key="result", disabled=False)]])]]
global window
window = sg.Window("recsys3.3.1.1.py", layout, finalize=True)
# 描画
x = []
y = []
fig = plt.figure(figsize=(6, 4))
plt.plot(x, y)
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.savefig("sin.png")
tcv = cv1.TKCanvas
fag = FigureCanvasTkAgg(fig, tcv)
fag.draw()
fag.get_tk_widget().pack()

"""plt.ion()  # 対話モードを有効にする
#fig, ax = plt.subplots()
line, = ax.plot(x, y)
plt.switch_backend("TkAgg")
def update_plot(x, y):
    line.set_data(x, y)
    ax.relim()  # 軸の範囲を更新
    ax.autoscale_view()  # プロット領域を自動調整
    fig.canvas.draw()  # プロットを描画"""


# 時間経過は別スレッドで


def timer(x, y, name):
    global window
    global event
    global values
    seconds = 0
    while True:
        time.sleep(1)
        seconds += 1
        x.append(seconds)
        y.append(random.random())
        plt.plot(x, y, color="blue")
        plt.xlabel("x")
        plt.ylabel("sin(x)")
        plt.savefig(name)
        # update_plot(x,y)
        # Matplotlibの描画をGUIキャンバスに反映
        # fig_photo = plt.gcf()
        # draw_photo = fig_photo.canvas.tostring_rgb()
        # window["-CANVAS-"].draw_image(data=draw_photo, location=(0, 0))
        print(x)
        if event == "end":
            break


global event
global values
while True:
    event, values = window.read()
    print("イベント:", event, ":値", values)

    if event == None:
        # 一旦リセット
        with open("mytext.txt", "w", encoding='utf-8') as f:
            f.write('')
        # 現在のtodoリストの保存
        with open("mytext.txt", "a", encoding='utf-8') as f:
            for s in itm:
                f.write(s)
                f.write("\n")
        break
    elif values["todolist"] != []:
        window['start'].update(disabled=False)
    if event == "taskadd":
        r = sg.PopupGetText('やりたいことを入力してください.', title='入力画面')
        if r:  # 戻り値が None や空文字列でない場合の処理
            itm.append(r)
            window['todolist']. Update(values=itm)
    if event == "start":
        cv1 = sg.Canvas(size=(400, 300), key="-CANVAS-")
        x = []
        y = []
        name = random.random()
        name = str(name)+".png"
        plt.plot(x, y)
        plt.xlabel("x")
        plt.ylabel("sin(x)")
        plt.savefig(name)

        window["nowrec"].update(visible=True)
        window['result'].update(disabled=False)
        window["end"].update(disabled=False)
        window["start"].update(disabled=True)
        time_current = time.time()
        timer_thread = threading.Thread(target=timer, args=(x, y, name))
        timer_thread.start()
        t1 = threading.Thread(target=volume_control.get_position_seq)
        t1.start()
        volume_thread = threading.Thread(target=play_audio, args=(freq,))
        volume_thread.start()
    if event == "end":
        window["end"].update(disabled=True)
        window["start"].update(disabled=False)
        window["nowrec"].update(visible=False)
        window["start"].update(disabled=False)
        itm.remove(values['todolist'][0])
        window['todolist']. Update(values=itm)
window.close()
