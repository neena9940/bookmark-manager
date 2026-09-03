from arq.connections import RedisSettings

from app.tasks.summarize import summarize_bookmark

# 1. Define how to connect to Redis
REDIS_SETTINGS = RedisSettings(host="localhost", port=6379)


# 2. Define the Worker Settings class (ARQ looks for this)
class WorkerSettings:
    redis_settings = REDIS_SETTINGS
    functions = [summarize_bookmark]  # Tell ARQ which functions it is allowed to run
    max_jobs = 5  # Process up to 5 jobs concurrently
