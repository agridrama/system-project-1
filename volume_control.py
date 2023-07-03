import pyaudio
import wave
import pydub
import numpy as np
import os
import threading
import random
import time
import sys
freq = 60 #60秒おきに集中力を計算
excert_range = 5 #その５倍の時間の姿勢データを計算に使う
global position
position = [4] * freq*excert_range  #####集中力を計算するために姿勢を格納する配列(最初は非集中なので姿勢4を入れてる)

def get_position_seq():
    global position
    n = len(position)
    i = 0
    while True:
        position[i] = 1 ##############ここに姿勢を入れる####################
        print("姿勢は",position[i])
        i += 1
        if(i == n):
            i = 0
        time.sleep(1) ##1秒ディレイを入れてる(多分いらない)

def concentration_rate(sequence): ###集中力を計算する(関数は適当)
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
    if concentrate_raw >= 0.7:  ##集中力はせいぜい0.7が最大と仮定
        concentrate = 1
    else:
        concentrate = concentrate_raw/0.7
    print("集中力は",concentrate)
    return concentrate

def choose_music(concentration,threshold):  ##集中力に応じて音楽を選ぶ
    folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    #上がる方
    if concentration < threshold:
        mp3_folder_path = os.path.join(folder_path, "no_concentrate_music")
        mp3_files = [file for file in os.listdir(mp3_folder_path) if file.endswith(".mp3")]
        random_file = random.choice(mp3_files)
        file_path = os.path.join(mp3_folder_path, random_file)
        print("上がる音楽",file_path,"を再生します")
    #集中できる方
    else:
        mp3_folder_path = os.path.join(folder_path, "concentrate_music")
        mp3_files = [file for file in os.listdir(mp3_folder_path) if file.endswith(".mp3")]
        random_file = random.choice(mp3_files)
        file_path = os.path.join(mp3_folder_path, random_file)
        print("集中できる音楽",file_path,"を再生します")
    return file_path

def volume(raw_volume):     ##dBに基づいて適切な音量に変える
    min_volume = 0.1
    return (10**(raw_volume*-0.5)-10**-0.5+min_volume)/(1-10**-0.5+min_volume)

def play_audio(freq):   ##音楽を再生する、音量は1秒おきに少しずつ滑らかに変わるようになってる(中断ボタンに合わせて再生を終了するとかは未実装)
    global position
    global event
    decay = int(freq/2)
    threshold_0 = 0.1 ##これを下回ったら非集中と仮定
    threshold_1 = 0.5 ##これを上回ったら集中と仮定
    n = 0
    concentration_1 = 0
    while True:
        if event == "end":
            break
        file_path = choose_music(concentration_1,threshold_0)
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
                        rate = chunk,
                        output=True)

        # 音声のストリームを再生
        data = wf.readframes(chunk)
        concentration_origin = concentration_1
        print("最初の集中力は",concentration_origin)
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
                print("音量は",volume_factor)
                adjusted_array = (audio_array * volume_factor).astype(np.int16)

                # 音声データをバイナリに戻す
                adjusted_data = adjusted_array.tobytes()

                # 調整済みの音声を再生

                stream.write(adjusted_data)

                # 次のデータを読み込む
                data = wf.readframes(chunk)

                raw_volume += concentration_step

                #########ここに中断ボタンを押されたらループを抜けるコード??
                if event == "end":
                    break
            if event == "end":
                break
            volume_factor = volume(raw_volume)

            for i in range(freq - decay):
                # バイナリデータをnumpy配列に変換
                audio_array = np.frombuffer(data, dtype=np.int16)
                print("音量は",volume_factor)
                adjusted_array = (audio_array * volume_factor).astype(np.int16)

                # 音声データをバイナリに戻す
                adjusted_data = adjusted_array.tobytes()

                # 調整済みの音声を再生

                stream.write(adjusted_data)

                # 次のデータを読み込む
                data = wf.readframes(chunk)

                #########ここに中断ボタンを押されたらループを抜けるコード??
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

        #########ここに中断ボタンを押されたらループを抜けるコード??
        if event == "end":
            break

# メインの処理
if __name__ == "__main__":
    # ロックオブジェクトを作成
    lock = threading.Lock()

    # スレッドを作成
    t1 = threading.Thread(target=get_position_seq)
    t2 = threading.Thread(target=play_audio, args=(freq,))

    # スレッドを開始
    t1.start()
    t2.start()
