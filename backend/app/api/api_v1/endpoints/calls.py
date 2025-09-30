"""
API endpoints for call management.
Designer: Abdullah Alawiss
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....models.call import Call, CallTranscript, CallAnalysis
from ....schemas.call import CallResponse, CallDetailResponse, CallListResponse

router = APIRouter()

@router.get("/", response_model=CallListResponse)
async def get_calls(
    skip: int = Query(0, ge=0, description="Number of calls to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of calls to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get list of calls with pagination and filtering."""
    query = db.query(Call)
    
    if status:
        query = query.filter(Call.status == status)
    
    total = query.count()
    calls = query.offset(skip).limit(limit).all()
    
    return CallListResponse(
        calls=[CallResponse.from_orm(call) for call in calls],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call(
    call_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific call."""
    call = db.query(Call).filter(Call.id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return CallDetailResponse.from_orm(call)

@router.delete("/{call_id}")
async def delete_call(
    call_id: int,
    db: Session = Depends(get_db)
):
    """Delete a call and all associated data."""
    call = db.query(Call).filter(Call.id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Delete related records first
    db.query(CallTranscript).filter(CallTranscript.call_id == call_id).delete()
    db.query(CallAnalysis).filter(CallAnalysis.call_id == call_id).delete()
    
    # Delete the call
    db.delete(call)
    db.commit()
    
    return {"message": "Call deleted successfully"}

@router.get("/{call_id}/transcript")
async def get_call_transcript(
    call_id: int,
    db: Session = Depends(get_db)
):
    """Get transcript for a specific call."""
    transcript = db.query(CallTranscript).filter(CallTranscript.call_id == call_id).first()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return {
        "call_id": call_id,
        "raw_text": transcript.raw_text,
        "processed_text": transcript.processed_text,
        "language": transcript.language,
        "confidence": transcript.confidence,
        "segments": transcript.segments,
        "created_at": transcript.created_at
    }

@router.get("/{call_id}/analysis")
async def get_call_analysis(
    call_id: int,
    db: Session = Depends(get_db)
):
    """Get analysis results for a specific call."""
    analysis = db.query(CallAnalysis).filter(CallAnalysis.call_id == call_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "call_id": call_id,
        "overall_result": analysis.overall_result,
        "confidence_score": analysis.confidence_score,
        "violations": analysis.violations,
        "bindingstid_mentioned": analysis.bindingstid_mentioned,
        "bindingstid_details": analysis.bindingstid_details,
        "pris_mentioned": analysis.pris_mentioned,
        "pris_details": analysis.pris_details,
        "press_mentioned": analysis.press_mentioned,
        "press_details": analysis.press_details,
        "summary": analysis.summary,
        "key_points": analysis.key_points,
        "created_at": analysis.created_at
    }
