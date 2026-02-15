import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import asyncio
import edge_tts
import simpleaudio as sa
import time
import os

# ================== 配置 ==================
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_DURATION = 0.1          # 100ms
SILENCE_THRESHOLD = 0.015     # 🔴 关键：控制是否“算说话”
SILENCE_TIMEOUT = 1.2         # 连续静音多久算说完
MIN_VOICE_DURATION = 0.8      # 太短不算
TMP_WAV = "input.wav"
API_URL = "http://127.0.0.1:8000/ai_assistant/receive_audio_and_response/"
MIC_INDEX = 1                 # 你的麦克风索引

# ================== Edge TTS ==================
async def speak(text):
    print("🤖 AI:", text)
    tts = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
    await tts.save("reply.mp3")
    wave_obj = sa.WaveObject.from_wave_file(
        convert_mp3_to_wav("reply.mp3")
    )
    wave_obj.play().wait_done()

def convert_mp3_to_wav(mp3):
    import subprocess
    wav_path = "reply.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", mp3, wav_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return wav_path


def send_to_django(wav_path):
    with open(wav_path, "rb") as f:
        files = {"audio": f}
        r = requests.post(API_URL, files=files)
    if r.status_code == 200:
        return r.json().get("reply", "")
    return "Server error"

def listen_and_record():
    print("🎧 Listening（wait to speak）...")

    frames = []
    recording = False
    silence_time = 0.0
    voice_time = 0.0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=int(SAMPLE_RATE * BLOCK_DURATION),
        device=MIC_INDEX
    ) as stream:

        while True:
            data, _ = stream.read(int(SAMPLE_RATE * BLOCK_DURATION))
            volume = np.max(np.abs(data))

            if volume > SILENCE_THRESHOLD:
                if not recording:
                    print("🗣️ Detected speak，start recording")
                    recording = True
                frames.append(data.copy())
                voice_time += BLOCK_DURATION
                silence_time = 0.0
            else:
                if recording:
                    silence_time += BLOCK_DURATION
                    if silence_time >= SILENCE_TIMEOUT:
                        print("🛑 Detected mute，stop recording")
                        break

    if voice_time < MIN_VOICE_DURATION:
        print("🤫 Sound too short，delete it")
        return None

    audio = np.concatenate(frames, axis=0)
    wav.write(TMP_WAV, SAMPLE_RATE, audio)
    return TMP_WAV

# ================== 主循环 ==================
async def main():
    await speak("I'm ready.")

    while True:
        wav_path = listen_and_record()
        if wav_path is None:
            continue

        print("📤 Send to server...")
        reply = send_to_django(wav_path)
        if reply is not None:
            await speak(reply)

        time.sleep(0.3)

if __name__ == "__main__":
    asyncio.run(main())






# import sounddevice as sd
# import numpy as np
# duration = 5 # 秒
# fs = 16000
# print("开始录音...")
# mydata = sd.rec(int(duration * fs), samplerate=fs, channels=1,
# dtype='float32', device=1) # 改成你的索引
# sd.wait()
# print("录音结束，最大音量:", np.max(np.abs(mydata)))


