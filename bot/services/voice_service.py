"""Voice recognition service"""
import logging
import asyncio
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VoiceService:
    """Сервис для распознавания голоса"""
    
    def __init__(self, yandex_key: Optional[str] = None, google_key: Optional[str] = None):
        self.yandex_key = yandex_key
        self.google_key = google_key
    
    async def recognize_voice(
        self,
        audio_path: Path,
        language: str = "ru-RU"
    ) -> Optional[str]:
        """
        Распознать текст из аудиофайла
        
        Args:
            audio_path: путь к audio файлу
            language: язык для распознавания
        
        Returns:
            Распознанный текст или None
        """
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        # Попробовать Yandex SpeechKit
        if self.yandex_key:
            result = await self._recognize_yandex(audio_path, language)
            if result:
                return result
        
        # Fallback: простое распознавание через Telegram
        logger.warning("No voice recognition service available")
        return None
    
    async def _recognize_yandex(
        self,
        audio_path: Path,
        language: str
    ) -> Optional[str]:
        """Распознавание через Yandex SpeechKit"""
        try:
            import aiohttp
            
            url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
            
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            headers = {
                'Authorization': f'Bearer {self.yandex_key}',
            }
            
            params = {
                'topic': 'general',
                'language_code': language,
                'format': 'lpcm',
                'sample_rate_hertz': '16000',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=audio_data,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = data.get('result', '')
                        if result:
                            logger.info(f"Voice recognized: {result}")
                            return result
                    else:
                        logger.error(f"Yandex API error: {resp.status}")
        
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
        
        return None
    
    async def _recognize_google(
        self,
        audio_path: Path,
        language: str
    ) -> Optional[str]:
        """Распознавание через Google Speech-to-Text"""
        try:
            from google.cloud import speech_v1
            import google.auth
            
            client = speech_v1.SpeechClient()
            
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            audio = speech_v1.RecognitionAudio(content=audio_data)
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                logger.info(f"Voice recognized: {transcript}")
                return transcript
        
        except ImportError:
            logger.warning("Google Cloud Speech not installed")
        except Exception as e:
            logger.error(f"Google Speech error: {e}")
        
        return None
