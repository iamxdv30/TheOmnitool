FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port for local development (Heroku will ignore this)
EXPOSE 5000

# Use environment variable for port, defaulting to 5000 if not set
CMD gunicorn --bind 0.0.0.0:$PORT main:app