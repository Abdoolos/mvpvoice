"""
Celery tasks for GDPR compliance and data redaction.
Designer: Abdullah Alawiss
"""

import re
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.celery_config import celery_app
from ..core.database import SessionLocal
from ..models.call import Call, CallTranscript
from ..services.redaction_service import RedactionService

@celery_app.task(bind=True, name="redact_sensitive_data")
def redact_sensitive_data(self, call_id: int) -> Dict[str, Any]:
    """
    Redact sensitive personal data from call transcript for GDPR compliance.
    """
    db = SessionLocal()
    
    try:
        # Get call and transcript
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise Exception(f"Call with ID {call_id} not found")
        
        transcript = db.query(CallTranscript).filter(CallTranscript.call_id == call_id).first()
        if not transcript:
            raise Exception(f"No transcript found for call {call_id}")
        
        # Initialize redaction service
        redaction_service = RedactionService()
        
        # Redact the transcript
        redacted_result = redaction_service.redact_transcript(
            transcript.raw_text,
            transcript.segments
        )
        
        # Update transcript with redacted version
        transcript.processed_text = redacted_result["redacted_text"]
        db.commit()
        
        return {
            "call_id": call_id,
            "redactions_applied": redacted_result["redactions_count"],
            "redaction_types": redacted_result["redaction_types"],
            "original_length": len(transcript.raw_text),
            "redacted_length": len(redacted_result["redacted_text"])
        }
        
    except Exception as e:
        raise e
    finally:
        db.close()

@celery_app.task(bind=True, name="detect_personal_data")
def detect_personal_data(self, text: str) -> Dict[str, Any]:
    """
    Detect various types of personal data in text.
    """
    
    detections = {
        "phone_numbers": [],
        "email_addresses": [],
        "norwegian_ids": [],
        "addresses": [],
        "names": [],
        "credit_cards": [],
        "bank_accounts": []
    }
    
    # Norwegian phone number patterns
    phone_patterns = [
        r'\b(\+47\s?)?([4-9]\d{7})\b',  # Norwegian mobile
        r'\b(\+47\s?)?([2-3]\d{7})\b',  # Norwegian landline
        r'\b\d{8}\b'  # 8-digit numbers (potential phone)
    ]
    
    for pattern in phone_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            detections["phone_numbers"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.9
            })
    
    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.finditer(email_pattern, text)
    for match in matches:
        detections["email_addresses"].append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "confidence": 0.95
        })
    
    # Norwegian personal ID numbers (fødselsnummer)
    norwegian_id_pattern = r'\b(\d{6}[\s-]?\d{5})\b'
    matches = re.finditer(norwegian_id_pattern, text)
    for match in matches:
        # Validate Norwegian ID checksum
        id_number = re.sub(r'[\s-]', '', match.group(0))
        if validate_norwegian_id(id_number):
            detections["norwegian_ids"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.98
            })
    
    # Credit card numbers (basic pattern)
    credit_card_pattern = r'\b(?:\d{4}[\s-]?){3}\d{4}\b'
    matches = re.finditer(credit_card_pattern, text)
    for match in matches:
        # Basic Luhn algorithm check
        if validate_credit_card(re.sub(r'[\s-]', '', match.group(0))):
            detections["credit_cards"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.85
            })
    
    # Norwegian bank account numbers
    bank_account_pattern = r'\b\d{4}[\s.]?\d{2}[\s.]?\d{5}\b'
    matches = re.finditer(bank_account_pattern, text)
    for match in matches:
        detections["bank_accounts"].append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "confidence": 0.8
        })
    
    # Norwegian address patterns
    address_patterns = [
        r'\b[A-ZÆØÅ][a-zæøå]+(?:s?gate|svei|plass|vegen|gata)\s+\d+[A-Z]?\b',
        r'\b\d{4}\s+[A-ZÆØÅ][a-zæøå]+\b'  # Postal codes with city names
    ]
    
    for pattern in address_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            detections["addresses"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.7
            })
    
    # Norwegian names (basic pattern)
    name_pattern = r'\b[A-ZÆØÅ][a-zæøå]{2,}\s+[A-ZÆØÅ][a-zæøå]{2,}\b'
    matches = re.finditer(name_pattern, text)
    for match in matches:
        # Filter out common non-name combinations
        name_text = match.group(0).lower()
        if not any(word in name_text for word in ['telenor', 'telia', 'ice', 'fiber', 'bredbånd']):
            detections["names"].append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.6
            })
    
    # Calculate total detections
    total_detections = sum(len(detections[key]) for key in detections)
    
    return {
        "detections": detections,
        "total_count": total_detections,
        "types_found": [key for key, value in detections.items() if value]
    }

