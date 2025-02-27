# Base image 선택 (Python 3.9)
FROM python:3.9-slim AS builder

# 필요한 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# chromedriver 133.x 버전 다운로드 및 설치 (리눅스용)
RUN wget -v https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.141/linux64/chromedriver-linux64.zip -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# chromedriver 경로 수정: 압축 해제된 chromedriver를 /usr/local/bin/으로 이동
RUN mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /usr/local/bin/chromedriver-linux64

# Final image
FROM python:3.9-slim

# 필요한 시스템 의존성 설치 (빌드 단계에서 설치한 의존성은 필요 없음)
RUN apt-get update && apt-get install -y \
    chromium \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# chrome 및 chromedriver 경로 환경변수 설정
ENV CHROME_BIN=/usr/bin/chromium
ENV DISPLAY=:99
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# 빌드 단계에서 생성된 chromedriver를 복사
COPY --from=builder /usr/local/bin/chromedriver /usr/local/bin/chromedriver

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일을 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 코드 파일을 복사
COPY . .

# 환경 변수 로딩
RUN echo "GEMINI_API_KEY=${GEMINI_API_KEY}" >> .env

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
