"""
Pydantic schemas for call-related API responses.
Designer: Abdullah Alawiss
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel

class CallBase(BaseModel):
    """Base call schema with common fields."""
    filename: str
    original_filename: str
    file_size: int
    duration_seconds: Optional[float] = None
    status: str
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None

class CallResponse(CallBase):
    """Schema for call response in lists."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class TranscriptResponse(BaseModel):
    """Schema for transcript data."""
    id: int
    call_id: int
    raw_text: str
    processed_text: Optional[str] = None
    language: Optional[str] = None
    confidence: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None
    whisper_model: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class SpeakerResponse(BaseModel):
    """Schema for speaker diarization data."""
    id: int
    call_id: int
    speaker_id: str
    speaker_label: Optional[str] = None
    segments: List[Dict[str, Any]]
    total_speaking_time: Optional[float] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class AnalysisResponse(BaseModel):
    """Schema for call analysis data."""
    id: int
    call_id: int
    overall_result: str
    confidence_score: Optional[float] = None
    violations: Optional[List[Dict[str, Any]]] = None
    bindingstid_mentioned: bool
    bindingstid_details: Optional[Dict[str, Any]] = None
    pris_mentioned: bool
    pris_details: Optional[Dict[str, Any]] = None
    press_mentioned: bool
    press_details: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class CallDetailResponse(CallResponse):
    """Detailed call response with all related data."""
    transcript: Optional[TranscriptResponse] = None
    analysis: Optional[AnalysisResponse] = None
    speakers: List[SpeakerResponse] = []
    
    class Config:
        orm_mode = True

class CallListResponse(BaseModel):
    """Response for paginated call lists."""
    calls: List[CallResponse]
    total: int
    skip: int
    limit: int

class UploadResponse(BaseModel):
    """Response for file upload."""
    call_id: int
    filename: str
    original_filename: str
    file_size: int
    status: str
    message: str

class ProcessingTaskResponse(BaseModel):
    """Response for processing task status."""
    task_id: str
    call_id: Optional[int] = None
    task_type: str
    status: str
    progress_percentage: int
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        orm_mode = True

class StatsResponse(BaseModel):
    """Response for dashboard statistics."""
    total_calls: int
    completed_calls: int
    failed_calls: int
    processing_calls: int
    good_calls: int
    bad_calls: int
    total_duration_minutes: float
    avg_processing_time_seconds: float
    top_violations: List[Dict[str, Any]]
