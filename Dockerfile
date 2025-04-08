# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies including jq
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip \
    jq \ # Added jq
    libgssapi-krb5-2 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -Lo /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/google-chrome.deb || true && \
    apt-get update && apt-get install -f -y && \
    rm /tmp/google-chrome.deb

# Install ChromeDriver using the new Chrome for Testing API
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "Installed Chrome version: ${CHROME_VERSION}" && \
    # Get the latest stable ChromeDriver URL for linux64
    CHROMEDRIVER_URL=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url') && \
    if [ -z "$CHROMEDRIVER_URL" ]; then \
      echo "Could not automatically determine ChromeDriver URL. Exiting."; \
      exit 1; \
    fi && \
    echo "ChromeDriver download URL: ${CHROMEDRIVER_URL}" && \
    # Download, unzip, move, and set permissions
    curl -Lo /tmp/chromedriver.zip "${CHROMEDRIVER_URL}" && \
    unzip /tmp/chromedriver.zip -d /tmp && \
    # Adjust path based on actual zip contents if needed
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    # Clean up
    rm /tmp/chromedriver.zip && \
    rm -rf /tmp/chromedriver-linux64 && \
    # Verify
    chromedriver --version

# Set Chrome binary and ChromeDriver paths as environment variables (optional but good practice)
ENV CHROME_PATH="/usr/bin/google-chrome"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

# Install Python dependencies from requirements.txt
# Ensure requirements.txt is in your project root and includes selenium
RUN pip install --no-cache-dir -r requirements.txt

# Make automation.py executable (Only needed if you run it directly, not via `python automation.py`)
# RUN chmod +x automation.py

# Specify the command to run when the container starts
CMD ["python", "automation.py"]
