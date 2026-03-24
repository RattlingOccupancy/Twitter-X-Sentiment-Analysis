from transformers import AutoTokenizer
from preprocessing.config import MODEL_NAME, MAX_LENGTH

class TokenizerModule:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(self, text):
        return self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )