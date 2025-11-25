from __future__ import annotations

from fastapi import FastAPI, HTTPException
import uvicorn

from config import ALLOWED_ALGOS
from manager import Manager
from models import CrackRequest, CrackResponse, JobStatusResponse, CrackStatus
from mode import mode_chooser, terminal
import os

# api type shit
app = FastAPI(title = "Hash Cracker V1")
manager = Manager()

def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

@app.post("/crack", response_model = CrackResponse)
def start_crack(request: CrackRequest) -> CrackResponse:
    if not request.target:
        raise HTTPException(status_code = 400, detail = "no hash value provided")

    algo = request.algorithm.lower()
    if algo not in ALLOWED_ALGOS:
        raise HTTPException(status_code = 400, detail = "unsupported algorithm")

    job = manager.create_job(target = request.target, algorithm = algo)

    return CrackResponse(
        job_id = job.id,
        status = job.status,
        message = "job created",
    )


@app.get("/status/{job_id}", response_model=JobStatusResponse)
def get_status(job_id: str) -> JobStatusResponse:
    job = manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code = 404, detail = "job not found")

    progress: float | None = None
    if job.total_candidates is not None and job.total_candidates > 0:
        progress = job.attempts / job.total_candidates * 100

    return JobStatusResponse(
        job_id = job.id,
        status = job.status,
        result = job.result,
        progress = progress,
        error = job.error,
        started_at = job.started_at,
        finished_at = job.finished_at,
    )


@app.post("/cancel/{job_id}", response_model = CrackResponse)
def cancel_job(job_id: str) -> CrackResponse:
    job = manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code = 404, detail = "job not found")

    if job.status in (CrackStatus.FINISHED, CrackStatus.FAILED, CrackStatus.CANCELLED):
        raise HTTPException(status_code = 400, detail = "job already completed")

    job.status = CrackStatus.CANCELLED
    return CrackResponse(
        job_id = job.id,
        status = job.status,
        message = "job cancelled",
    )

# cli type shit
def start_crack_cli(request: CrackRequest) -> CrackResponse | None:
    if not request.target:
        print("[!] No target provided")
        return None

    algo = request.algorithm.lower()
    if algo not in ALLOWED_ALGOS:
        print(f"[!] Unsupported algorithm: {algo}")
        return None

    job = manager.create_job(target = request.target, algorithm = algo)

    return CrackResponse(
        job_id = job.id,
        status = job.status,
        message = "job created",
    )


if __name__ == "__main__":
    mode = mode_chooser()

    if mode == "api":
        uvicorn.run("app:app", host = "0.0.0.0", port = 8000, reload = True)

    elif mode == "terminal":
        clear_screen()
        last_response: CrackResponse | None = None

        while True:
            print("=== Hash Cracker CLI ===")
            target, algorithm = terminal()

            if not target or not algorithm:
                print("[!] Invalid input")
                input("[Enter] to continue...")
                clear_screen()
                continue

            request = CrackRequest(target = target, algorithm = algorithm)
            response = start_crack_cli(request)

            if response is None:
                input("[Enter] to continue...")
                clear_screen()
                continue

            last_response = response
            print(f"[+] Job created. Job ID : {response.job_id}")

            while True:
                print()
                action = input(
                    "[S]tatus [N]ew [Q]uit [L]ist > "
                ).strip().lower()

                if action == "q":
                    clear_screen()
                    raise SystemExit(0)

                elif action == "n":
                    print(f"[*] Job {last_response.job_id} running in background")
                    input("[Enter] to create new job...")
                    clear_screen()
                    break 

                elif action == "s":
                    job_id = input("[?] Job ID (blank = last) > ").strip()
                    if not job_id:
                        if last_response is None:
                            print("[!] No last job to use")
                            continue
                        job_id = last_response.job_id

                    try:
                        clear_screen()
                        status = get_status(job_id)
                    except HTTPException as exc:
                        print(f"[!] Error: {exc.detail}")
                        continue

                    print("=== Job Status ===")
                    print(f"ID       : {status.job_id}")
                    print(f"Status   : {status.status.value}")
                    print(f"Result   : {status.result}")
                    print(f"Progress : {status.progress}")
                    print()
                    input("[Enter] to go back...")

                elif action == "l":
                    clear_screen()
                    print("=== Jobs ===")
                    if not manager.jobs:
                        print("[*] No jobs yet")
                    else:
                        for jid, job in manager.jobs.items():
                            print(
                                f"{jid}  status: {job.status.value}  "
                                f"attempts: {job.attempts}  result: {job.result}"
                            )
                    print()
                    input("[Enter] to go back...")

                else:
                    print("[!] Unknown option.")
