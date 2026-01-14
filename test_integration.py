from model import SentimentAnalyzer
import json

def test_analyzer():
    print("Initializing Analyzer (this should load the ML model and vectorizer)...")
    analyzer = SentimentAnalyzer()
    
    test_cases = [
        "I am so happy and excited about the new project!",
        "I feel really sad and lonely today.",
        "That person made me so angry!",
        "I am terrified of the dark.",
        "I was shocked by the surprise party.",
        "I love my family so much."
    ]
    
    print("\nRunning Test Cases:")
    for text in test_cases:
        print(f"\nText: {text}")
        result = analyzer.analyze(text)
        print("Emotions:", json.dumps(result['emotions'], indent=2))
        
        # Simple assertion checks
        emotions = result['emotions']
        if "happy" in text.lower() and emotions.get("Happy", 0) < 50:
             print("WARNING: Low Happy score for happy text")
        if "sad" in text.lower() and emotions.get("Sad", 0) < 50:
             print("WARNING: Low Sad score for sad text")

if __name__ == "__main__":
    test_analyzer()
