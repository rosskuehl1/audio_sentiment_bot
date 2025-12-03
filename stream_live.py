# stream_live.py
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sentiment_analyzer = SentimentIntensityAnalyzer()

r = sr.Recognizer()
m = sr.Microphone()

print("Speak now… (press Ctrl+C to stop)")
with m as source:
    r.adjust_for_ambient_noise(source)
    while True:
        try:
            audio = r.listen(source, phrase_time_limit=5)  # 5s window
            text = r.recognize_google(audio)
            scores = sentiment_analyzer.polarity_scores(text)
            compound = scores["compound"]
            if compound >= 0.05:
                label = "POSITIVE"
                confidence = compound
            elif compound <= -0.05:
                label = "NEGATIVE"
                confidence = abs(compound)
            else:
                label = "NEUTRAL"
                confidence = 1 - abs(compound)

            print(f"\nText: {text}\nSentiment: {label} ({confidence:.2f})\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
