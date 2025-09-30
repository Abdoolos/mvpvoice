"""
Models module - imports all database models.
Designer: Abdullah Alawiss
"""

from .call import Call, CallTranscript, Speaker, CallAnalysis, ProcessingTask

__all__ = [
    "Call",
    "CallTranscript", 
    "Speaker",
    "CallAnalysis",
    "ProcessingTask"
]
