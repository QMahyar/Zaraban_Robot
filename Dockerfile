FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories and files
RUN mkdir -p data/logs data/tmp system && \
    echo "YourTeamName" > system/team && \
    echo "@YourChannel" > system/channel

# Create non-root user
RUN useradd --create-home --shell /bin/bash telegram && \
    chown -R telegram:telegram /app

USER telegram

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('data/bot_data.json') else 1)"

# Default command
CMD ["python", "start.py"]