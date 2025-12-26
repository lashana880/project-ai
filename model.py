from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import json
import os

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
        
        # Calculate percentages if we found any emotions
        emotion_percentages = {}
        if total_emotion_hits > 0:
            for emotion, count in emotion_scores.items():
                emotion_percentages[emotion] = round((count / total_emotion_hits) * 100, 1)
        
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
