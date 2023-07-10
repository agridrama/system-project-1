def play_audio(freq):  # 音楽を再生する、音量は1秒おきに少しずつ滑らかに変わるようになってる(中断ボタンに合わせて再生を終了するとかは未実装)
    global position
    global event
    decay = int(freq/2)
    threshold_0 = 0.1  # これを下回ったら非集中と仮定
    threshold_1 = 0.5  # これを上回ったら集中と仮定
    n = 0
    concentration_now = 0
    while True:
        if event == "end":
            break
        file_path = choose_music(concentration_now, threshold_0)
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
        concentration_origin = concentration_now
        print("最初の集中力は", concentration_origin)
        while data:

            # 入力値に基づいて音量を調整
            concentration_prev = concentration_now
            concentration_now = concentration_rate(position)#####################ここを現在の集中力、concentration_rateは消して良し
            
            n += freq

            if concentration_origin < threshold_0 and concentration_now > threshold_1:
                break

            elif concentration_origin > threshold_1 and concentration_now < threshold_0:
                concentration_prev = 0
                break
            
            if concentration_now <= concentration_prev:
                concentration_now = concentration_prev
            concentration_step = (concentration_now - concentration_prev)/decay
            raw_volume = concentration_prev
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