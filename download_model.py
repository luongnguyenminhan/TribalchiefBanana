#!/usr/bin/env python3
"""
Script để download model HuggingFace trong quá trình build Docker
Sẽ download model vào cache để runtime không cần download
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MODEL_NAME = "tarudesu/ViHateT5-base-HSD"


def setup_cache_directory():
    """Setup và kiểm tra cache directory"""
    cache_dir = os.environ.get("TRANSFORMERS_CACHE", "/root/.cache/huggingface")

    # Tạo cache directory nếu chưa có
    os.makedirs(cache_dir, exist_ok=True)
    logger.info(f"📁 Cache directory: {cache_dir}")

    return cache_dir


def download_model():
    """Download model và tokenizer vào cache"""
    logger.info(f"🔄 Starting download for model: {MODEL_NAME}")

    try:
        # Setup cache directory
        cache_dir = setup_cache_directory()

        # Download tokenizer
        logger.info("📝 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=cache_dir)
        logger.info("✅ Tokenizer downloaded successfully")

        # Download model
        logger.info("🤖 Downloading model...")
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, cache_dir=cache_dir)
        logger.info("✅ Model downloaded successfully")

        # Test model để đảm bảo hoạt động
        logger.info("🧪 Testing model functionality...")
        test_cases = ["xin chào", "bạn khỏe không", "cảm ơn bạn"]

        for test_text in test_cases:
            test_input = f"toxic-speech-detection: {test_text}"
            input_ids = tokenizer.encode(test_input, return_tensors="pt")

            # Generate với các tham số tối ưu
            output_ids = model.generate(
                input_ids, max_length=256, do_sample=False, early_stopping=True
            )

            output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            logger.info(f"✅ Test '{test_text}' -> '{output_text}'")

        # Kiểm tra cache size
        try:
            cache_size = get_directory_size(cache_dir)
            logger.info(f"📦 Cache size: {cache_size:.2f} MB")
        except Exception as e:
            logger.warning(f"Could not calculate cache size: {e}")

        # Environment info
        logger.info(f"📦 Model cached in: {cache_dir}")
        logger.info(f"🐍 Python version: {sys.version}")

        return True

    except Exception as e:
        logger.error(f"❌ Error downloading model: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return False


def get_directory_size(path):
    """Tính kích thước directory tính bằng MB"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        logger.warning(f"Error calculating directory size: {e}")
        return 0

    return total_size / (1024 * 1024)  # Convert to MB


def verify_model_files():
    """Verify rằng model files đã được download thành công"""
    cache_dir = os.environ.get("TRANSFORMERS_CACHE", "/root/.cache/huggingface")

    logger.info("🔍 Verifying downloaded model files...")

    # Các files quan trọng cần có
    expected_patterns = [
        "config.json",
        "tokenizer.json",
        "pytorch_model.bin",
        "special_tokens_map.json",
    ]

    found_files = []
    for root, dirs, files in os.walk(cache_dir):
        found_files.extend(files)

    # Check if important files exist
    for pattern in expected_patterns:
        matching_files = [f for f in found_files if pattern in f]
        if matching_files:
            logger.info(f"✅ Found {pattern}: {len(matching_files)} files")
        else:
            logger.warning(f"⚠️  Missing {pattern}")

    logger.info(f"📊 Total files in cache: {len(found_files)}")
    return len(found_files) > 0


def main():
    """Main function"""
    logger.info("🚀 Starting ViHateT5 model download process...")

    try:
        # Download model
        success = download_model()

        if not success:
            logger.error("❌ Model download failed!")
            sys.exit(1)

        # Verify files
        if verify_model_files():
            logger.info("✅ Model files verification passed!")
        else:
            logger.warning("⚠️  Model files verification had issues")

        logger.info("🎉 Model download completed successfully!")
        logger.info("📝 Model is ready for use in production!")

    except KeyboardInterrupt:
        logger.info("🛑 Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
