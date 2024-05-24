import os
import tkinter as tk
from tkinter import filedialog
import whisper
from whisper.utils import get_writer
from deep_translator import GoogleTranslator
import time


def split_text(file_path, max_length=5000):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    parts = []
    while text:
        part = text[:max_length]
        next_index = part.rfind('\n')
        if next_index == -1 or len(text) <= max_length:
            next_index = max_length
        parts.append(text[:next_index])
        text = text[next_index:].lstrip()

    return parts


def translate_text(parts, target_language='ko'):
    translator = GoogleTranslator(source='auto', target=target_language)
    return [translator.translate(part) for part in parts]

def save_translated_text(translated_parts, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(translated_parts))


def get_all_files_in_directory(directory):
    all_files = []

    # os.walk()를 사용하여 주어진 디렉토리와 모든 하위 디렉토리를 순회합니다.
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 각 파일의 전체 경로를 all_files 리스트에 추가합니다.
            all_files.append(os.path.join(root, file))

    return all_files


# Open a folder selection dialog
root = tk.Tk()
root.withdraw()  # Hide the main window
directory = filedialog.askdirectory()  # Open the folder selection dialog
cnt = 1
# Iterate over all files in the directory
for root, dirs, files in os.walk(directory):
    for filename in files:
        # Check if the file is a .mp4 file
        if os.path.splitext(filename)[1] in ['.mp4', '.mp3', '.flac', '.wav', '.aac']:
            video_file_path = os.path.join(root, filename)
            # print(root + " : " + dirs + " : " + filename)
            # Check the file size and load the appropriate Whisper model
            file_size_mb = os.path.getsize(
                video_file_path) / (1024 * 1024)  # File size in megabytes
            if file_size_mb < 74:
                model = whisper.load_model("base")
                print(filename + ": base")
            elif file_size_mb < 244:
                model = whisper.load_model("small")
                print(filename + "small")
            else:
                model = whisper.load_model("medium")
                print(filename + "medium")

            # Transcribe the audio from the video file

            result = model.transcribe(video_file_path, language='en')

            # Translate each segment

            for segment in result['segments']:
                if cnt % 150 == 0:
                    time.sleep(10)
                translated_text = GoogleTranslator(
                    source='auto', target='korean').translate(text=segment['text'])
                segment['text'] = translated_text
                print(segment['text'])
                cnt += 1

            # get srt writer for the current directory
            writer = get_writer("srt", root)
            options = {"max_line_width": 10000,
                       "max_line_count": 10000, "highlight_words": True}
            writer(result, video_file_path, options)
            path = os.path.realpath(directory)
            os.startfile(path)
        elif os.path.splitext(filename)[1] in ['.txt']:
            doc_file_path = os.path.join(root, filename )
            # file_size_mb = os.path.getsize(
            #     doc_file_path) / (1024 * 1024)  # File size in megabytes

            doc_file_path = os.path.join(root, filename)

            # 파일 분할 및 번역
            parts = split_text(doc_file_path)
            translated_parts = translate_text(parts)

            # 번역된 텍스트 저장
            result_path = os.path.join(root, "ko_" + filename)
            save_translated_text(translated_parts, result_path)

            # 완료된 디렉토리 열기
            path = os.path.realpath(root)
            os.startfile(path)
