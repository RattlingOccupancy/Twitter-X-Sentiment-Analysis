# import required libraries
import os
import re
import json
import pickle
import logging
import subprocess
from pathlib import Path

import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import requests

# download stopwords silently if not available
nltk.download("stopwords", quiet=True)

# configure logging for better debugging and tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# set base directory for accessing model files and scripts
BASE_DIR = Path(__file__).resolve().parent

# load trained sentiment analysis model and supporting objects
model = pickle.load(open(BASE_DIR.parent / "model" / "trained_model.sav", "rb"))
vectorizer = pickle.load(open(BASE_DIR.parent / "model" / "tfidf_vectorizer.sav", "rb"))
encoder = pickle.load(open(BASE_DIR.parent / "model" / "label_encoder.sav", "rb"))

# list of emotions used by the model
EMOTIONS = ["joy", "sadness", "fear", "anger", "surprise", "neutral", "disgust", "shame"]

# initialize stemmer for text preprocessing
port_stem = PorterStemmer()


# function to apply stemming and remove unwanted characters
def stemming(content: str) -> str:
    # remove non-alphabetic characters and convert to lowercase
    stemmed_content = re.sub("[^a-zA-Z]", " ", content)
    stemmed_content = stemmed_content.lower().split()
    
    # remove stopwords and apply stemming
    filtered = [port_stem.stem(word) for word in stemmed_content if word not in stopwords.words("english")]
    return " ".join(filtered)


# function to preprocess a series of text data
def preprocess_text(text_series: pd.Series) -> pd.Series:
    return text_series.apply(stemming)


# function to fetch tweets using node.js script
def fetch_tweets(topic: str, count: int) -> list[str]:
    try:
        logging.info(f"fetching tweets for topic: {topic}")

        # define output path for node.js results
        output_path = BASE_DIR / 'tweets.json'
        if output_path.exists():
            output_path.unlink()

        # define node.js script path
        node_script = BASE_DIR / 'node' / 'tweet_fetch.js'
        if not node_script.exists():
            raise FileNotFoundError(f"node script not found at {node_script}")

        # run the node.js script as a subprocess
        result = subprocess.run(
            ['node', str(node_script), topic, str(count)],
            check=True,
            capture_output=True,
            text=True,
            timeout=200,
            encoding='utf-8',
            env=dict(os.environ, NODE_OPTIONS='--unhandled-rejections=strict')
        )

        # log node.js output and errors if any
        logging.info("node.js output:\n" + result.stdout)
        if result.stderr:
            logging.error("node.js errors:\n" + result.stderr)

        # ensure output file is created
        if not output_path.exists():
            raise RuntimeError("output file not created by node.js script")

        # read fetched tweets from the generated json file
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data.get('success'):
                raise ValueError("node script reported failure")

            # return list of tweet texts
            return [tweet['text'] for tweet in data['tweets']]

    except subprocess.CalledProcessError as e:
        logging.error(
            f"node.js failed with code {e.returncode}\n"
            f"command: {e.cmd}\n"
            f"output: {e.stdout}\n"
            f"error: {e.stderr}"
        )
        return []
    except Exception as e:
        logging.exception("critical error in fetch_tweets:")
        return []


# function to predict sentiment/emotions from a list of tweets
def predict_sentiment(tweet_texts: list[str]) -> dict:
    if not tweet_texts:
        raise ValueError("no tweets to analyze")

    # preprocess tweet texts
    processed = preprocess_text(pd.Series(tweet_texts))
    if processed.empty:
        raise ValueError("no valid tweets after preprocessing")

    # vectorize tweets and predict emotions using the trained model
    vectorized = vectorizer.transform(processed)
    predictions = model.predict(vectorized)
    predicted_emotions = encoder.inverse_transform(predictions)

    # calculate emotion counts and percentages
    emotion_counts = {emotion: np.count_nonzero(predicted_emotions == emotion) for emotion in EMOTIONS}
    total = len(predicted_emotions)
    emotion_percentages = {emotion: (count / total) * 100 for emotion, count in emotion_counts.items()}

    # find the dominant emotion
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)

    # function to safely convert numpy types to native python types
    def convert_numpy(obj):
        if isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    # construct final result and return
    result = {
        "emotion_counts": emotion_counts,
        "emotion_percentages": emotion_percentages,
        "dominant_emotion": dominant_emotion
    }
    return convert_numpy(result)
