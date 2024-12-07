# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app



# Install dependencies (optimized for Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .


# Environment variables
ENV PORT=8080

# Expose port
EXPOSE 8080

# Start the application with gunicorn (updated to JSON array syntax)
CMD ["gunicorn", "--bind", ":8080", "app:app", "--workers", "1", "--threads", "8", "--timeout", "0"]
