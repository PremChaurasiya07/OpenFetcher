# Use a slim Python 3.11 base
FROM python:3.11-slim

# Install Chromium, Chrome Driver, and essential Linux libraries
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Set Environment Variables for Selenium
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromiumdriver \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the FastAPI port (Render uses 10000 by default)
EXPOSE 10000

# Start Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]