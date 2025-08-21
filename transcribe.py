#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import whisper
import sys
import os
from imageio_ffmpeg import get_ffmpeg_exe


ffmpeg_path = r"C:\Users\kgm20\Desktop\mp3_to_txt transcription\.venv\Lib\site-packages\imageio_ffmpeg\binaries"

# Добавляем ffmpeg в PATH
os.environ["PATH"] += os.pathsep + ffmpeg_path
# Также укажем для imageio
os.environ["IMAGEIO_FFMPEG_EXE"] = os.path.join(ffmpeg_path, "ffmpeg.exe")


def convert_mp3_to_wav(mp3_path: str, wav_path: str):
    """
    Конвертирует MP3 в WAV (16 kHz, моно) через встроенный ffmpeg из imageio-ffmpeg.
    """
    ffmpeg_exe = get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-y",               # перезаписывать выходной файл, если уже существует
        "-i", mp3_path,     # входной файл
        "-ar", "16000",     # частота дискретизации 16 kHz
        "-ac", "1",         # 1 канал (моно)
        wav_path
    ]
    try:
        # stdout/stderr можно убрать, если хочется видеть логи ffmpeg
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("Ошибка конвертации через ffmpeg:", e)
        sys.exit(1)


def transcribe_audio(wav_path: str, model_size: str = "small", language: str = None) -> str:
    """
    Транскрибирует WAV-файл в текст.
    model_size: tiny, base, small, medium, large
    language: ISO-код языка, например "ru" (необязательно)
    """
    model = whisper.load_model(model_size)
    options = {}
    if language:
        options["language"] = language
    result = model.transcribe(wav_path, **options)
    return result["text"]


def main():
    if len(sys.argv) < 2:
        print("Использование: python transcribe.py <input.mp3> [<model_size>] [<language>]")
        sys.exit(1)

    mp3_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) >= 3 else "small"
    language   = sys.argv[3] if len(sys.argv) >= 4 else None

    if not os.path.isfile(mp3_path):
        print(f"Файл не найден: {mp3_path}")
        sys.exit(1)

    base     = os.path.splitext(mp3_path)[0]
    wav_path = base + ".wav"
    txt_path = base + ".txt"

    print("Конвертация mp3 → wav через встроенный ffmpeg…")
    convert_mp3_to_wav(mp3_path, wav_path)

    print(f"Загрузка модели Whisper (‘{model_size}’) и транскрибация…")
    text = transcribe_audio(wav_path, model_size, language)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Готово! Результат сохранён в {txt_path}")

if __name__ == "__main__":
    main()
