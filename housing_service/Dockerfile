FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY housing_service/requirements.txt ./

ENV CMAKE_C_COMPILER=gcc
ENV CMAKE_CXX_COMPILER=g++

RUN pip install --upgrade pip
RUN CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install --no-cache-dir llama-cpp-python==0.2.9
RUN pip install --no-cache-dir -r requirements.txt

COPY housing_service/app ./app
COPY models ./models
COPY shared ./shared

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
