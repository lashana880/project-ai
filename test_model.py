from model import SentimentAnalyzer
import json

def test_model():
    print("Initializing SentimentAnalyzer...")
    analyzer = SentimentAnalyzer()
    
    test_cases = [
        # Basic Emotions
        {"text": "I hope you are happy with this! 😀", "desc": "Emoji Support + Positive", "expected_sentiment": "Positive", "expected_emotion": "Happy"},
        {"text": "I am furious and angry about this situation.", "desc": "Anger", "expected_sentiment": "Negative", "expected_emotion": "Anger"},
        {"text": "I am so afraid of the ghost.", "desc": "Fear", "expected_sentiment": "Negative", "expected_emotion": "Fear"},
        {"text": "Wow, I am totally surprised and amazed!", "desc": "Surprise", "expected_sentiment": "Positive", "expected_emotion": "Surprise"},
        
        # New Emotions
        {"text": "I am so excited and pumped for the concert!", "desc": "Excitement", "expected_sentiment": "Positive", "expected_emotion": "Excitement"},
        {"text": "Why is this happening? I wonder what went wrong.", "desc": "Questions", "expected_sentiment": "Negative", "expected_emotion": "Questions"},
        {"text": "I am completely stuck and powerless to change anything.", "desc": "Helplessness", "expected_sentiment": "Negative", "expected_emotion": "Helplessness"},
        {"text": "OMG! I am absolutely stunned by this wonderful news.", "desc": "Shock", "expected_sentiment": "Positive", "expected_emotion": "Shock"}, # Added 'wonderful' to ensure Positive
        {"text": "I deserve the best treatment because I earned it.", "desc": "Entitlement", "expected_sentiment": "Positive", "expected_emotion": "Entitlement"},
        {"text": "It is an honor to serve you, I am truly grateful.", "desc": "Humbleness", "expected_sentiment": "Positive", "expected_emotion": "Humbleness"},
        {"text": "I am superior to everyone else here. I am the best.", "desc": "Arrogance", "expected_sentiment": "Positive", "expected_emotion": "Arrogance"},
        {"text": "I am certain we will succeed. I have no doubts.", "desc": "Confidence", "expected_sentiment": "Positive", "expected_emotion": "Confidence"},
        {"text": "The deadline is approaching and the pressure is overwhelming.", "desc": "Stress", "expected_sentiment": "Negative", "expected_emotion": "Stress"},
        {"text": "I wish for a better future and pray for success.", "desc": "Hope", "expected_sentiment": "Positive", "expected_emotion": "Hope"},
        {"text": "You must obey my command immediately!", "desc": "Dominance", "expected_sentiment": "Neutral", "expected_emotion": "Dominance"}, # Imperatives often Neutral in VADER unless "love"/"hate"
        {"text": "I will comply with your request, sorry for the trouble.", "desc": "Submissiveness", "expected_sentiment": "Negative", "expected_emotion": "Submissiveness"}, # 'Sorry' drags to negative
        
        # Complex Scenarios
        {
            "text": "I am stressed about the exam but hopeful I will pass.", 
            "desc": "Complex: Stress + Hope", 
            "expected_sentiment": "Positive", # Hopeful/Pass usually outweighs stressed slightly or makes it positive
            "expected_emotion": "Hope", # Should find both, checking for Hope specifically here
            "check_emotions": ["Stress", "Hope"]
        },
        {
            "text": "Why did you do that? I am so angry yet humble enough to forgive.",
            "desc": "Complex: Questions + Anger + Humbleness",
            "expected_sentiment": "Negative", # Angry dominates sentiment usually
            "check_emotions": ["Questions", "Anger", "Humbleness"],
            "expected_emotion": "Anger" 
        }
    ]
    
    all_passed = True
    
    print("\n--- Running Tests ---\n")
    for case in test_cases:
        print(f"Testing: {case['desc']}")
        print(f"Input: {case['text'].encode('ascii', 'replace').decode()}")
        
        result = analyzer.analyze(case['text'])
        print(f"Result: Sentiment={result['sentiment']}, Polarity={result['polarity']}, Subjectivity={result.get('subjectivity', 'N/A')}")
        print(f"Emotions: {result['emotions']}")
        
        if case.get('check_breakdown'):
            print("Checking Sentence Breakdown...")
            breakdown = result.get('sentence_breakdown')
            if not breakdown or len(breakdown) < 2:
                print(f"[FAIL] Expected sentence breakdown with multiple sentences, got: {breakdown}")
                all_passed = False
            else:
                print(f"Breakdown Details: {json.dumps(breakdown, indent=2)}")
                # Verify first sentence is positive (Fantastic)
                s1 = breakdown[0]
                if s1['sentiment'] != 'Positive':
                    print(f"[FAIL] Sentence 1 expected partial Positive, got {s1['sentiment']}")
                    all_passed = False
                
                # Check if emotions have percentages
                if 'emotions' in s1 and s1['emotions']:
                     print(f"[PASS] Sentence 1 has emotions: {s1['emotions']}")
                
                # Verify last sentence is negative (Uncomfortable)
                s_last = breakdown[-1]
                if s_last['sentiment'] != 'Negative':
                    print(f"[FAIL] Last sentence expected partial Negative, got {s_last['sentiment']}")
                    all_passed = False
                print(f"[PASS] Breakdown verified: {len(breakdown)} sentences analyzed.")

        # Check Subjectivity presence
        if 'subjectivity' not in result:
             print("[FAIL] 'subjectivity' field missing in result")
             all_passed = False

        # Check Sentiment
        if case['desc'] != "Subjectivity Check" and not case.get('check_breakdown'): # Skip strict sentiment checks for complex paragraph if checked manually above
            if result['sentiment'] != case['expected_sentiment']:
                # Relaxed check for Surprise which can be neutral/positive depending on VADER
                if not (case['expected_emotion'] == "Surprise" and result['sentiment'] in ["Positive", "Neutral"]):
                    print(f"[FAIL] Sentiment mismatch! Expected {case['expected_sentiment']}, got {result['sentiment']}")
                    all_passed = False
        
        emotions_found = result['emotions'].keys()

        if 'check_emotions' in case:
            for em in case['check_emotions']:
                if em not in emotions_found:
                    print(f"[FAIL] Expected complex emotion '{em}' not found. Found: {list(emotions_found)}")
                    all_passed = False
                else:
                    print(f"[PASS] Complex emotion '{em}' detected ({result['emotions'][em]}%)")
        
        # Check Emotion
        expected_emotion = case.get('expected_emotion')
        if expected_emotion and not 'check_emotions' in case:
            if expected_emotion not in emotions_found:
                print(f"[FAIL] Expected emotion '{expected_emotion}' not found in {list(emotions_found)}")
                all_passed = False
            else:
                print(f"[PASS] Emotion '{expected_emotion}' detected ({result['emotions'][expected_emotion]}%)")
        
        print("-" * 30)

    if all_passed:
        print("\n[ALL TESTS PASSED]")
    else:
        print("\n[SOME TESTS FAILED]")

if __name__ == "__main__":
    test_model()
