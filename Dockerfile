FROM python:3.12-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to utilize Docker layer caching
COPY requirements.txt .

# Install python dependencies and awscli
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir awscli

# Copy the rest of the application files
COPY . .

# Ensure prediction output directory exists
RUN mkdir -p prediction_output

# Expose FastAPI server port
EXPOSE 8080

# Run the FastAPI server using uvicorn binding to 0.0.0.0 (required for Docker/EC2 access)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
