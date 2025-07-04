from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
from runner import check_toxic, health_check

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ViHateT5 Toxicity Detection API",
    description="API để kiểm tra độc tính trong văn bản tiếng Việt sử dụng model ViHateT5-base-HSD",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class TextRequest(BaseModel):
    text: str
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Xin chào, bạn khỏe không?"
            }
        }

class APIResponse(BaseModel):
    status_code: int
    error: Optional[str] = None
    data: Optional[dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status_code": 200,
                "error": None,
                "data": {
                    "input_text": "Xin chào, bạn khỏe không?",
                    "toxicity_result": "CLEAN",
                    "processed": True
                }
            }
        }

@app.get("/", response_model=APIResponse, tags=["Root"])
async def root():
    """Endpoint gốc - Kiểm tra API đang hoạt động"""
    try:
        return APIResponse(
            status_code=200,
            error=None,
            data={
                "message": "ViHateT5 Toxicity Detection API is running",
                "version": "2.0.0",
                "docs": "/docs",
                "health_check": "/health"
            }
        )
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        return APIResponse(
            status_code=500,
            error=f"Internal server error: {str(e)}",
            data=None
        )

@app.post("/check-toxicity", response_model=APIResponse, tags=["Toxicity Detection"])
async def check_toxicity_endpoint(request: TextRequest):
    """
    Kiểm tra độc tính của văn bản tiếng Việt
    
    - **text**: Văn bản cần kiểm tra độc tính (bắt buộc)
    
    **Ví dụ request:**
    ```json
    {
        "text": "Xin chào, bạn khỏe không?"
    }
    ```
    
    **Response sẽ trả về:**
    - CLEAN: Văn bản không độc hại
    - TOXIC: Văn bản có nội dung độc hại
    """
    try:
        # Validate input
        if not request.text or not request.text.strip():
            return APIResponse(
                status_code=400,
                error="Text cannot be empty or whitespace only",
                data=None
            )
        
        # Check length limit
        if len(request.text) > 1000:
            return APIResponse(
                status_code=400,
                error="Text too long. Maximum 1000 characters allowed",
                data=None
            )
        
        logger.info(f"Processing toxicity check for text: {request.text[:50]}...")
        
        # Perform toxicity check
        result = check_toxic(request.text)
        
        logger.info(f"Toxicity check result: {result}")
        
        return APIResponse(
            status_code=200,
            error=None,
            data={
                "input_text": request.text,
                "toxicity_result": result,
                "processed": True,
                "model": "ViHateT5-base-HSD"
            }
        )
    
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return APIResponse(
            status_code=400,
            error=str(ve),
            data=None
        )
    
    except RuntimeError as re:
        logger.error(f"Model error: {re}")
        return APIResponse(
            status_code=503,
            error=f"Model service unavailable: {str(re)}",
            data=None
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in toxicity check: {e}")
        return APIResponse(
            status_code=500,
            error=f"Internal server error: {str(e)}",
            data=None
        )

@app.get("/health", response_model=APIResponse, tags=["Health Check"])
async def health_check_endpoint():
    """
    Kiểm tra trạng thái sức khỏe của server và model
    
    Endpoint này kiểm tra:
    - Trạng thái server
    - Model đã được load hay chưa
    - Test model với input đơn giản
    """
    try:
        logger.info("Performing health check...")
        
        # Check model health
        model_status = health_check()
        
        if model_status["status"] == "healthy":
            return APIResponse(
                status_code=200,
                error=None,
                data={
                    "server_status": "healthy",
                    "model_status": model_status,
                    "api_version": "2.0.0",
                    "endpoints": {
                        "toxicity_check": "/check-toxicity",
                        "health": "/health",
                        "docs": "/docs"
                    }
                }
            )
        else:
            return APIResponse(
                status_code=503,
                error="Model service unavailable",
                data={
                    "server_status": "healthy",
                    "model_status": model_status,
                    "api_version": "2.0.0"
                }
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse(
            status_code=500,
            error=f"Health check failed: {str(e)}",
            data=None
        )

@app.get("/model-info", response_model=APIResponse, tags=["Model Info"])
async def model_info():
    """Thông tin về model đang sử dụng"""
    try:
        return APIResponse(
            status_code=200,
            error=None,
            data={
                "model_name": "tarudesu/ViHateT5-base-HSD",
                "model_type": "Text-to-Text Generation",
                "task": "Toxic Speech Detection",
                "language": "Vietnamese",
                "base_model": "T5",
                "description": "Fine-tuned T5 model for Vietnamese hate speech detection"
            }
        )
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return APIResponse(
            status_code=500,
            error=f"Internal server error: {str(e)}",
            data=None
        )

if __name__ == "__main__":
    logger.info("🚀 Starting ViHateT5 Toxicity Detection API...")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 