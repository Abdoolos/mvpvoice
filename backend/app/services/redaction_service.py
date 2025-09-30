"""
GDPR-compliant data redaction service.
Designer: Abdullah Alawiss
"""

from typing import Dict, Any, List
from ..workers.gdpr_tasks import detect_personal_data, apply_redactions

class RedactionService:
    """Service for GDPR-compliant data redaction."""
    
    def redact_transcript(self, text: str, segments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Redact sensitive data from transcript text.
        """
        # Detect personal data
        detections = detect_personal_data.delay(text).get()
        
        # Apply redactions
        redacted_result = apply_redactions.delay(text, detections).get()
        
        # Also redact segments if provided
        redacted_segments = []
        if segments:
            for segment in segments:
                segment_text = segment.get("text", "")
                if segment_text:
                    segment_detections = detect_personal_data.delay(segment_text).get()
                    segment_redacted = apply_redactions.delay(segment_text, segment_detections).get()
                    
                    # Update segment with redacted text
                    redacted_segment = segment.copy()
                    redacted_segment["text"] = segment_redacted["redacted_text"]
                    redacted_segments.append(redacted_segment)
                else:
                    redacted_segments.append(segment)
        
        return {
            "redacted_text": redacted_result["redacted_text"],
            "redacted_segments": redacted_segments,
            "redactions_count": redacted_result["redactions_count"],
            "redaction_types": redacted_result["redaction_types"]
        }
