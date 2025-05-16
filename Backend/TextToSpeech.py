import pygame  # For handling audio playback
import random  # For generating random choices
import asyncio  # For asynchronous operations
import edge_tts  # For text-to-speech functionality
import os  # For file path handling
import time  # For adding delay in case of file lock issues
from dotenv import dotenv_values  # For reading environment variables from a .env file

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-AriaNeural")

# Define speech file path
file_path = os.path.join(os.getcwd(), "Data", "speech.mp3")

# Ensure Data directory exists
if not os.path.exists("Data"):
    os.makedirs("Data")

# Initialize pygame mixer only if it hasn't been initialized
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing pygame: {e}")

async def TextToAudioFile(text) -> None:
    """Converts text to an audio file using Edge TTS."""
    try:
        # Wait until the previous file is not in use
        for _ in range(5):  # Try up to 5 times
            try:
                if os.path.exists(file_path):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()  # Ensure file is not in use
                    os.remove(file_path)
                break
            except PermissionError:
                time.sleep(0.5)  # Wait a moment and retry
        
        # Generate new speech
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)
    except Exception as e:
        print(f"Error generating speech: {e}")

def TTS(Text, func=lambda r=None: True):
    """Handles Text-to-Speech (TTS) playback."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(TextToAudioFile(Text))  # Convert text to audio file

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if func() == False:  # Stop if external function returns False
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            if callable(func):
                func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.unload()  # Ensure file is released after use
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    """Handles longer text-to-speech by splitting long texts into manageable parts."""
    sentences = Text.split(". ")  # Splitting sentences carefully
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(sentences) > 4 and len(Text) >= 250:
        TTS(". ".join(sentences[:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    while True:
        text = input("Enter the text: ")
        if text.lower() == "exit":
            break
        TextToSpeech(text)
