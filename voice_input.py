
import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_command(timeout=None, phrase_time_limit=None):
    """
    Listens for a single command. Blocks until speech is fully captured.
    Returns recognized text or None.
    """
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("🔍 Recognizing...")
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"❌ API error: {e}")
        return None
    except OSError as e:
        print(f"❌ Microphone error: {e}")
        return None
