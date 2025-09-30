"""
Celery tasks for audio processing (transcription, diarization).
Designer: Abdullah Alawiss
"""

import os
import time
import whisper
import ffmpeg
from datetime import datetime
from typing import Dict, Any, List
from celery import current_task
from sqlalchemy.orm import Session

from ..core.celery_config import celery_app
from ..core.database import SessionLocal
from ..models.call import Call, CallTranscript, Speaker, ProcessingTask
from ..services.audio_service import AudioService
from ..services.diarization_service import DiarizationService

@celery_app.task(bind=True, name="process_audio_file")
def process_audio_file(self, call_id: int) -> Dict[str, Any]:
    """
    Main task to process an audio file completely.
    Steps: validate -> normalize -> transcribe -> diarize -> analyze -> persist
    """
    db = SessionLocal()
    task_id = self.request.id
    
    try:
        # Update task status
        task = ProcessingTask(
            task_id=task_id,
            call_id=call_id,
            task_type="full_processing",
            status="running",
            started_at=datetime.utcnow(),
            current_step="initializing"
        )
        db.add(task)
        db.commit()
        
        # Get call record
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise Exception(f"Call with ID {call_id} not found")
        
        call.status = "processing"
        db.commit()
        
        # Step 1: Audio validation and normalization
        current_task.update_state(
            state="PROGRESS",
            meta={"current_step": "audio_validation", "progress": 10}
        )
        task.current_step = "audio_validation"
        task.progress_percentage = 10
        db.commit()
        
        audio_service = AudioService()
        normalized_path = audio_service.validate_and_normalize(call.file_path)
        
        # Get audio metadata
        metadata = audio_service.get_audio_metadata(normalized_path)
        call.duration_seconds = metadata.get("duration")
        call.sample_rate = metadata.get("sample_rate")
        call.channels = metadata.get("channels")
        db.commit()
        
        # Step 2: Transcription with Whisper
        current_task.update_state(
            state="PROGRESS", 
            meta={"current_step": "transcription", "progress": 30}
        )
        task.current_step = "transcription"
        task.progress_percentage = 30
        db.commit()
        
        transcript_result = transcribe_audio.delay(call_id, normalized_path).get()
        
        # Step 3: Speaker Diarization
        current_task.update_state(
            state="PROGRESS",
            meta={"current_step": "diarization", "progress": 60}
        )
        task.current_step = "diarization"
        task.progress_percentage = 60
        db.commit()
        
        diarization_result = diarize_audio.delay(call_id, normalized_path).get()
        
        # Step 4: Analysis
        current_task.update_state(
            state="PROGRESS",
            meta={"current_step": "analysis", "progress": 80}
        )
        task.current_step = "analysis"
        task.progress_percentage = 80
        db.commit()
        
        from .analysis_tasks import analyze_call
        analysis_result = analyze_call.delay(call_id).get()
        
        # Step 5: GDPR Processing
        current_task.update_state(
            state="PROGRESS",
            meta={"current_step": "gdpr_processing", "progress": 90}
        )
        task.current_step = "gdpr_processing"
        task.progress_percentage = 90
        db.commit()
        
        from .gdpr_tasks import redact_sensitive_data
        gdpr_result = redact_sensitive_data.delay(call_id).get()
        
        # Final step: Mark as completed
        call.status = "completed"
        call.processed_at = datetime.utcnow()
        
        task.status = "completed"
        task.progress_percentage = 100
        task.current_step = "completed"
        task.completed_at = datetime.utcnow()
        task.result = {
            "transcript": transcript_result,
            "diarization": diarization_result, 
            "analysis": analysis_result,
            "gdpr": gdpr_result
        }
        
        db.commit()
        
        # Clean up temporary files
        if os.path.exists(normalized_path) and normalized_path != call.file_path:
            os.remove(normalized_path)
        
        return {
            "status": "completed",
            "call_id": call_id,
            "processing_time": time.time(),
            "steps_completed": ["validation", "transcription", "diarization", "analysis", "gdpr"]
        }
        
    except Exception as e:
        # Handle errors
        if 'call' in locals():
            call.status = "failed"
            db.commit()
        
        if 'task' in locals():
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.commit()
        
        raise e
    
    finally:
        db.close()

