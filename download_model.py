#!/usr/bin/env python3
"""
Script để download model HuggingFace trong quá trình build Docker
Sẽ download model vào cache để runtime không cần download
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import sys

MODEL_NAME = "tarudesu/ViHateT5-base-HSD"


def download_model():
    """Download model và tokenizer vào cache"""
    print(f"🔄 Downloading model: {MODEL_NAME}")

    try:
        # Download tokenizer
        print("📝 Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        print(f"✅ Tokenizer downloaded successfully")

        # Download model
        print("🤖 Downloading model...")
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        print(f"✅ Model downloaded successfully")

        # Test model để đảm bảo hoạt động
        print("🧪 Testing model...")
        test_input = "toxic-speech-detection: xin chào"
        input_ids = tokenizer.encode(test_input, return_tensors="pt")
        output_ids = model.generate(input_ids, max_length=256)
        output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        print(f"✅ Model test successful: {output_text}")

        # In thông tin cache
        cache_dir = os.environ.get("TRANSFORMERS_CACHE", "~/.cache/huggingface")
        print(f"📦 Model cached in: {cache_dir}")

        return True

    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False


if __name__ == "__main__":
    success = download_model()
    if not success:
        sys.exit(1)
    print("🎉 Model download completed successfully!")
