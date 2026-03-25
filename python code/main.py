import sys
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

# Add root directory to sys.path to allow importing from top-level modules
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from inference_pipeline import EmotionInferencePipeline


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

# initialize stemming for text preprocessing (legacy, but keeping if needed elsewhere)
port_stem = PorterStemmer()

# Initialize the new transformer pipeline
# We set this as None and load it when needed or at startup
_emotion_pipeline = None

def get_emotion_pipeline():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        # Add root to path to ensure inference_pipeline is findable
        root_dir = Path(__file__).resolve().parent.parent
        if str(root_dir) not in sys.path:
            sys.path.append(str(root_dir))
        _emotion_pipeline = EmotionInferencePipeline()
    return _emotion_pipeline


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
        output_path = root_dir / 'tweets.json'
        if output_path.exists():
            output_path.unlink()

        # define node.js script path
        node_script = root_dir / 'node' / 'tweet_fetch.js'
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

    pipeline = get_emotion_pipeline()
    results = pipeline.predict_batch(tweet_texts)

    if not results or not results["success"]:
        raise ValueError("emotion analysis failed")

    # Map the results to the format expected by app.py
    # app.py expects: emotion_counts, emotion_percentages, dominant_emotion (as 'dominant')
    
    return {
        "emotion_counts": results["emotion_counts"],
        "emotion_percentages": results["emotion_percentages"],
        "dominant_emotion": results["dominant_emotion"],
        "individual_results": results["predictions"] # Include the list of processed tweets
    }

