from flask import Flask, render_template, request, jsonify
from model import SentimentAnalyzer

app = Flask(__name__)
analyzer = SentimentAnalyzer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
        
    result = analyzer.analyze(text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
