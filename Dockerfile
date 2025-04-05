# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip \
    libgssapi-krb5-2 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver
RUN curl -Lo /tmp/chrome.zip https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    unzip /tmp/chrome.zip -d /tmp/chrome && \
    dpkg -i /tmp/chrome/google-chrome-stable_current_amd64.deb; \
    apt-get install -f -y && \
    rm -rf /tmp/chrome*

# Set Chrome binary path
ENV CHROME_PATH="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make automation.py executable
RUN chmod +x automation.py

# Specify the command to run when the container starts
CMD ["python", "automation.py"]
