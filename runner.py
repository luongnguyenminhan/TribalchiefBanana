from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Tải mô hình và tokenizer
tokenizer = AutoTokenizer.from_pretrained("tarudesu/ViHateT5-base-HSD")
model = AutoModelForSeq2SeqLM.from_pretrained("tarudesu/ViHateT5-base-HSD")

def clean_text(text):
    # Bắt buộc thành unicode string, loại ký tự lạ
    if not isinstance(text, str):
        text = str(text)
    return text.encode("utf-8", "ignore").decode("utf-8").strip()

def check_toxic(text):
    text = clean_text(text)
    prefix = "toxic-speech-detection"
    input_text = f"{prefix}: {text}"

    # Tokenize an toàn
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Sinh kết quả
    output_ids = model.generate(input_ids, max_length=256)

    # Giải mã
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return output_text
