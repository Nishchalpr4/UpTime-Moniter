# Start from an official Python 3.11 image (slim = smaller size)
FROM python:3.11-slim

# Set the working directory inside the container.
# All commands below run from here.
WORKDIR /app

# Copy requirements FIRST (before copying code).
# Why? Docker caches layers. If requirements.txt hasn't changed,
# Docker skips the pip install step entirely → faster rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code
COPY . .

# Tell Docker this container listens on port 8000
EXPOSE 8000

# The command that runs when the container starts.
# uvicorn = the ASGI server that runs FastAPI
# main:app = "in main.py, find the object called app"
# --host 0.0.0.0 = listen on all network interfaces (not just localhost)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
