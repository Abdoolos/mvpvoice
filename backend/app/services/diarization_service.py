"""
Speaker diarization service using pyannote.audio.
Designer: Abdullah Alawiss
"""

from typing import Dict, Any, List

# Try to import optional dependencies
try:
    import torch
    from pyannote.audio import Pipeline
    from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    torch = None
    Pipeline = None
    PretrainedSpeakerEmbedding = None

class DiarizationService:
    """Service for speaker diarization using pyannote.audio."""
    
    def __init__(self):
        """Initialize the diarization pipeline."""
        if not PYANNOTE_AVAILABLE:
            print("Warning: pyannote.audio not available, using mock implementation")
            self.pipeline = None
            return
            
        try:
            # Initialize pyannote pipeline
            self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
            
            # Set device (GPU if available)
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.pipeline = self.pipeline.to(device)
            
        except Exception as e:
            # Fallback to mock implementation for development
            print(f"Warning: Could not initialize pyannote pipeline: {e}")
            self.pipeline = None
    
    def diarize(self, audio_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform speaker diarization on audio file.
        Returns dictionary mapping speaker IDs to their speaking segments.
        """
        if self.pipeline is None:
            # Mock implementation for development/testing
            return self._mock_diarization(audio_path)
        
        try:
            # Apply diarization pipeline
            diarization = self.pipeline(audio_path)
            
            # Convert to our format
            speakers = {}
            
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                if speaker not in speakers:
                    speakers[speaker] = []
                
                speakers[speaker].append({
                    "start": turn.start,
                    "end": turn.end,
                    "duration": turn.end - turn.start,
                    "confidence": 0.8  # Default confidence
                })
            
            return speakers
            
        except Exception as e:
            # Fallback to mock on error
            print(f"Diarization failed: {e}, using mock data")
            return self._mock_diarization(audio_path)
    
    def _mock_diarization(self, audio_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Mock diarization for development/testing.
        Creates fake speaker segments.
        """
        # Get audio duration (simplified)
        try:
            import ffmpeg
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['format']['duration'])
        except:
            duration = 120.0  # Default 2 minutes
        
        # Create mock segments for 2 speakers
        speakers = {
            "SPEAKER_00": [  # Agent
                {"start": 0.0, "end": 5.2, "duration": 5.2, "confidence": 0.9},
                {"start": 12.1, "end": 18.7, "duration": 6.6, "confidence": 0.85},
                {"start": 25.3, "end": 35.8, "duration": 10.5, "confidence": 0.92},
                {"start": 42.1, "end": 48.9, "duration": 6.8, "confidence": 0.88}
            ],
            "SPEAKER_01": [  # Customer
                {"start": 5.2, "end": 12.1, "duration": 6.9, "confidence": 0.87},
                {"start": 18.7, "end": 25.3, "duration": 6.6, "confidence": 0.91},
                {"start": 35.8, "end": 42.1, "duration": 6.3, "confidence": 0.89}
            ]
        }
        
        # Adjust to actual duration if needed
        if duration > 60:
            # Add more segments for longer calls
            speakers["SPEAKER_00"].extend([
                {"start": 55.2, "end": 62.8, "duration": 7.6, "confidence": 0.86},
                {"start": 70.1, "end": 78.5, "duration": 8.4, "confidence": 0.93}
            ])
            speakers["SPEAKER_01"].extend([
                {"start": 48.9, "end": 55.2, "duration": 6.3, "confidence": 0.84},
                {"start": 62.8, "end": 70.1, "duration": 7.3, "confidence": 0.90}
            ])
        
        return speakers
    
    def merge_overlapping_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge overlapping or very close segments for the same speaker."""
        if not segments:
            return segments
        
        # Sort segments by start time
        sorted_segments = sorted(segments, key=lambda x: x["start"])
        merged = [sorted_segments[0]]
        
        for current in sorted_segments[1:]:
            last_merged = merged[-1]
            
            # If segments overlap or are very close (within 0.5 seconds)
            if current["start"] <= last_merged["end"] + 0.5:
                # Merge segments
                last_merged["end"] = max(last_merged["end"], current["end"])
                last_merged["duration"] = last_merged["end"] - last_merged["start"]
                # Average confidence
                last_merged["confidence"] = (last_merged["confidence"] + current["confidence"]) / 2
            else:
                merged.append(current)
        
        return merged
    
    def get_speaker_statistics(self, speakers: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics for each speaker."""
        stats = {}
        
        for speaker_id, segments in speakers.items():
            total_time = sum(segment["duration"] for segment in segments)
            avg_confidence = sum(segment["confidence"] for segment in segments) / len(segments)
            
            stats[speaker_id] = {
                "total_speaking_time": total_time,
                "segment_count": len(segments),
                "average_confidence": avg_confidence,
                "average_segment_length": total_time / len(segments) if segments else 0
            }
        
        return stats
