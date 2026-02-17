# 🎓 Lecture Voice-to-Notes Generator

Transform your lecture recordings into clear notes, quizzes, and flashcards instantly using AI.

## Features

- 🎤 **Audio Transcription**: Convert audio/video lectures to text using Groq's Whisper
- 📚 **Study Notes**: Generate comprehensive, structured study notes
- ❓ **Interactive Quiz**: Test your knowledge with auto-generated quizzes
- 🃏 **Flashcards**: Create flashcards with flip animations for effective learning
- 🔗 **URL Support**: Download and process lectures from YouTube and other platforms

## Tech Stack

- **Frontend**: Streamlit
- **STT**: Groq Whisper API
- **LLM**: Groq LLaMA 3.3 70B
- **Audio Processing**: yt-dlp, pydub, ffmpeg

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```bash
   streamlit run main.py
   ```

## Deployment

Deploy to Streamlit Cloud:
1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Connect your repository
4. Add `GROQ_API_KEY` to secrets
5. Deploy!

## Usage

1. Upload an audio/video file or enter a URL
2. Click "Generate Notes" to transcribe
3. Use tabs to view:
   - Raw transcription
   - Study notes
   - Interactive quiz
   - Flashcards

## API Requirements

- Groq API key (free tier available)
- Get yours at: https://console.groq.com/

## License

MIT
