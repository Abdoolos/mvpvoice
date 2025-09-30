"""
Celery configuration for background task processing.
Designer: Abdullah Alawiss
"""

from celery import Celery
from .config import settings

# Create Celery app
celery_app = Celery(
    "callcenter_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.audio_tasks",
        "app.workers.analysis_tasks",
        "app.workers.gdpr_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.workers.audio_tasks.*": {"queue": "audio_processing"},
        "app.workers.analysis_tasks.*": {"queue": "analysis"},
        "app.workers.gdpr_tasks.*": {"queue": "gdpr"}
    },
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-old-tasks": {
            "task": "app.workers.maintenance_tasks.cleanup_old_tasks",
            "schedule": 3600.0,  # Every hour
        },
        "sftp-sync": {
            "task": "app.workers.sftp_tasks.sync_sftp_files",
            "schedule": 300.0,  # Every 5 minutes
        }
    }
)

# Task registration
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
    return {"task_id": self.request.id, "status": "completed"}
