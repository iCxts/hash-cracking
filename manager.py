from __future__ import annotations

import uuid
from typing import Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from config import MAX_WORKERS
from models import Job, CrackStatus
from cracker import Cracker
from mode import *

class Manager:
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers= self.max_workers)
        self.jobs: Dict[str, Job] = {}

    def create_job(self, target: str, algorithm: str) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id = job_id, target = target, algorithm = algorithm)
        self.jobs[job_id] = job
        self.executor.submit(self._run_job, job_id)
        return job
    
    def get_job(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def _run_job(self, job_id: str) -> None:
        job: Job | None = self.jobs.get(job_id)
        if job is None:
            return 
        
        job.started_at = datetime.now()
        job.status = CrackStatus.RUNNING
        
        cracker = Cracker(job.target, job.algorithm)
        try:
            result = cracker.dictionary_attack(job)
            job.result = result
            if job.status != CrackStatus.CANCELLED:
                job.status = CrackStatus.FINISHED
        except Exception as exc:
            job.status = CrackStatus.FAILED
            job.result = None
            job.error = str(exc)
        finally:
            job.finished_at = datetime.now()
