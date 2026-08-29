from arq import run_worker

from app.core.worker import WorkerSettings

if __name__ == "__main__":
    # This starts the ARQ worker process
    run_worker(WorkerSettings)  # type: ignore[arg-type]
