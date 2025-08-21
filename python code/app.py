# import required libraries
from flask import Flask, request, jsonify, render_template
import json
from pathlib import Path

# import tweet fetching and sentiment prediction functions from main.py
from main import fetch_tweets, predict_sentiment

# create flask app instance and set static folder for templates
app = Flask(__name__, static_folder='templates')


# route to serve css file
@app.route('/style.css')
def serve_css():
    # read and return css file content
    with open('templates/style.css', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}


# route to serve javascript file
@app.route('/script.js')
def serve_js():
    # read and return js file content
    with open('templates/script.js', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/javascript'}


# route to render homepage
@app.route('/')
def home():
    return render_template('index.html')


# route to handle tweet analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # check if data is sent as json or form-data
        if request.is_json:
            data = request.get_json()
            topic = data.get('topic', '')
        else:
            topic = request.form.get('topic', '')

        # validate user input
        if not topic:
            return jsonify({
                'success': False,
                'error': 'please enter a topic to analyze'
            })

        # fetch tweets based on the given topic
        tweets = fetch_tweets(topic, 20)

        # handle case when no tweets are found
        if not tweets:
            return jsonify({
                'success': False,
                'error': 'no tweets found for this topic. try another keyword.'
            })

        # perform sentiment prediction on fetched tweets
        results = predict_sentiment(tweets)

        # return json response with detailed emotion data
        return jsonify({
            'success': True,
            'topic': topic,
            'total_tweets': len(tweets),
            'emotion_counts': results['emotion_counts'],
            'emotion_percentages': results['emotion_percentages'],
            'dominant': results['dominant_emotion']
        })

    except Exception as e:
        # log any unexpected errors
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


# entry point of the flask application
if __name__ == '__main__':
    app.run(debug=True)
