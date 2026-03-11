import pyttsx3

# Initialize engine
engine = pyttsx3.init()

# Set female voice (check available voices)
voices = engine.getProperty('voices')
for v in voices:
    # Usually female voices have "Female" or "Zira" on Windows
    if "female" in v.name.lower() or "zira" in v.name.lower():
        engine.setProperty('voice', v.id)
        break

# Speed
engine.setProperty('rate', 200)  # 200 words per minute, adjust for faster/slower

def speak(text):
    """
    Blocking TTS: speaks the text and waits until finished
    """
    engine.say(text)
    engine.runAndWait()
