import os
import whisperx
import torch
import tempfile
from pathlib import Path

_original_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

class STTEngine:
    def __init__(self, model_size="turbo"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if torch.cuda.is_available() else "int8"
        
        print(f"🎯 STT инициализирован на устройстве: {self.device}")
        print(f"⏳ Загрузка {model_size}")
        self.model = whisperx.load_model(
            model_size, 
            device=self.device,
            compute_type=self.compute_type
        )
        print("✅ Модель загружена")
        
    # def extract_audio_from_video(self, video_bytes: bytes, original_filename: str) -> str:
    #     """Извлекает аудио из видеофайла и возвращает путь к временному аудиофайлу"""
    #     # Создаем временный видеофайл
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=Path(original_filename).suffix) as video_file:
    #         video_file.write(video_bytes)
    #         video_path = video_file.name
        
    #     # Создаем временный аудиофайл
    #     audio_path = video_path + "_extracted_audio.wav"
        
    #     try:
    #         # Используем ffmpeg для извлечения аудио
    #         command = [
    #             'ffmpeg',
    #             '-i', video_path,
    #             '-vn',  # без видео
    #             '-acodec', 'pcm_s16le',  # кодек для WAV
    #             '-ar', '16000',  # частота дискретизации
    #             '-ac', '1',  # моно
    #             '-y',  # перезаписать если файл существует
    #             audio_path
    #         ]
            
    #         result = subprocess.run(command, capture_output=True, text=True)
    #         if result.returncode != 0:
    #             raise Exception(f"Ошибка извлечения аудио: {result.stderr}")
            
    #         return audio_path
            
    #     finally:
    #         # Удаляем временный видеофайл
    #         if os.path.exists(video_path):
    #             os.unlink(video_path)
    
    def transcribe(self, tmp_file_path: Path, language: str = "ru", file_type: str = "audio") -> str:
        # if file_type == "audio":
        # with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        #     f.write(file_bytes)
        #     temp_path = f.name
        # else:
        #     self.extract_audio_from_video(file_bytes, )
             
        try:
            audio = whisperx.load_audio(str(tmp_file_path))
            result = self.model.transcribe(audio, language=language)
            
            return result
        
        finally:
            tmp_file_path.unlink(missing_ok = True)
