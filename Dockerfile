FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment variables
ENV PORT=8080

# Expose port
EXPOSE 8080

# Start the application with gunicorn
CMD exec gunicorn --bind :$PORT api.app:app --workers 1 --threads 8 --timeout 0