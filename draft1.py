import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import cv2 as cv
import io
import os
import time
import random
import threading


# カレントディレクトリのパスを取得
current_directory = os.getcwd()
# ファイルのパスを作成
file_name = "image.jfif"
file_path = os.path.join(current_directory, "samplerec.png")
file_path2 = os.path.join(current_directory, "sin.png")
sg.theme("Systemdefault")
itm = []  # todoリスト
# 使い方を説明するテキストは画像で渡しているけどそれ以外にいい方法が思いつかなかった
# このテキスト、ある程度詳しく書かないといけない気もするので説明だけで独立させてタブにさせてもよさそう
layout1 = [[sg.Listbox(itm, size=(60, 7), key="todolist", enable_events=True),
            sg.Button("やること追加", key="taskadd"),
            sg.Button("開始", size=(10, 2), key="start", disabled=True),
           sg.Button(image_filename=file_path, key="nowrec", disabled=True, visible=False)],
           [sg.Button("終了", key="end", disabled=True)],
           [sg.Text("録音が完了しました。上のタブを切り替えて結果を確認してください", key="afterrec", visible=False)]]
# 2つ目のタブ、結果表示ページ(リアルタイムで動かしたい)


cv1 = sg.Canvas(size =(400,300), key ="-CANVAS-")
layout2 = [[cv1]]
#layout2 = [[sg.Image(filename =file_path2)]]


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


def timer(x, y,name):
    global window
    global event
    global values
    seconds = 0
    while True:
        time.sleep(1)
        seconds += 1
        x.append(seconds)
        y.append(random.random())
        plt.plot(x, y,color ="blue")
        plt.xlabel("x")
        plt.ylabel("sin(x)")
        plt.savefig(name)
        #update_plot(x,y)
            # Matplotlibの描画をGUIキャンバスに反映
        #fig_photo = plt.gcf()
        #draw_photo = fig_photo.canvas.tostring_rgb()
        #window["-CANVAS-"].draw_image(data=draw_photo, location=(0, 0))
        print(x)
        if event == "end":
            break


global event
global values
while True:
    event, values = window.read()
    print("イベント:", event, ":値", values)

    if event == None:
        break
    elif values["todolist"] != []:
        window['start'].update(disabled=False)
    if event == "taskadd":
        r = sg.PopupGetText('やりたいことを入力してください.', title='入力画面')
        if r:  # 戻り値が None や空文字列でない場合の処理
            itm.append(r)
            window['todolist']. Update(values=itm)
    if event == "start":
        cv1 = sg.Canvas(size =(400,300), key ="-CANVAS-")
        x =[]
        y =[]
        name =random.random()
        name =str(name)+".png"
        plt.plot(x, y)
        plt.xlabel("x")
        plt.ylabel("sin(x)")
        plt.savefig(name)

        window["nowrec"].update(visible=True)
        window['result'].update(disabled=False)
        window["end"].update(disabled=False)
        window["start"].update(disabled=True)
        time_current = time.time()
        timer_thread = threading.Thread(target=timer, args=(x, y,name))
        timer_thread.start()
    if event == "end":
        window["end"].update(disabled=True)
        window["start"].update(disabled=False)
window.close()
