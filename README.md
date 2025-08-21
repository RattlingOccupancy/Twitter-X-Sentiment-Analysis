# Twitter/X Sentiment Analyzer

This project analyzes recent tweets for a given topic and visualizes the distribution of emotions such as joy, sadness, fear, anger, surprise, neutral, disgust, and shame.

The project uses:
- **Python (Flask)** backend to serve the UI and run ML inference.
- A pre-trained **scikit-learn model** (`trained_model.sav`) with TF-IDF (`tfidf_vectorizer.sav`) and a label encoder (`label_encoder.sav`).
- An unofficial tweet fetcher using **Rettiwt-API** via `node/tweet_fetch.js`.
- A simple **HTML/CSS/JS frontend** in the `templates/` directory.

## Unofficial Tweet Fetcher

This project uses the **[Rettiwt-API](https://github.com/Rishikant181/Rettiwt-API)** — an **unofficial, open-source tweet fetching API** built by the community. I chose this approach instead of the **official Twitter API** because:

- The **official API** has **strict rate limits**.
- Accessing higher request quotas requires a **paid subscription**.
- Rettiwt-API leverages Twitter's internal endpoints to fetch tweets more flexibly.

> ⚠️ **Disclaimer**: Since Rettiwt-API is unofficial and reverse-engineered, Twitter may change its internal APIs at any time, which could break this implementation.

## Project Structure

```
├── .gitignore
├── model/
│   ├── label_encoder.sav
│   ├── tfidf_vectorizer.sav
│   └── trained_model.sav
├── node/
│   └── tweet_fetch.js
├── python code/
│   ├── app.py
│   └── main.py
├── requirements/
│   ├── js_requirements.txt
│   └── py_requirements.txt
├── template/
│   ├── index.html
│   ├── script.js
│   └── style.css

```

## Prerequisites

- Windows 10/11 or macOS/Linux
- Python 3.10–3.12 recommended
- Node.js 18+ (required by `rettiwt-api`)

Ensure both `python` and `node` are available in your system's PATH.

## Setup and Installation

### 1. Install Python Dependencies

First, create and activate a virtual environment.

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements/py_requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/py_requirements.txt
```
> **Note**: The first run will automatically download the NLTK stopwords package.

### 2. Install Node.js Dependencies

Install the required Node packages from inside the `node` folder.

```bash
cd node
npm install
cd ..
```

### 3. Configure Twitter API (rettiwt-api)

The Node script `node/tweet_fetch.js` requires working `rettiwt-api` keys. Replace the placeholder values in the `apiKeys` array with your own valid keys.

Edit `node/tweet_fetch.js`:
```javascript
const apiKeys = [
  "YOUR_ENCODED_API_KEY_HERE",
  // You can add more keys here to rotate through them
];
```

## How to Run

With your Python virtual environment activated, run the Flask server from the project root:

```bash
python app.py
```

The server will start at **http://127.0.0.1:5000/**.

1.  Open the URL in your web browser.
2.  Enter a topic (e.g., `football` or `trump`).
3.  Click **Analyze**.
4.  The server will then:
    - Call the Node script to fetch up to 20 recent, English-language tweets for the topic.
    - Preprocess the text and run the ML model on each tweet.
    - Send the aggregated emotion percentages and counts back to the UI for display.

## Common Issues and Fixes

-   **Node not found**: Ensure Node.js 18+ is installed correctly and that running `node -v` in your terminal prints a version number.
-   **API rate limits or invalid keys**: The Node script rotates through the keys provided in the `apiKeys` array. If you see repeated failures, your keys may be invalid or rate-limited. Replace them with new, valid keys.
-   **Empty results**: The topic you entered may be too narrow or have no recent tweets. Try a broader keyword.
-   **NLTK stopwords download fails**: The stopwords are downloaded automatically. If you are behind a corporate firewall, you may need to pre-download them manually by running this Python script:
    ```python
    import nltk
    nltk.download('stopwords')
    ```
-   **Python version conflicts**: Ensure you are using a supported Python version (3.10-3.12) and a fresh virtual environment to avoid dependency issues.

## Development Notes

-   Flask serves `templates/index.html` at the root URL (`/`) and proxies the static files `style.css` and `script.js`.
-   The `main.py` script loads the model, vectorizer, and encoder from the `model/` folder using paths relative to its own location, allowing the application to be run from any working directory.
-   The Node.js script (`node/tweet_fetch.js`) writes a temporary `tweets.json` file in the project root, which `main.py` then reads for processing.

## Scripts and Commands Cheat Sheet

-   **Create venv and install Python dependencies:**
    -   **Windows:** `python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements/py_requirements.txt`
    -   **macOS/Linux:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements/py_requirements.txt`
-   **Install Node dependencies:**
    -   `cd node && npm install && cd ..`
-   **Run the application:**
    -   `python app.py`

