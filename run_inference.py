import sys
import io
import json
from inference_pipeline import EmotionInferencePipeline

# Fix potential Windows emoji printing issues
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    pipeline = EmotionInferencePipeline()

    # Define a variable that contains multiple inputs for batch analysis
    topic_data = [
        "I am so happy that I won the lottery! 🥳 #blessed",
        "I am really disappointed in the service I received today. 😡",
        "Wait, what just happened? I didn't see that coming at all! 😮",
        "This is a disaster, I am so angry right now!! 😡",
        "I feel so sad and lonely today... 😢",
        "Just a normal day at the office. 😐",
        "This is disgusting, how can people do this? 🤢",
        "Everything is working perfectly, I'm so excited! 🚀",
        "I'm a bit worried about the final exam next week. 😰"
    ]

    print("\n" + "="*60)
    print("BATCH EMOTION ANALYSIS (AGGREGATED METRICS)")
    print("="*60)

    # Perform batch prediction
    results = pipeline.predict_batch(topic_data)

    if results and results["success"]:
        print(f"\nTotal inputs analyzed: {results['total_count']}")
        print(f"Dominant Emotion:      {results['dominant_emotion'].upper()}")
        
        print("\nEmotion Distribution:")
        print("-" * 30)
        for label in results['emotion_counts']:
            count = results['emotion_counts'][label]
            percent = results['emotion_percentages'][label]
            # Create a simple visual bar
            bar = "█" * int(percent / 5)
            print(f"{label:10}: {count:2} ({percent:>5.2f}%) {bar}")
        
        print("-" * 30)
        