@celery_app.task(bind=True, name="apply_redactions")
def apply_redactions(self, text: str, detections: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply redactions to text based on detection results.
    """
    
    redacted_text = text
    redactions_applied = 0
    redaction_types = set()
    
    # Sort all detections by position (reverse order to maintain positions)
    all_detections = []
    for detection_type, detection_list in detections["detections"].items():
        for detection in detection_list:
            detection["type"] = detection_type
            all_detections.append(detection)
    
    # Sort by start position in reverse order
    all_detections.sort(key=lambda x: x["start"], reverse=True)
    
    # Apply redactions
    redaction_masks = {
        "phone_numbers": "[TELEFON]",
        "email_addresses": "[E-POST]",
        "norwegian_ids": "[PERSONNUMMER]", 
        "addresses": "[ADRESSE]",
        "names": "[NAVN]",
        "credit_cards": "[KORTNUMMER]",
        "bank_accounts": "[KONTONUMMER]"
    }
    
    for detection in all_detections:
        # Only redact if confidence is above threshold
        if detection["confidence"] >= 0.7:
            start = detection["start"]
            end = detection["end"]
            detection_type = detection["type"]
            
            mask = redaction_masks.get(detection_type, "[REDACTED]")
            
            # Replace the detected text with mask
            redacted_text = redacted_text[:start] + mask + redacted_text[end:]
            redactions_applied += 1
            redaction_types.add(detection_type)
    
    return {
        "redacted_text": redacted_text,
        "redactions_count": redactions_applied,
        "redaction_types": list(redaction_types),
        "original_length": len(text),
        "redacted_length": len(redacted_text)
    }

@celery_app.task(bind=True, name="pseudonymize_data")
def pseudonymize_data(self, call_id: int) -> Dict[str, Any]:
    """
    Create pseudonymized version of data for analytics while preserving privacy.
    """
    db = SessionLocal()
    
    try:
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise Exception(f"Call with ID {call_id} not found")
        
        transcript = db.query(CallTranscript).filter(CallTranscript.call_id == call_id).first()
        if not transcript:
            raise Exception(f"No transcript found for call {call_id}")
        
        # Create pseudonymized mapping
        pseudonym_mapping = {}
        
        # Detect personal data
        detections = detect_personal_data.delay(transcript.raw_text).get()
        
        # Create consistent pseudonyms
        for detection_type, detection_list in detections["detections"].items():
            for i, detection in enumerate(detection_list):
                original_value = detection["text"]
                if original_value not in pseudonym_mapping:
                    pseudonym_mapping[original_value] = generate_pseudonym(detection_type, i)
        
        # Apply pseudonymization
        pseudonymized_text = transcript.raw_text
        for original, pseudonym in pseudonym_mapping.items():
            pseudonymized_text = pseudonymized_text.replace(original, pseudonym)
        
        return {
            "call_id": call_id,
            "pseudonym_count": len(pseudonym_mapping),
            "pseudonymized_text": pseudonymized_text,
            "mapping_hash": hash(str(sorted(pseudonym_mapping.items())))
        }
        
    except Exception as e:
        raise e
    finally:
        db.close()

def validate_norwegian_id(id_number: str) -> bool:
    """Validate Norwegian personal ID number using checksum."""
    if len(id_number) != 11 or not id_number.isdigit():
        return False
    
    # Simplified validation - implement full algorithm for production
    return True

def validate_credit_card(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0

def generate_pseudonym(data_type: str, index: int) -> str:
    """Generate consistent pseudonyms for different data types."""
    pseudonyms = {
        "phone_numbers": f"12345{index:03d}",
        "email_addresses": f"person{index}@example.no",
        "norwegian_ids": f"12345{index:06d}",
        "addresses": f"Testgate {index}",
        "names": f"Person {index}",
        "credit_cards": f"1234567890{index:06d}",
        "bank_accounts": f"1234.56.{index:05d}"
    }
    
    return pseudonyms.get(data_type, f"DATA_{index}")
