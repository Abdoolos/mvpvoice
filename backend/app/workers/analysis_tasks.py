"""
Celery tasks for call analysis (bindingstid, pris, press rules).
Designer: Abdullah Alawiss
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from ..core.celery_config import celery_app
from ..core.database import SessionLocal
from ..models.call import Call, CallTranscript, CallAnalysis
from ..rules.norwegian_rules import NorwegianRulesEngine

@celery_app.task(bind=True, name="analyze_call")
def analyze_call(self, call_id: int) -> Dict[str, Any]:
    """
    Analyze a call for Norwegian telecom sales compliance.
    Checks for bindingstid (binding period), pris (price), and press (pressure) violations.
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
        
        # Initialize rules engine
        rules_engine = NorwegianRulesEngine()
        
        # Analyze the transcript
        analysis_result = rules_engine.analyze_transcript(
            transcript.raw_text,
            transcript.segments
        )
        
        # Determine overall result
        overall_result = "good" if len(analysis_result["violations"]) == 0 else "bad"
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(analysis_result)
        
        # Create analysis record
        analysis = CallAnalysis(
            call_id=call_id,
            overall_result=overall_result,
            confidence_score=confidence_score,
            violations=analysis_result["violations"],
            bindingstid_mentioned=analysis_result["bindingstid"]["mentioned"],
            bindingstid_details=analysis_result["bindingstid"]["details"],
            pris_mentioned=analysis_result["pris"]["mentioned"],
            pris_details=analysis_result["pris"]["details"],
            press_mentioned=analysis_result["press"]["mentioned"],
            press_details=analysis_result["press"]["details"],
            summary=analysis_result["summary"],
            key_points=analysis_result["key_points"]
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return {
            "analysis_id": analysis.id,
            "overall_result": overall_result,
            "confidence_score": confidence_score,
            "violations_count": len(analysis_result["violations"]),
            "rules_checked": ["bindingstid", "pris", "press"],
            "summary": analysis_result["summary"]
        }
        
    except Exception as e:
        raise e
    finally:
        db.close()

@celery_app.task(bind=True, name="check_bindingstid_compliance")
def check_bindingstid_compliance(self, call_id: int, transcript_text: str) -> Dict[str, Any]:
    """
    Check if binding period (bindingstid) was properly disclosed.
    Norwegian telecom law requires clear disclosure of contract duration.
    """
    
    violations = []
    bindingstid_mentioned = False
    details = {}
    
    # Norwegian patterns for binding period disclosure
    bindingstid_patterns = [
        r'bindingstid.*?(\d+)\s*(måned|år)',
        r'binding.*?(\d+)\s*(month|year)',
        r'kontrakt.*?(\d+)\s*(måned|år)',
        r'avtale.*?(\d+)\s*(måned|år)',
        r'forpliktelse.*?(\d+)\s*(måned|år)',
        r'(\d+)\s*(års?|måneders?)\s*binding',
        r'(\d+)\s*(års?|måneders?)\s*kontrakt'
    ]
    
    text_lower = transcript_text.lower()
    
    # Check for binding period mentions
    for pattern in bindingstid_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            bindingstid_mentioned = True
            duration = match.group(1)
            unit = match.group(2)
            details[f"mention_{len(details)}"] = {
                "duration": duration,
                "unit": unit,
                "text": match.group(0),
                "position": match.start()
            }
    
    # Check for proper disclosure requirements
    if bindingstid_mentioned:
        # Check if duration was clearly stated
        clear_disclosure_patterns = [
            r'du blir bundet.*?(\d+)',
            r'kontrakten gjelder.*?(\d+)',
            r'du forplikter deg.*?(\d+)',
            r'bindingstiden er.*?(\d+)'
        ]
        
        clear_disclosure = any(
            re.search(pattern, text_lower) for pattern in clear_disclosure_patterns
        )
        
        if not clear_disclosure:
            violations.append({
                "type": "bindingstid_unclear",
                "severity": "high",
                "description": "Bindingstid mentioned but not clearly disclosed",
                "timestamp": None,
                "rule": "Norwegian telecom regulations require clear disclosure of contract duration"
            })
    else:
        # No binding period mentioned - potential violation
        violations.append({
            "type": "bindingstid_missing",
            "severity": "high", 
            "description": "No mention of binding period found in conversation",
            "timestamp": None,
            "rule": "Binding period must be clearly disclosed in telecom sales"
        })
    
    return {
        "mentioned": bindingstid_mentioned,
        "violations": violations,
        "details": details
    }

@celery_app.task(bind=True, name="check_price_compliance")
def check_price_compliance(self, call_id: int, transcript_text: str) -> Dict[str, Any]:
    """
    Check if pricing was properly disclosed.
    Must include total cost, monthly fees, and any additional charges.
    """
    
    violations = []
    pris_mentioned = False
    details = {}
    
    # Norwegian patterns for price disclosure
    price_patterns = [
        r'pris.*?(\d+)\s*kroner?',
        r'koster.*?(\d+)\s*kr',
        r'betaler.*?(\d+)\s*kroner?',
        r'månedlig.*?(\d+)\s*kr',
        r'(\d+)\s*kr.*?måneden',
        r'totalprisen.*?(\d+)',
        r'opprettelsesgebyr.*?(\d+)',
        r'fakturagebyr.*?(\d+)'
    ]
    
    text_lower = transcript_text.lower()
    
    # Check for price mentions
    for pattern in price_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            pris_mentioned = True
            amount = match.group(1)
            details[f"price_{len(details)}"] = {
                "amount": amount,
                "text": match.group(0),
                "position": match.start()
            }
    
    # Check for required price components
    if pris_mentioned:
        required_disclosures = {
            "monthly_fee": [r'månedlig.*?(\d+)', r'per måned.*?(\d+)', r'(\d+).*?i måneden'],
            "setup_fee": [r'opprettelse.*?(\d+)', r'etablering.*?(\d+)', r'aktivering.*?(\d+)'],
            "total_cost": [r'total.*?(\d+)', r'tilsamen.*?(\d+)', r'samlet.*?(\d+)']
        }
        
        missing_disclosures = []
        for disclosure_type, patterns in required_disclosures.items():
            if not any(re.search(pattern, text_lower) for pattern in patterns):
                missing_disclosures.append(disclosure_type)
        
        if missing_disclosures:
            violations.append({
                "type": "price_incomplete",
                "severity": "medium",
                "description": f"Missing price disclosures: {', '.join(missing_disclosures)}",
                "timestamp": None,
                "missing_components": missing_disclosures,
                "rule": "All price components must be clearly disclosed"
            })
    else:
        violations.append({
            "type": "price_missing",
            "severity": "high",
            "description": "No pricing information disclosed during call",
            "timestamp": None,
            "rule": "Price must be clearly disclosed in telecom sales"
        })
    
    return {
        "mentioned": pris_mentioned,
        "violations": violations,
        "details": details
    }

@celery_app.task(bind=True, name="check_pressure_compliance")
def check_pressure_compliance(self, call_id: int, transcript_text: str) -> Dict[str, Any]:
    """
    Check for inappropriate sales pressure tactics.
    Norwegian consumer protection law prohibits aggressive sales tactics.
    """
    
    violations = []
    press_mentioned = False
    details = {}
    
    # Norwegian patterns for pressure tactics
    pressure_patterns = {
        "urgency": [
            r'må bestemme deg nå',
            r'tilbudet utgår',
            r'kun i dag',
            r'begrenset tid',
            r'siste sjanse',
            r'bare nå',
            r'må handle raskt'
        ],
        "repetition": [
            r'som jeg sa',
            r'som nevnt',
            r'igjen',
            r'fortsatt'
        ],
        "dismissal": [
            r'ikke tenk så mye',
            r'bare si ja',
            r'det er enkelt',
            r'ikke kompliser'
        ]
    }
    
    text_lower = transcript_text.lower()
    
    # Check for each type of pressure tactic
    for tactic_type, patterns in pressure_patterns.items():
        tactic_count = 0
        for pattern in patterns:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            if matches:
                press_mentioned = True
                tactic_count += len(matches)
                details[f"{tactic_type}_examples"] = [
                    {
                        "text": match.group(0),
                        "position": match.start()
                    } for match in matches
                ]
        
        # Determine if tactic usage is excessive
        if tactic_type == "urgency" and tactic_count > 2:
            violations.append({
                "type": "excessive_urgency",
                "severity": "high",
                "description": f"Excessive urgency tactics used ({tactic_count} instances)",
                "timestamp": None,
                "rule": "Excessive pressure tactics are prohibited in telecom sales"
            })
        elif tactic_type == "repetition" and tactic_count > 5:
            violations.append({
                "type": "excessive_repetition", 
                "severity": "medium",
                "description": f"Excessive repetition detected ({tactic_count} instances)",
                "timestamp": None,
                "rule": "Repetitive pressure tactics may violate consumer protection"
            })
        elif tactic_type == "dismissal" and tactic_count > 1:
            violations.append({
                "type": "dismissive_language",
                "severity": "high",
                "description": f"Dismissive language used ({tactic_count} instances)",
                "timestamp": None,
                "rule": "Dismissive sales tactics are inappropriate"
            })
    
    # Check conversation pace and interruptions
    if "segments" in details and len(details["segments"]) > 0:
        # Analyze speaking patterns for pressure indicators
        agent_interruptions = count_interruptions(details["segments"])
        if agent_interruptions > 3:
            violations.append({
                "type": "excessive_interruptions",
                "severity": "medium",
                "description": f"Agent interrupted customer {agent_interruptions} times",
                "timestamp": None,
                "rule": "Excessive interruptions may indicate pressure tactics"
            })
    
    return {
        "mentioned": press_mentioned,
        "violations": violations,
        "details": details
    }

def calculate_confidence_score(analysis_result: Dict[str, Any]) -> float:
    """Calculate confidence score for the analysis."""
    
    base_score = 0.7  # Base confidence
    
    # Increase confidence if clear patterns were found
    if analysis_result["bindingstid"]["mentioned"]:
        base_score += 0.1
    if analysis_result["pris"]["mentioned"]:
        base_score += 0.1
    if analysis_result["press"]["mentioned"]:
        base_score += 0.1
    
    # Decrease confidence for ambiguous cases
    if len(analysis_result["violations"]) == 0:
        base_score += 0.1  # High confidence in good calls
    
    return min(base_score, 1.0)

def count_interruptions(segments: List[Dict]) -> int:
    """Count potential interruptions in conversation."""
    interruptions = 0
    
    for i in range(len(segments) - 1):
        current_end = segments[i]["end"]
        next_start = segments[i + 1]["start"]
        
        # If next segment starts before current ends (overlap), it's an interruption
        if next_start < current_end:
            interruptions += 1
    
    return interruptions
