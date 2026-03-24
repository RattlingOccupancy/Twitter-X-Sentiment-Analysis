import contractions

class TextNormalizer:
    def to_lower(self, text):
        return text.lower()

    def expand_contractions(self, text):
        return contractions.fix(text)

    def normalize(self, text):
        text = self.expand_contractions(text)
        text = self.to_lower(text)
        return text