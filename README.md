# ViHateT5 Toxicity Detection API

API để kiểm tra độc tính trong văn bản tiếng Việt sử dụng mô hình ViHateT5-base-HSD.

## ✨ Tính năng

- **Kiểm tra độc tính**: Phân tích văn bản tiếng Việt và xác định mức độ độc tính
- **API chuẩn RESTful**: Endpoints đơn giản và dễ sử dụng  
- **JSON Response**: Định dạng phản hồi thống nhất với `status_code`, `error`, `data`
- **FastAPI**: Performance cao với tự động tạo docs
- **Lazy Loading**: Model chỉ load khi cần, tối ưu memory
- **Model Caching**: Cache model trong memory sau lần load đầu
- **Health Check**: Endpoint để kiểm tra trạng thái server và model
- **Error Handling**: Xử lý lỗi chi tiết và logging đầy đủ
- **Input Validation**: Kiểm tra và làm sạch input text

## 🚀 Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd TribalchiefBanana
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy server
```bash
python main.py
```

Hoặc sử dụng uvicorn trực tiếp:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 API Documentation

Server sẽ chạy tại: `http://localhost:8000`

### Endpoints

#### 1. Root Endpoint
- **URL**: `GET /`
- **Mô tả**: Kiểm tra API đang hoạt động

#### 2. Kiểm tra độc tính  
- **URL**: `POST /check-toxicity`
- **Body**:
```json
{
    "text": "Văn bản cần kiểm tra"
}
```

- **Response**:
```json
{
    "status_code": 200,
    "error": null,
    "data": {
        "input_text": "Văn bản cần kiểm tra",
        "toxicity_result": "CLEAN hoặc TOXIC",
        "processed": true,
        "model": "ViHateT5-base-HSD"
    }
}
```

#### 3. Health Check
- **URL**: `GET /health`
- **Mô tả**: Kiểm tra trạng thái server và model

#### 4. Model Info
- **URL**: `GET /model-info`
- **Mô tả**: Thông tin chi tiết về model đang sử dụng

### Response Format

Tất cả các response đều có format chuẩn:

```json
{
    "status_code": 200,
    "error": null,
    "data": {...}
}
```

- **status_code**: HTTP status code (200, 400, 500, etc.)
- **error**: Thông báo lỗi (null nếu thành công)  
- **data**: Dữ liệu trả về (null nếu có lỗi)

## 🔧 Sử dụng

### Với curl
```bash
# Kiểm tra độc tính
curl -X POST "http://localhost:8000/check-toxicity" \
     -H "Content-Type: application/json" \
     -d '{"text": "Xin chào, bạn khỏe không?"}'
```

### Với Python requests
```python
import requests

response = requests.post(
    "http://localhost:8000/check-toxicity",
    json={"text": "Văn bản cần kiểm tra"}
)

result = response.json()
print(result)
```

## 📚 Interactive Documentation

FastAPI tự động tạo documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🐳 Docker

### ⚡ Tính năng Docker optimized

- **Alpine Linux**: Image nhỏ gọn và bảo mật
- **UV Package Manager**: Cài đặt dependencies siêu nhanh
- **Pre-downloaded Model**: Model được download sẵn trong build
- **Multi-stage Build**: Tối ưu kích thước image
- **Cache Optimization**: Build nhanh với Docker layer cache
- **Non-root User**: Bảo mật tối ưu
- **Health Check**: Monitoring tự động

### 🔨 Build với Docker

```bash
# Build production image
docker build -t vihatet5-api .

# Build với cache và verbose
docker build -t vihatet5-api . --progress=plain

# Build specific stage
docker build -t vihatet5-builder --target builder .
```

### 🚀 Run với Docker

```bash
# Run production container
docker run -p 8000:8000 vihatet5-api

# Run với environment variables
docker run -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  vihatet5-api

# Run interactive cho debug
docker run -it -p 8000:8000 vihatet5-api /bin/sh
```

### 📋 Docker Compose

```bash
# Production
docker-compose up -d

# Development với bind mount
docker-compose --profile dev up

# Build và run
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 🔍 Docker image info

```bash
# Check image size
docker images vihatet5-api

# Inspect image
docker inspect vihatet5-api

# Check running containers
docker ps

# Container logs
docker logs <container_id>
```

## 🛠️ Development

### Run in development mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Test runner directly
```bash
python runner.py
```

## 📋 Requirements

- Python 3.8+
- PyTorch
- Transformers
- FastAPI
- Uvicorn

## 📝 Model Info

- **Model**: `tarudesu/ViHateT5-base-HSD`
- **Task**: Toxic Speech Detection cho tiếng Việt
- **Input**: Văn bản tiếng Việt
- **Output**: CLEAN hoặc TOXIC 