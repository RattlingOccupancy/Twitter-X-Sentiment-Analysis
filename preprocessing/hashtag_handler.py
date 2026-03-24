import re

class HashtagHandler:
    def process_hashtags(self, text):
        # #happyLife → happyLife
        text = re.sub(r"#(\w+)", r"\1", text)
        return text