@celery_app.task(bind=True, name="transcribe_audio")
def transcribe_audio(self, call_id: int, audio_path: str) -> Dict[str, Any]:
    """Transcribe audio using Whisper."""
    db = SessionLocal()
    
    try:
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise Exception(f"Call with ID {call_id} not found")
        
        # Load Whisper model
        from ..core.config import settings
        model = whisper.load_model(settings.WHISPER_MODEL)
        
        start_time = time.time()
        
        # Transcribe with timestamps
        result = model.transcribe(
            audio_path,
            language="no",  # Norwegian
            task="transcribe",
            verbose=True,
            word_timestamps=True
        )
        
        processing_time = time.time() - start_time
        
        # Create transcript record
        transcript = CallTranscript(
            call_id=call_id,
            raw_text=result["text"],
            language=result.get("language", "no"),
            confidence=result.get("confidence", 0.0),
            segments=result.get("segments", []),
            whisper_model=settings.WHISPER_MODEL,
            processing_time_seconds=processing_time
        )
        
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        return {
            "transcript_id": transcript.id,
            "text": result["text"],
            "language": result.get("language"),
            "segments_count": len(result.get("segments", [])),
            "processing_time": processing_time
        }
        
    except Exception as e:
        raise e
    finally:
        db.close()

@celery_app.task(bind=True, name="diarize_audio") 
def diarize_audio(self, call_id: int, audio_path: str) -> Dict[str, Any]:
    """Perform speaker diarization on audio."""
    db = SessionLocal()
    
    try:
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise Exception(f"Call with ID {call_id} not found")
        
        # Perform diarization
        diarization_service = DiarizationService()
        diarization_result = diarization_service.diarize(audio_path)
        
        speakers_created = []
        
        # Process each speaker
        for speaker_id, segments in diarization_result.items():
            total_speaking_time = sum(
                segment["end"] - segment["start"] for segment in segments
            )
            
            # Determine speaker label (basic heuristic)
            speaker_label = "Agent" if speaker_id == "SPEAKER_00" else "Customer"
            
            speaker = Speaker(
                call_id=call_id,
                speaker_id=speaker_id,
                speaker_label=speaker_label,
                segments=segments,
                total_speaking_time=total_speaking_time
            )
            
            db.add(speaker)
            speakers_created.append({
                "speaker_id": speaker_id,
                "label": speaker_label,
                "segments_count": len(segments),
                "total_speaking_time": total_speaking_time
            })
        
        db.commit()
        
        return {
            "speakers_count": len(speakers_created),
            "speakers": speakers_created
        }
        
    except Exception as e:
        raise e
    finally:
        db.close()

@celery_app.task(bind=True, name="extract_audio_metadata")
def extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
    """Extract metadata from audio file using ffmpeg."""
    
    try:
        probe = ffmpeg.probe(file_path)
        
        # Get audio stream info
        audio_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
            None
        )
        
        if not audio_stream:
            raise Exception("No audio stream found in file")
        
        metadata = {
            "duration": float(probe['format']['duration']),
            "size": int(probe['format']['size']),
            "bit_rate": int(probe['format'].get('bit_rate', 0)),
            "format_name": probe['format']['format_name'],
            "sample_rate": int(audio_stream.get('sample_rate', 0)),
            "channels": int(audio_stream.get('channels', 0)),
            "codec": audio_stream.get('codec_name'),
            "bit_depth": audio_stream.get('bits_per_sample')
        }
        
        return metadata
        
    except Exception as e:
        raise Exception(f"Failed to extract metadata: {str(e)}")
