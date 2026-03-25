import sys
import os
from pathlib import Path

# Fix SSL error caused by incorrect SSL_CERT_FILE environment variable
if "SSL_CERT_FILE" in os.environ:
    os.environ.pop("SSL_CERT_FILE")

# Add the project root to sys.path for direct script execution
sys.path.append(str(Path(__file__).parents[1]))

from preprocessing.pipeline import PreprocessingPipeline

if __name__ == "__main__":
    pipeline = PreprocessingPipeline()

    sample = "OMG!!! I can't believe this.          this is miracle😭😭 #heartbroken @user https://t.co/xyz"

    output = pipeline.process(sample)

    print("Cleaned Text:", output["cleaned_text"])
    print("Input IDs shape:", output["input_ids"].shape)


