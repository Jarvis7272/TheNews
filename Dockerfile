# 1. Use official Python image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy requirements first for caching
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the app
COPY . .

# 6. Expose any port (Render sets the actual port via PORT env)
EXPOSE 8080

# 7. Run Flask using correct port from environment variable
CMD ["python", "-u", "app.py"]
