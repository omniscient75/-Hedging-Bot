# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables (optional, e.g., for unbuffered output)
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"] 