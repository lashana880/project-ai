from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import json
import os
import joblib
import pandas as pd
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        # Initialize VADER analyzer
        self.vader = SentimentIntensityAnalyzer()
        
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/wordnet')
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            print("Downloading NLTK data...")
            nltk.download('punkt')
            nltk.download('wordnet')
            nltk.download('omw-1.4')
            
        self.lemmatizer = WordNetLemmatizer()

        # Load complex emotions data
        self.emotions = {}
        try:
            # Construct absolute path to avoid directory issues
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, 'data', 'emotions.json')
            
            with open(data_path, 'r') as f:
                self.emotions = json.load(f)
        except Exception as e:
            print(f"Error loading emotions data: {e}")
            # Fallback empty emotions if file fails
            self.emotions = {}

        # Load ML Model and Vectorizer
        self.ml_model = None
        self.vectorizer = None
        try:
            model_path = os.path.join(base_dir, 'data', 'emotion_model.pkl')
            vec_path = os.path.join(base_dir, 'data', 'tfidf_vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vec_path):
                self.ml_model = joblib.load(model_path)
                self.vectorizer = joblib.load(vec_path)
                print("ML Model loaded successfully")
        except Exception as e:
            print(f"Error loading ML model: {e}")

    def _analyze_segment(self, text):
        """
        Helper method to analyze a single segment of text (sentence or full text).
        """
        # 1. VADER Analysis for basic sentiment and emoji support
        vader_scores = self.vader.polarity_scores(text)
        compound_score = vader_scores['compound']
        
        # Determine basic sentiment label
        if compound_score >= 0.05:
            sentiment = "Positive"
        elif compound_score <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # 2. TextBlob Analysis for Subjectivity
        blob = TextBlob(text)
        subjectivity = blob.sentiment.subjectivity

        # 3. Complex Emotion Analysis (NLP Improved)
        # Tokenize and Lemmatize
        words = nltk.word_tokenize(text.lower())
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]
        
        emotion_scores = {}
        total_emotion_hits = 0
        
        for emotion, keywords in self.emotions.items():
            count = 0
            # Check for matches in lemmatized words
            for word in lemmatized_words:
                if word in keywords:
                    count += 1
            
            # Also check original words in case keywords aren't base forms
            for word in words:
                if word in keywords and word not in lemmatized_words: # Avoid double counting if lemma == word
                     count += 1

        if count > 0:
                emotion_scores[emotion] = count
                total_emotion_hits += count
        
        # Calculate percentages from keywords
        emotion_percentages = {}
        if total_emotion_hits > 0:
            for emotion, count in emotion_scores.items():
                emotion_percentages[emotion] = (count / total_emotion_hits) * 100

        # 4. Integrate ML Predictions (Hybrid Approach)
        if self.ml_model and self.vectorizer:
            try:
                # Vectorize text
                text_vec = self.vectorizer.transform([text])
                
                # Get probabilities
                classes = self.ml_model.classes_
                probs = self.ml_model.predict_proba(text_vec)[0]
                
                # Map ML labels to JSON keys
                label_map = {
                    'joy': 'Happy',
                    'sadness': 'Sad',
                    'anger': 'Anger',
                    'fear': 'Fear',
                    'surprise': 'Surprise',
                    'love': 'Love'
                }
                
                for label, prob in zip(classes, probs):
                    mapped_label = label_map.get(label, label.capitalize())
                    ml_score = prob * 100  # Convert to percentage
                    
                    # Blend strategies:
                    # If keyword score exists, average it with ML score
                    # If not, use ML score
                    if mapped_label in emotion_percentages:
                        emotion_percentages[mapped_label] = (emotion_percentages[mapped_label] + ml_score) / 2
                    else:
                        emotion_percentages[mapped_label] = ml_score
                        
            except Exception as e:
                print(f"ML Prediction error: {e}")

        # Round all final scores
        for k, v in emotion_percentages.items():
            emotion_percentages[k] = round(v, 1)
        
        return {
            "text": text,
            "polarity": round(compound_score, 2),
            "subjectivity": round(subjectivity, 2),
            "sentiment": sentiment,
            "emotions": emotion_percentages
        }

    def analyze(self, text):
        """
        Analyzes the text as a paragraph, providing overall stats and sentence breakdown.
        """
        # Overall Analysis
        overall_result = self._analyze_segment(text)
        
        # Sentence-by-Sentence Analysis
        sentences = nltk.sent_tokenize(text)
        sentence_results = []
        
        for sentence in sentences:
            sentence_results.append(self._analyze_segment(sentence))
            
        overall_result['sentence_breakdown'] = sentence_results
        return overall_result
