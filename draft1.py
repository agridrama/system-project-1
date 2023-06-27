import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image
import cv2 as cv
import io
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
while True:
    event, values = window.read()
    print("イベント:", event, ":値", values)
    if event == None:
        break
window.close()
