# coding: utf -8
import PySimpleGUI as sg
import time
import simpleaudio
import pyaudio  # 録音機能を使うためのライブラリ
import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import cv2 as cv
import io
# 録音するための関数


def recordvoice():
    RECORD_SECONDS = 10  # 録音する時間の長さ（秒）
    WAVE_OUTPUT_FILENAME = "sample.wav"  # 音声を保存するファイル名
    iDeviceIndex = 0  # 録音デバイスのインデックス番号

    # 基本情報の設定
    FORMAT = pyaudio.paInt16  # 音声のフォーマット
    CHANNELS = 1  # モノラル
    RATE = 44100  # サンプルレート
    CHUNK = 2**11  # データ点数
    audio = pyaudio.PyAudio()  # pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        input_device_index=iDeviceIndex,  # 録音デバイスのインデックス番号
                        frames_per_buffer=CHUNK)

    # --------------録音開始---------------

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # --------------録音終了---------------

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()


# ここからレイアウト
sg.theme("Systemdefault")
n = 3
itm = ["福山雅治1", "アントニオ猪木1"]
# 使い方を説明するテキストは画像で渡しているけどそれ以外にいい方法が思いつかなかった
# このテキスト、ある程度詳しく書かないといけない気もするので説明だけで独立させてタブにさせてもよさそう
layout1 = [[sg.Image(filename="C:\\sysrec\picture\sampletext2.png", pad=((0, 80), (30, 30)))],
           [sg.Listbox(itm, size=(30, 7), key="select", enable_events=True),
            sg.Button("見本を聞く", key="listen", disabled=True),
            sg.Button("開始", size=(10, 2), key="rec", disabled=True),
            sg.Text(n, key="count", size=10, visible=False),
           sg.Button(image_filename="C:\\sysrec\picture\samplerec.png", key="nowrec", disabled=True, visible=False)],
           [sg.Text("録音が完了しました。上のタブを切り替えて結果を確認してください", key="afterrec", visible=False)]]
# layout2はまだまだこれから

cv1 = sg.Canvas()

x = np.linspace(0, 4*np.pi, 200)
y = np.sin(x)

"""# 動画処理
##
# ポップアップでファイル名を取得する
filename = 'C:\\Users\wakai_2\Desktop\class\B2A\codepractice\sysrec\sample.mp4'

# 　取得したファイルがNoneなら、終了

# 　選択された動画ファイルの読み込み
vidFile = cv.VideoCapture(filename)

# 　動画ファイルのプロパティを取得（総フレーム数、FPS）
num_frames = vidFile.get(cv.CAP_PROP_FRAME_COUNT)
fps = vidFile.get(cv.CAP_PROP_FPS)
#
# ここまで"""


score = 0
layout2 = [[sg.Text("あなたの点数は"+str(score) + "点です", key="point")],
           [cv1], [sg.Image(filename='', key='-image-')]]
layout = [
    [sg.TabGroup([[sg.Tab('録音', layout1), sg.Tab('結果', layout2, key="result", disabled=True)]])]]

window = sg.Window("recsys3.3.1.1.py", layout, finalize=True)

"""# 動画処理
image_elem = window['-image-']
slider_elem = window['-slider-']
# ここまで"""

x = np.linspace(0, 4*np.pi, 200)
y = np.sin(x)

fig = plt.figure(figsize=(6, 4))
plt.plot(x, y)
plt.xlabel("x")
plt.ylabel("sin(x)")
tcv = cv1.TKCanvas
fag = FigureCanvasTkAgg(fig, tcv)
fag.draw()
fag.get_tk_widget().pack()


z = np.cos(x)
fig2 = plt.figure(figsize=(4, 2))
plt.plot(x, z)
plt.xlabel("x")
plt.ylabel("cos(x)")
tcv2 = cv1.TKCanvas
fag2 = FigureCanvasTkAgg(fig2, tcv2)
fag2.draw()
fag2.get_tk_widget().pack()

while True:
    event, values = window.read()
    print("イベント:", event, ":値", values)
    if event == None:
        break
    elif values["select"] != []:
        window['rec'].update(disabled=False)
        window['listen'].update(disabled=False)

    if event == "listen":
        window['listen'].update(disabled=True)
        window['rec'].update(disabled=True)
        # 音声流す、流し終わったらボタンを押せるようにする
        wav_obj = simpleaudio.WaveObject.from_wave_file(
            "C:\\sysrec\picture\wai.wav")
        play_obj = wav_obj.play()
        while True:
            event, values = window.read(timeout=50)
            if play_obj.is_playing():
                continue
            else:
                break
        window['rec'].update(disabled=False)
        window['listen'].update(disabled=False)
    if event == "rec":
        window["count"].update(visible=True)
        window['rec'].update(disabled=True)
        window['listen'].update(disabled=True)
        # 3カウント→recの画像表示
        start_time = time.time()
        while True:
            event, values = window.read(timeout=50)
            n = round(3.5-(time.time() - start_time))
            window["count"].update(n)
            if (3.5-(time.time() - start_time) < 0.6):
                window["count"].update(visible=False)
                window["nowrec"].update(visible=True)
            if (n <= 0):
                recordvoice()
                break
        window["nowrec"].update(visible=False)
        # wavファイルを採点関数に渡す
        score = 5
        # 採点結果反映完了
        window['rec'].update(disabled=False)
        window['listen'].update(disabled=False)
        window["result"].update(disabled=False)
        window["afterrec"].update(visible=True)
window.close()
