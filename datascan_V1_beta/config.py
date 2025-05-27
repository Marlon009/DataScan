class Config:
    MODEL_NAME = "pierreguillou/gpt2-small-portuguese"
    PAD_TOKEN = "<|pad|>"
    MAX_TOKENS = 64
    MAX_CONTEXT_LENGTH = 2
    USE_QUANTIZATION = False
    DEVICE = "cpu"
    TEMP_DIR = "temp_processing"
    BACKUP_DIR = "backups"
    GENERATION_CONFIG = {
        "max_new_tokens": 150,
        "temperature": 0.3,
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 2.0,
        "no_repeat_ngram_size": 3,
        "do_sample": True,
        "num_beams": 1,
        "pad_token_id": 50256,
    }
