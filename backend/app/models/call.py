"""
Database models for calls and related entities.
Designer: Abdullah Alawiss
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Call(Base):
    """Model for call records."""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded", index=True)  # uploaded, processing, completed, failed
    
    # Audio metadata
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    format = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transcript = relationship("CallTranscript", back_populates="call", uselist=False)
    analysis = relationship("CallAnalysis", back_populates="call", uselist=False)
    speakers = relationship("Speaker", back_populates="call")

class CallTranscript(Base):
    """Model for call transcripts."""
    __tablename__ = "call_transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    
    # Transcript content
    raw_text = Column(Text, nullable=False)
    processed_text = Column(Text, nullable=True)  # After GDPR redaction
    
    # Whisper metadata
    language = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Segmented transcript with timestamps
    segments = Column(JSON, nullable=True)  # Array of segment objects
    
    # Processing info
    whisper_model = Column(String, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    call = relationship("Call", back_populates="transcript")

class Speaker(Base):
    """Model for speaker diarization results."""
    __tablename__ = "speakers"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    
    # Speaker identification
    speaker_id = Column(String, nullable=False)  # e.g., "SPEAKER_00", "SPEAKER_01"
    speaker_label = Column(String, nullable=True)  # e.g., "Agent", "Customer"
    
    # Speaking segments
    segments = Column(JSON, nullable=False)  # Array of time segments
    total_speaking_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    call = relationship("Call", back_populates="speakers")

class CallAnalysis(Base):
    """Model for call analysis results."""
    __tablename__ = "call_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    
    # Overall analysis
    overall_result = Column(String, nullable=False)  # "good" or "bad"
    confidence_score = Column(Float, nullable=True)
    
    # Rule violations
    violations = Column(JSON, nullable=True)  # Array of violation objects
    
    # Analysis details
    bindingstid_mentioned = Column(Boolean, default=False)
    bindingstid_details = Column(JSON, nullable=True)
    
    pris_mentioned = Column(Boolean, default=False)
    pris_details = Column(JSON, nullable=True)
    
    press_mentioned = Column(Boolean, default=False)
    press_details = Column(JSON, nullable=True)
    
    # Summary
    summary = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)  # Array of key points
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    call = relationship("Call", back_populates="analysis")

class ProcessingTask(Base):
    """Model for tracking processing tasks."""
    __tablename__ = "processing_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    
    # Task details
    task_id = Column(String, unique=True, index=True, nullable=False)  # Celery task ID
    task_type = Column(String, nullable=False)  # transcribe, diarize, analyze, etc.
    status = Column(String, default="pending")  # pending, running, completed, failed
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String, nullable=True)
    
    # Results and errors
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
