FROM python:3.10-slim

WORKDIR /app

# Install OS-level dependencies first
RUN apt-get update && \
    apt-get install -y build-essential python3-dev poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Pre-copy requirements.txt to take advantage of Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . /app

EXPOSE 8000
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.document_summarizer_agent:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
