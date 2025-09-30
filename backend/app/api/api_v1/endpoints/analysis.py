"""
API endpoints for call analysis and statistics.
Designer: Abdullah Alawiss
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ....core.database import get_db
from ....models.call import Call, CallAnalysis, CallTranscript, ProcessingTask
from ....schemas.call import StatsResponse, ProcessingTaskResponse

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    
    # Basic call counts
    total_calls = db.query(Call).count()
    completed_calls = db.query(Call).filter(Call.status == "completed").count()
    failed_calls = db.query(Call).filter(Call.status == "failed").count()
    processing_calls = db.query(Call).filter(Call.status == "processing").count()
    
    # Analysis results
    good_calls = db.query(CallAnalysis).filter(CallAnalysis.overall_result == "good").count()
    bad_calls = db.query(CallAnalysis).filter(CallAnalysis.overall_result == "bad").count()
    
    # Duration stats
    total_duration = db.query(func.sum(Call.duration_seconds)).scalar() or 0
    total_duration_minutes = total_duration / 60
    
    # Processing time stats
    avg_processing_time = db.query(func.avg(CallTranscript.processing_time_seconds)).scalar() or 0
    
    # Top violations
    violations_data = db.query(CallAnalysis.violations).filter(
        CallAnalysis.violations.isnot(None)
    ).all()
    
    violation_counts = {}
    for analysis in violations_data:
        if analysis.violations:
            for violation in analysis.violations:
                violation_type = violation.get('type', 'unknown')
                violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
    
    top_violations = [
        {"type": vtype, "count": count}
        for vtype, count in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    ]
    
    return StatsResponse(
        total_calls=total_calls,
        completed_calls=completed_calls,
        failed_calls=failed_calls,
        processing_calls=processing_calls,
        good_calls=good_calls,
        bad_calls=bad_calls,
        total_duration_minutes=total_duration_minutes,
        avg_processing_time_seconds=avg_processing_time,
        top_violations=top_violations
    )

@router.get("/violations")
async def get_violations_summary(
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get summary of all violations across calls."""
    
    calls_with_violations = db.query(Call).join(CallAnalysis).filter(
        CallAnalysis.overall_result == "bad"
    ).order_by(desc(Call.created_at)).limit(limit).all()
    
    violations_summary = []
    
    for call in calls_with_violations:
        if call.analysis and call.analysis.violations:
            for violation in call.analysis.violations:
                violations_summary.append({
                    "call_id": call.id,
                    "filename": call.original_filename,
                    "violation_type": violation.get('type'),
                    "description": violation.get('description'),
                    "timestamp": violation.get('timestamp'),
                    "severity": violation.get('severity', 'medium'),
                    "created_at": call.created_at
                })
    
    return {
        "violations": violations_summary,
        "total": len(violations_summary)
    }

@router.get("/rule-analysis")
async def get_rule_analysis_summary(
    db: Session = Depends(get_db)
):
    """Get analysis summary for each rule type."""
    
    # Count mentions of each rule
    bindingstid_count = db.query(CallAnalysis).filter(
        CallAnalysis.bindingstid_mentioned == True
    ).count()
    
    pris_count = db.query(CallAnalysis).filter(
        CallAnalysis.pris_mentioned == True
    ).count()
    
    press_count = db.query(CallAnalysis).filter(
        CallAnalysis.press_mentioned == True
    ).count()
    
    total_analyzed = db.query(CallAnalysis).count()
    
    return {
        "total_analyzed_calls": total_analyzed,
        "rules": {
            "bindingstid": {
                "mentioned_count": bindingstid_count,
                "percentage": (bindingstid_count / total_analyzed * 100) if total_analyzed > 0 else 0
            },
            "pris": {
                "mentioned_count": pris_count,
                "percentage": (pris_count / total_analyzed * 100) if total_analyzed > 0 else 0
            },
            "press": {
                "mentioned_count": press_count,
                "percentage": (press_count / total_analyzed * 100) if total_analyzed > 0 else 0
            }
        }
    }

@router.get("/tasks", response_model=List[ProcessingTaskResponse])
async def get_processing_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get list of processing tasks."""
    
    query = db.query(ProcessingTask)
    
    if status:
        query = query.filter(ProcessingTask.status == status)
    
    tasks = query.order_by(desc(ProcessingTask.created_at)).limit(limit).all()
    
    return [ProcessingTaskResponse.from_orm(task) for task in tasks]

@router.get("/tasks/{task_id}", response_model=ProcessingTaskResponse)
async def get_processing_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific processing task."""
    
    task = db.query(ProcessingTask).filter(ProcessingTask.task_id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return ProcessingTaskResponse.from_orm(task)

@router.post("/reprocess/{call_id}")
async def reprocess_call(
    call_id: int,
    db: Session = Depends(get_db)
):
    """Reprocess a call (re-run analysis)."""
    
    call = db.query(Call).filter(Call.id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Reset call status
    call.status = "processing"
    db.commit()
    
    # Start reprocessing task
    from ....workers.audio_tasks import process_audio_file
    task = process_audio_file.delay(call_id)
    
    return {
        "message": "Reprocessing started",
        "call_id": call_id,
        "task_id": task.id
    }

@router.get("/export/violations")
async def export_violations(
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """Export violations data in JSON or CSV format."""
    
    violations_data = []
    
    calls_with_violations = db.query(Call).join(CallAnalysis).filter(
        CallAnalysis.overall_result == "bad"
    ).all()
    
    for call in calls_with_violations:
        if call.analysis and call.analysis.violations:
            for violation in call.analysis.violations:
                violations_data.append({
                    "call_id": call.id,
                    "filename": call.original_filename,
                    "violation_type": violation.get('type'),
                    "description": violation.get('description'),
                    "timestamp": violation.get('timestamp'),
                    "severity": violation.get('severity', 'medium'),
                    "created_at": call.created_at.isoformat() if call.created_at else None
                })
    
    if format == "json":
        return {"violations": violations_data}
    else:
        # For CSV, you would implement CSV conversion here
        # This is a simplified response
        return {"message": "CSV export not implemented yet", "data": violations_data}
