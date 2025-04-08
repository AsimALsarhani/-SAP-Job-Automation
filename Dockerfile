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

# Install Google Chrome
RUN curl -Lo /tmp/google-chrome.deb [https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb](https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb) && \
    dpkg -i /tmp/google-chrome.deb || true && \
    apt-get update && apt-get install -f -y && \
    rm /tmp/google-chrome.deb

# Install ChromeDriver matching the installed Chrome version
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '^\d+') && \
    CHROMEDRIVER_VERSION=$(curl -s "[https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$](https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$){CHROME_VERSION}") && \
    curl -Lo /tmp/chromedriver.zip "[https://chromedriver.storage.googleapis.com/$](https://chromedriver.storage.googleapis.com/$){CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set Chrome binary path and ChromeDriver path as environment variables
ENV CHROME_PATH="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make automation.py executable
RUN chmod +x automation.py

# Specify the command to run when the container starts
CMD ["python", "automation.py"]
