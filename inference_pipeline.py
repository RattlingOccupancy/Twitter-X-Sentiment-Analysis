import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import os

# Fix SSL error if it exists
if "SSL_CERT_FILE" in os.environ:
    os.environ.pop("SSL_CERT_FILE")

# Import your preprocessing pipeline
try:
    from preprocessing.pipeline import PreprocessingPipeline
except ImportError:
    # If not found, we will redefine a minimal one or handle it
    print("Warning: PreprocessingPipeline not found. Using raw text.")
    class PreprocessingPipeline:
        def process(self, text): return {"cleaned_text": text}

class EmotionInferencePipeline:
    def __init__(self, model_name="j-hartmann/emotion-english-distilroberta-base"):
        print("Loading model and tokenizer...")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load tokenizer and model for j-hartmann/emotion-english-distilroberta-base
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

        self.model.to(self.device)
        self.model.eval()

        self.preprocessor = PreprocessingPipeline()

        # Model labels in correct order for j-hartmann model
        self.labels = [
            "anger",
            "disgust",
            "fear",
            "joy",
            "neutral",
            "sadness",
            "surprise"
        ]

    def predict(self, text):
        # Step 1: Preprocess text using existing pipeline
        try:
            processed = self.preprocessor.process(text)
            cleaned_text = processed["cleaned_text"]
        except Exception as e:
            print(f"Preprocessing error: {e}")
            cleaned_text = text

        # Step 2: Tokenize using specific model tokenizer
        inputs = self.tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

        # Step 3: Model inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probs = F.softmax(logits, dim=1)

        # Step 4: Get prediction
        # Get index of max probability
        predicted_class_id = torch.argmax(probs, dim=1).item()
        
        # Construct the response
        predicted_label = self.labels[predicted_class_id]
        confidence = probs[0][predicted_class_id].item()

        # Step 5: Full probability distribution
        all_scores = {
            self.labels[i]: round(probs[0][i].item(), 4)
            for i in range(len(self.labels))
        }

        # Sort all_scores by value descending for better display
        sorted_scores = dict(sorted(all_scores.items(), key=lambda item: item[1], reverse=True))

        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "predicted_emotion": predicted_label,
            "confidence": round(confidence, 4),
            "all_emotions": sorted_scores
        }
    def predict_batch(self, texts):
        if not texts:
            return None

        # Step 1: Preprocess all texts
        cleaned_texts = []
        for t in texts:
            try:
                processed = self.preprocessor.process(t)
                cleaned_texts.append(processed["cleaned_text"])
            except Exception:
                cleaned_texts.append(t)

        # Step 2: Tokenize using batch mode
        inputs = self.tokenizer(
            cleaned_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

        # Step 3: Model inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probs = F.softmax(logits, dim=1)

        # Step 4: Get predictions
        batch_results = []
        emotion_counts = {label: 0 for label in self.labels}
        
        for i in range(len(texts)):
            # Get index of max probability for this item
            predicted_class_id = torch.argmax(probs[i], dim=0).item()
            label = self.labels[predicted_class_id]
            confidence = probs[i][predicted_class_id].item()
            
            emotion_counts[label] += 1
            
            batch_results.append({
                "original_text": texts[i],
                "cleaned_text": cleaned_texts[i],
                "predicted_emotion": label,
                "confidence": round(confidence, 4)
            })

        # Step 5: Aggregate metrics
        total = len(texts)
        emotion_percentages = {label: round((count / total) * 100, 2) for label, count in emotion_counts.items()}
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)

        return {
            "success": True,
            "total_count": total,
            "emotion_counts": emotion_counts,
            "emotion_percentages": emotion_percentages,
            "dominant_emotion": dominant_emotion,
            "predictions": batch_results
        }
