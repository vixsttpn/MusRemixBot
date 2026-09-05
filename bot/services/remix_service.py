"""Audio processing and remix service"""
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Optional
from ..models import RemixType

logger = logging.getLogger(__name__)


class RemixService:
    """Сервис для создания ремиксов"""
    
    # FFmpeg фильтры для каждого типа обработки
    REMIX_FILTERS = {
        RemixType.ORIGINAL: "",
        
        RemixType.SLOWED: (
            "atempo=0.85,"
            "asetrate=48000*0.92,"
            "aresample=48000:resampler=soxr,"
            "lowpass=f=12000,"
            "volume=0.95"
        ),
        
        RemixType.SPED_UP: (
            "atempo=1.30,"
            "asetrate=48000*1.20,"
            "aresample=48000:resampler=soxr,"
            "volume=1.05"
        ),
        
        RemixType.BASS_BOOSTED: (
            "bass=g=20:f=85:w=0.5,"
            "equalizer=f=55:width_type=o:width=1.2:g=10,"
            "equalizer=f=110:width_type=o:width=0.8:g=6,"
            "lowpass=f=18000,"
            "acompressor=threshold=-12dB:ratio=2.5:attack=2:release=100,"
            "volume=1.1"
        ),
        
        RemixType.NIGHTCORE: (
            "atempo=1.25,"
            "asetrate=48000*1.20,"
            "aresample=48000:resampler=soxr,"
            "highpass=f=120,"
            "volume=1.05"
        ),
        
        RemixType.REVERB: (
            "aecho=0.8:0.9:80:0.40,"
            "aecho=0.65:0.75:180:0.30,"
            "lowpass=f=8000,"
            "volume=0.90"
        ),
        
        RemixType.LOFI: (
            "lowpass=f=3200,"
            "highpass=f=200,"
            "equalizer=f=1000:width_type=o:width=1.5:g=-2,"
            "volume=0.85"
        ),
        
        RemixType.ACOUSTIC: (
            "highpass=f=180:width_type=h:width=1,"
            "lowpass=f=7000:width_type=h:width=1,"
            "volume=1.0"
        ),
        
        RemixType.INSTRUMENTAL: (
            # Простое подавление вокала
            "extrastereo=m=-1.0,"
            "volume=1.0"
        ),
        
        RemixType.LIVE: (
            "aecho=0.4:0.5:40:0.25,"
            "volume=0.95"
        ),
    }
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_remix(
        self,
        input_path: Path,
        output_path: Path,
        remix_type: RemixType,
        timeout: int = 120
    ) -> bool:
        """
        Создать ремикс
        
        Args:
            input_path: путь к исходному файлу
            output_path: путь для сохранения
            remix_type: тип обработки
            timeout: таймаут в секундах
        
        Returns:
            True если успешно
        """
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return False
        
        # Original - просто копируем
        if remix_type == RemixType.ORIGINAL:
            try:
                import shutil
                shutil.copy2(input_path, output_path)
                logger.info(f"Original saved to {output_path}")
                return True
            except Exception as e:
                logger.error(f"Copy error: {e}")
                return False
        
        # Получить фильтр для данного типа
        filter_str = self.REMIX_FILTERS.get(remix_type, "")
        if not filter_str:
            logger.error(f"Unknown remix type: {remix_type}")
            return False
        
        # Построить FFmpeg команду
        cmd = self._build_ffmpeg_command(
            input_path,
            output_path,
            filter_str
        )
        
        logger.info(f"Creating {remix_type.value} remix...")
        
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                _, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                logger.error(f"FFmpeg timeout for {remix_type.value}")
                return False
            
            if process.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"Remix created: {output_path}")
                return True
            else:
                error = stderr.decode(errors='ignore')[-500:] if stderr else "Unknown error"
                logger.error(f"FFmpeg error: {error}")
                return False
        
        except Exception as e:
            logger.error(f"Remix creation error: {e}")
            return False
    
    @staticmethod
    def _build_ffmpeg_command(
        input_path: Path,
        output_path: Path,
        filter_str: str
    ) -> str:
        """Построить FFmpeg команду"""
        if filter_str:
            return (
                f'ffmpeg -y -i "{input_path}" '
                f'-vn -af "{filter_str}" '
                f'-c:a libmp3lame -b:a 320k -ar 48000 '
                f'"{output_path}"'
            )
        else:
            return (
                f'ffmpeg -y -i "{input_path}" '
                f'-vn -c:a libmp3lame -b:a 320k -ar 48000 '
                f'"{output_path}"'
            )
    
    async def validate_audio(self, file_path: Path) -> bool:
        """
        Проверить качество аудиофайла
        
        Args:
            file_path: путь к файлу
        
        Returns:
            True если файл валидный
        """
        if not file_path.exists() or file_path.stat().st_size == 0:
            logger.error(f"Invalid file: {file_path}")
            return False
        
        try:
            cmd = (
                f'ffprobe -v error -select_streams a:0 '
                f'-show_entries stream=codec_type,duration '
                f'-of default=noprint_wrappers=1 "{file_path}"'
            )
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=10
            )
            
            output = stdout.decode()
            
            # Проверяем, что это аудиопоток
            if 'codec_type=audio' in output:
                logger.info(f"Audio file validated: {file_path}")
                return True
            else:
                logger.error(f"Not an audio file: {file_path}")
                return False
        
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    async def get_duration(self, file_path: Path) -> int:
        """
        Получить длительность аудиофайла
        
        Args:
            file_path: путь к файлу
        
        Returns:
            Длительность в секундах или 0
        """
        try:
            cmd = (
                f'ffprobe -v error -show_entries format=duration '
                f'-of default=noprint_wrappers=1:nokey=1 "{file_path}"'
            )
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=10
            )
            
            duration_str = stdout.decode().strip()
            return int(float(duration_str)) if duration_str else 0
        
        except Exception as e:
            logger.error(f"Duration error: {e}")
            return 0
