from __future__ import annotations

import hashlib

from config import WORDLIST_PATH
from models import Job, CrackStatus


class Cracker:
    def __init__(self, target: str, algorithm: str) -> None:
        self.target = target.lower()
        self.algorithm = algorithm.lower()
    
    def _compute_hash(self, plaintext: str) -> str:
        try:
            hasher = hashlib.new(self.algorithm)
        except ValueError:
            raise ValueError("Unsupported Algorithm")
        
        hasher.update(plaintext.encode("utf-8"))
        return hasher.hexdigest()
    
    def dictionary_attack(self, job: Job, wordlist: str = WORDLIST_PATH) -> str | None:
        with open(wordlist, "r", encoding = "utf-8", errors = "ignore") as file:
            candidates = [line.strip() for line in file if line.strip()]

        job.total_candidates = len(candidates)

        for candidate in candidates:
            if job.status == CrackStatus.CANCELLED:
                return None

            job.attempts += 1
            hashed_line = self._compute_hash(candidate)
            if hashed_line == self.target:
                return candidate
        
        return None
