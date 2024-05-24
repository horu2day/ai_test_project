import pyaudio
import numpy as np
import whisper
import srt
from datetime import timedelta
import time

# Whisper 모델 로드
model = whisper.load_model("base")

# PyAudio 초기화
p = pyaudio.PyAudio()

# 사용 가능한 오디오 입력 장치 나열 및 선택
print("Available audio input devices:")
device_info = []
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    device_info.append(info)
    print(f"{i}: {info['name']}")

device_index = int(input("Select device index: "))
selected_device_info = device_info[device_index]
channels = selected_device_info['maxInputChannels']
rate = int(selected_device_info['defaultSampleRate'])

# 채널 수 확인 및 설정
if channels < 1:
    channels = 1  # 최소 채널 수 1로 설정

print(f"Selected device: {selected_device_info['name']}")
print(f"Channels: {channels}, Rate: {rate}")

# 오디오 스트림 설정
stream = p.open(format=pyaudio.paInt16,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024)

print("Recording...")

# .srt 자막 생성에 필요한 변수 초기화
subtitles = []
start_time = time.time()
subtitle_index = 1

try:
    while True:
        # 오디오 데이터 읽기
        data = stream.read(1024)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # 오디오 데이터를 float32로 변환
        audio_data = audio_data.astype(np.float32) / 32768.0

        # Whisper 모델로 음성 인식
        result = model.transcribe(audio_data)
        text = result['text']
        
        # 현재 시간 계산
        current_time = time.time()
        start_delta = timedelta(seconds=start_time)
        end_delta = timedelta(seconds=current_time)

        # srt 자막 객체 생성
        subtitle = srt.Subtitle(index=subtitle_index,
                                start=start_delta,
                                end=end_delta,
                                content=text)
        subtitles.append(subtitle)
        subtitle_index += 1

        # .srt 파일에 자막 저장
        with open("output.srt", "w", encoding="utf-8") as f:
            f.write(srt.compose(subtitles))

        # 시작 시간 갱신
        start_time = current_time
except KeyboardInterrupt:
    print("Recording stopped.")

# 스트림 닫기
stream.stop_stream()
stream.close()
p.terminate()
