# 1. Start with a lightweight, official Python 3.12 image
FROM python:3.12-slim

# 2. Set environment variables to make Python run better in Docker
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Forces Python to print logs to the terminal immediately (no buffering)
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy ONLY the requirements file first (Docker caches this layer!)
COPY requirements.txt .

# 5. Install dependencies. --no-cache-dir keeps the image size small.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code into the container
COPY . .

# 7. Tell Docker that the container will listen on port 8000
EXPOSE 8000

# 8. The command to run when the container starts
# --host 0.0.0.0 is CRUCIAL: it allows external connections (like your browser)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]