import os
from groq import Groq

def transcribe_audio(file_path, api_key):
    """
    Transcribes audio using Groq's Whisper API.
    
    Args:
        file_path (str): Path to the audio file.
        api_key (str): Groq API Key.
        
    Returns:
        str: Transcribed text.
    """
    if not api_key:
        raise ValueError("Groq API Key is missing.")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        client = Groq(api_key=api_key)
        
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en", 
                temperature=0.0
            )
        
        return transcription.text
    except Exception as e:
        return f"Error during transcription: {str(e)}"
