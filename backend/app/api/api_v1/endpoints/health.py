"""
API endpoints for health checks and system status.
Designer: Abdullah Alawiss
"""

import time
import redis
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from celery import Celery

from ....core.config import settings
from ....core.database import engine

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "AI Callcenter Agent MVP",
        "version": settings.VERSION,
        "designer": "Abdullah Alawiss"
    }

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including all dependencies."""
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "AI Callcenter Agent MVP",
        "version": settings.VERSION,
        "checks": {
            "database": {"status": "unknown"},
            "redis": {"status": "unknown"},
            "celery": {"status": "unknown"},
            "disk_space": {"status": "unknown"}
        }
    }
    
    # Check database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis connection
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check Celery worker
    try:
        celery_app = Celery(
            "callcenter_tasks",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND
        )
        
        # Get active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            health_status["checks"]["celery"] = {
                "status": "healthy",
                "message": f"Celery workers active: {len(active_workers)}",
                "workers": list(active_workers.keys())
            }
        else:
            health_status["checks"]["celery"] = {
                "status": "degraded",
                "message": "No active Celery workers found"
            }
    except Exception as e:
        health_status["checks"]["celery"] = {
            "status": "unhealthy",
            "message": f"Celery check failed: {str(e)}"
        }
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100
        
        if free_percent > 20:
            status = "healthy"
        elif free_percent > 10:
            status = "degraded"
        else:
            status = "unhealthy"
            health_status["status"] = "unhealthy"
        
        health_status["checks"]["disk_space"] = {
            "status": status,
            "message": f"Free disk space: {free_percent:.1f}%",
            "free_gb": round(free / (1024**3), 2),
            "total_gb": round(total / (1024**3), 2)
        }
    except Exception as e:
        health_status["checks"]["disk_space"] = {
            "status": "unknown",
            "message": f"Disk space check failed: {str(e)}"
        }
    
    return health_status

@router.get("/readiness")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration."""
    
    # Check critical dependencies
    try:
        # Database check
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Redis check
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return {
            "status": "ready",
            "timestamp": time.time(),
            "message": "Service is ready to accept requests"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "timestamp": time.time(),
                "message": f"Service not ready: {str(e)}"
            }
        )

@router.get("/liveness")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration."""
    
    # Basic application liveness check
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - start_time if 'start_time' in globals() else 0
    }

# Store application start time
start_time = time.time()

@router.get("/metrics")
async def get_metrics():
    """Get basic application metrics."""
    
    try:
        # Get database metrics
        with engine.connect() as conn:
            db_connections = conn.execute(text("SELECT count(*) FROM pg_stat_activity")).scalar()
        
        # Get Redis metrics
        r = redis.Redis.from_url(settings.REDIS_URL)
        redis_info = r.info()
        
        return {
            "timestamp": time.time(),
            "application": {
                "uptime_seconds": time.time() - start_time,
                "version": settings.VERSION
            },
            "database": {
                "active_connections": db_connections,
                "pool_size": engine.pool.size(),
                "checked_out": engine.pool.checkedout()
            },
            "redis": {
                "used_memory": redis_info.get('used_memory', 0),
                "connected_clients": redis_info.get('connected_clients', 0),
                "total_commands_processed": redis_info.get('total_commands_processed', 0)
            }
        }
        
    except Exception as e:
        return {
            "timestamp": time.time(),
            "error": f"Failed to collect metrics: {str(e)}"
        }
