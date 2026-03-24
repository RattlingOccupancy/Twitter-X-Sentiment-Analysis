import emoji

class EmojiHandler:
    def convert_emojis(self, text):
        text = emoji.demojize(text)
        text = text.replace(":", " ")
        return text