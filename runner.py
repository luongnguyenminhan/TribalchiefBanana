from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "tarudesu/ViHateT5-base-HSD"

# Global variables để cache model và tokenizer
_tokenizer = None
_model = None
_model_loaded = False


def get_model_and_tokenizer():
    """
    Lazy loading cho model và tokenizer
    Chỉ load một lần và cache lại
    """
    global _tokenizer, _model, _model_loaded

    if _model_loaded:
        return _tokenizer, _model

    try:
        logger.info(f"🔄 Loading model: {MODEL_NAME}")

        # Kiểm tra cache directory
        cache_dir = os.environ.get("TRANSFORMERS_CACHE", "~/.cache/huggingface")
        logger.info(f"📦 Using cache directory: {cache_dir}")

        # Load tokenizer
        logger.info("📝 Loading tokenizer...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        # Load model
        logger.info("🤖 Loading model...")
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

        _model_loaded = True
        logger.info("✅ Model and tokenizer loaded successfully!")

        return _tokenizer, _model

    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise RuntimeError(f"Failed to load model {MODEL_NAME}: {e}")


def clean_text(text):
    """Làm sạch và chuẩn hóa text input"""
    if not isinstance(text, str):
        text = str(text)
    return text.encode("utf-8", "ignore").decode("utf-8").strip()


def check_toxic(text):
    """
    Kiểm tra độc tính của văn bản

    Args:
        text (str): Văn bản cần kiểm tra

    Returns:
        str: Kết quả phân loại (CLEAN hoặc TOXIC)

    Raises:
        RuntimeError: Nếu không thể load model
        ValueError: Nếu input text không hợp lệ
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty")

    try:
        # Get cached model và tokenizer
        tokenizer, model = get_model_and_tokenizer()

        # Clean text
        text = clean_text(text)
        prefix = "toxic-speech-detection"
        input_text = f"{prefix}: {text}"

        logger.debug(f"🔍 Processing text: {input_text[:50]}...")

        # Tokenize
        input_ids = tokenizer.encode(input_text, return_tensors="pt")

        # Generate prediction
        output_ids = model.generate(input_ids, max_length=256)

        # Decode result
        output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        logger.debug(f"✅ Result: {output_text}")
        return output_text

    except Exception as e:
        logger.error(f"❌ Error in toxicity check: {e}")
        raise


def health_check():
    """
    Kiểm tra trạng thái của model

    Returns:
        dict: Thông tin trạng thái model
    """
    try:
        tokenizer, model = get_model_and_tokenizer()

        # Test với input đơn giản
        test_result = check_toxic("xin chào")

        return {
            "model_loaded": True,
            "model_name": MODEL_NAME,
            "test_result": test_result,
            "status": "healthy",
        }
    except Exception as e:
        return {
            "model_loaded": False,
            "model_name": MODEL_NAME,
            "error": str(e),
            "status": "unhealthy",
        }


# Legacy support - giữ cho compatibility với code cũ
# Chỉ load khi được gọi trực tiếp
if __name__ == "__main__":
    print("=== TOXICITY CHECK ===")

    # Load model khi chạy trực tiếp
    try:
        tokenizer, model = get_model_and_tokenizer()
        print("🎉 Model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        exit(1)

    # Interactive loop
    while True:
        text = input("Nhập văn bản (hoặc gõ 'q' để thoát): ").strip()
        if text.lower() == "q":
            break
        if not text:
            print("=> Bạn chưa nhập gì cả.")
            continue
        try:
            result = check_toxic(text)
            print(f"=> Kết quả: {result}")
        except Exception as e:
            print(f"=> Đã xảy ra lỗi: {e}")
