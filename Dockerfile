# ------------------------------
# 1) Base Python légère
# ------------------------------
FROM python:3.10-slim

# ------------------------------
# 2) Env
# ------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ------------------------------
# 3) OS dependencies (OCR / PDF only)
# ------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# 4) Workdir
# ------------------------------
WORKDIR /app

# ------------------------------
# 5) Copy requirements first (cache)
# ------------------------------
COPY requirements.txt .

# ------------------------------
# 6) Upgrade pip + install deps
# ------------------------------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ------------------------------
# 7) Copy source code
# ------------------------------
COPY . .

# ------------------------------
# 8) Expose API
# ------------------------------
EXPOSE 8000

# ------------------------------
# 9) Start FastAPI (prod safe)
# ------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
