from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CrackStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    def __init__(
        self,
        id: str,
        target: str,
        algorithm: str,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        total_candidates: int | None = None,
        status: CrackStatus = CrackStatus.PENDING,
        result: str | None = None,
        attempts: int = 0,
        error: str | None = None,
    ) -> None:
        self.id = id
        self.target = target
        self.algorithm = algorithm
        self.started_at = started_at
        self.finished_at = finished_at
        self.total_candidates = total_candidates
        self.status = status
        self.result = result
        self.attempts = attempts
        self.error = error


class CrackRequest(BaseModel):
    target: str
    algorithm: str = "md5"


class CrackResponse(BaseModel):
    job_id: str
    status: CrackStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: CrackStatus
    result: str | None
    progress: float | None
    error: str | None
    started_at: datetime | None = None
    finished_at: datetime | None = None
