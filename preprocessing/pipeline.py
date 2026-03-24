from preprocessing.cleaner import TextCleaner
from preprocessing.normalizer import TextNormalizer
from preprocessing.hashtag_handler import HashtagHandler
from preprocessing.emoji_handler import EmojiHandler
from preprocessing.tokenizer_module import TokenizerModule


class PreprocessingPipeline:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.normalizer = TextNormalizer()
        self.hashtag_handler = HashtagHandler()
        self.emoji_handler = EmojiHandler()
        self.tokenizer = TokenizerModule()

    def process(self, text):
        # Step 1: Clean
        text = self.cleaner.clean(text)

        # Step 2: Hashtags
        text = self.hashtag_handler.process_hashtags(text)

        # Step 3: Emojis
        text = self.emoji_handler.convert_emojis(text)

        # Step 4: Normalize
        text = self.normalizer.normalize(text)

        # Step 5: Tokenize
        encoded = self.tokenizer.tokenize(text)

        return {
            "cleaned_text": text,
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"]
        }