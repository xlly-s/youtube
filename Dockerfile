# Use an official Python base image
FROM python:3.10-slim

# Install ffmpeg and other required packages
RUN apt-get update && apt-get install -y ffmpeg curl && apt-get clean

# Set working directory
WORKDIR /app

# Copy everything into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
