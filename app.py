#importing shit
from __future__ import annotations

import hashlib
import uuid
from enum import Enum
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor

#config
WORDLIST_PATH = "wordlist.txt"
MAX_WORKERS = 4
ALLOWED_ALGOS = {"md5", "sha1", "sha256"}

# models
class CrackStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"

class Job:
    def __init__(
            self,
            id: str,
            target: str,
            algorithm: str,
            status: CrackStatus = CrackStatus.PENDING,
            result: str | None = None,
            attempts: int = 0,
            error: str | None = None
    ) -> None:
        self.id = id
        self.target = target
        self.algorithm = algorithm
        self.status = status
        self.result = result
        self.attempts = attempts
        self.error = error

class Cracker:
    def __init__(self, target: str, algorithm: str) -> None:
        self.target = target.lower()
        self.algorithm = algorithm.lower()
    
    def _compute_hash(self, plaintext: str) -> str:
        try:
            hasher = hashlib.new(self.algorithm)
        except ValueError:
            raise ValueError('Unsupported Algorithm')
        
        hasher.update(plaintext.encode('utf-8'))
        return hasher.hexdigest()
    
    def _variant(self, plaintext: str) -> list[str]:
        upper = plaintext.upper()
        lower = plaintext.lower()
        capitalized = plaintext.capitalize()
        simple_l33t = ""

        l33t_dict = {"a": "@", "e": "3", "g": '6', "i": "1", "o": "0", "s": "5"}
        for char in plaintext:
            if char in l33t_dict.key():
                simple_l33t += l33t_dict.values()
            else:
                simple_l33t += char
        
        return [upper, lower, capitalized, simple_l33t]
    
    def dictionary_attack(self, job: Job, use_variant: bool = False, wordlist: str = WORDLIST_PATH) -> str | None:
        with open(wordlist, "r", encoding = "utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if not use_variant:
                    job.attempts += 1
                    hashed_line = self._compute_hash(line)
                    if hashed_line == self.target:
                        return line
                else:
                    pass 
        return None
    

class Manager:
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers = self.max_workers)
        self.jobs: Dict[str, Job] = {}

    def create_job(self, target: str, algorithm: str) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id = job_id, target = target, algorithm = algorithm)
        self.jobs[job_id] = job
        self.executor.submit(self._run_job, job_id)
        return job
    
    def get_job(self, job_id: str) -> Job:
        return self.jobs.get(job_id)

    def _run_job(self, job_id: str) -> None:
        job: Job = self.jobs.get(job_id)
        if job == None:
            return 
        
        job.status = CrackStatus.RUNNING
        cracker = Cracker(job.target, job.algorithm)
        try:
            result = cracker.dictionary_attack(job)
            job.result = result
            job.status = CrackStatus.FINISHED
        except Exception as exc:
            job.status = CrackStatus.FAILED
            job.result = None
            job.error = str(exc)

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
    attempts: int
    error: str | None


#api type shit
app = FastAPI(title = "Hash Cracker V1")
manager = Manager()

@app.post("/crack", response_model = CrackResponse)
def start_crack(request: CrackRequest) -> CrackResponse:
    if not request.target:
        raise HTTPException(status_code = 400, detail = "no hash value provided")
    if request.algorithm.lower() not in ALLOWED_ALGOS:
        raise HTTPException(status_code = 400, detail = "unsupported algorithm")
    
    job = manager.create_job(target = request.target, algorithm = request.algorithm)
    
    return CrackResponse(
        job_id = job.id,
        status = job.status,
        message = "job created")
    

@app.get("/status/{job_id}", response_model = JobStatusResponse)
def get_status(job_id: str) -> JobStatusResponse:
    job = manager.get_job(job_id)
    if job == None:
        raise HTTPException(status_code = 404, detail = "job not found")
    
    return JobStatusResponse(
        job_id = job.id,
        status = job.status,
        result = job.result,
        attempts = job.attempts,
        error = job.error
        )
    
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host = "0.0.0.0", port = 8000, reload = True)



        

