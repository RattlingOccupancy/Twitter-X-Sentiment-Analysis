import re

class TextCleaner:
    def remove_urls(self, text):
        return re.sub(r"http\S+|www\S+", "", text)

    def remove_mentions(self, text):
        return re.sub(r"@\w+", "", text)

    def remove_extra_spaces(self, text):
        return re.sub(r"\s+", " ", text).strip()

    def clean(self, text):
        text = self.remove_urls(text)
        text = self.remove_mentions(text)
        text = self.remove_extra_spaces(text)
        return text