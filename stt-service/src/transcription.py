import os
import whisperx
import torch
import tempfile

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
    
    def transcribe(self, audio_bytes: bytes, language: str = "ru") -> str:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            audio = whisperx.load_audio(temp_path)
            result = self.model.transcribe(audio, language=language)
            
            text = " ".join(segment["text"] for segment in result["segments"])
            return text
        
        finally:
            os.unlink(temp_path)
