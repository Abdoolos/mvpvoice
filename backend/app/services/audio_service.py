"""
Audio processing service for validation, normalization, and metadata extraction.
Designer: Abdullah Alawiss
"""

import os
import ffmpeg
from typing import Dict, Any
from ..core.config import settings

class AudioService:
    """Service for audio file processing operations."""
    
    def validate_and_normalize(self, file_path: str) -> str:
        """
        Validate audio file and normalize it for processing.
        Returns path to normalized file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > settings.MAX_CONTENT_LENGTH:
            raise ValueError(f"File too large: {file_size} bytes")
        
        # Get audio metadata to validate
        metadata = self.get_audio_metadata(file_path)
        
        if metadata["duration"] > settings.MAX_AUDIO_DURATION:
            raise ValueError(f"Audio too long: {metadata['duration']} seconds")
        
        # Normalize audio (convert to standard format)
        normalized_path = self._normalize_audio(file_path)
        
        return normalized_path
    
    def get_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from audio file."""
        try:
            probe = ffmpeg.probe(file_path)
            
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )
            
            if not audio_stream:
                raise ValueError("No audio stream found")
            
            return {
                "duration": float(probe['format']['duration']),
                "size": int(probe['format']['size']),
                "sample_rate": int(audio_stream.get('sample_rate', 0)),
                "channels": int(audio_stream.get('channels', 0)),
                "codec": audio_stream.get('codec_name'),
                "bit_rate": int(probe['format'].get('bit_rate', 0))
            }
            
        except Exception as e:
            raise ValueError(f"Failed to extract metadata: {str(e)}")
    
    def _normalize_audio(self, file_path: str) -> str:
        """Normalize audio to standard format for processing."""
        file_dir = os.path.dirname(file_path)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        normalized_path = os.path.join(file_dir, f"{file_name}_normalized.wav")
        
        try:
            # Convert to 16kHz mono WAV for Whisper
            (
                ffmpeg
                .input(file_path)
                .output(
                    normalized_path,
                    acodec='pcm_s16le',
                    ac=1,  # mono
                    ar=16000  # 16kHz sample rate
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            return normalized_path
            
        except Exception as e:
            raise ValueError(f"Failed to normalize audio: {str(e)}")
