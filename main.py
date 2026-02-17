import streamlit as st
import os
from dotenv import load_dotenv
from utils.stt_engine import transcribe_audio
from utils.llm_engine import generate_content

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Lecture Voice-to-Notes", page_icon="🎓", layout="wide")


st.title("🎓 Lecture Voice-to-Notes Generator")
st.markdown("Transform your lecture recordings into clear notes, quizzes, and flashcards instantly.")

# Custom CSS for better UI
st.markdown("""
<style>
    /* Flashcard styling */
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        color: white;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 18px;
        transition: transform 0.3s ease;
    }
    .flashcard:hover {
        transform: translateY(-5px);
    }
    .flashcard-front {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .flashcard-back {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    /* Quiz styling */
    .quiz-question {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
    }
    .correct-answer {
        background: #d4edda;
        border-color: #28a745;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .incorrect-answer {
        background: #f8d7da;
        border-color: #dc3545;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .score-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 24px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
# Load API key from Streamlit Cloud secrets or local .env file
groq_api_key = None

# Check if secrets.toml file exists to avoid FileNotFoundError
secrets_file_paths = [
    os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml"),
    os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
]

secrets_exists = any(os.path.exists(path) for path in secrets_file_paths)

if secrets_exists:
    try:
        # Try to load from Streamlit Cloud secrets
        groq_api_key = st.secrets.get("GROQ_API_KEY", None)
    except Exception:
        # Fall back to .env file
        pass

# If not found in secrets, try .env file
if not groq_api_key:
    groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ GROQ_API_KEY not found!")
    st.info("**For local development:** Add `GROQ_API_KEY=your_key` to your `.env` file")
    st.info("**For Streamlit Cloud:** Add your API key in Settings → Secrets")
    st.stop()

# Main Area
tab_upload, tab_url = st.tabs(["📂 Upload File", "🔗 URL Input"])

with tab_upload:
    uploaded_file = st.file_uploader("Upload Lecture Audio/Video (MP3, WAV, M4A, MP4)", type=["mp3", "wav", "m4a", "mp4"])

with tab_url:
    url_input = st.text_input("Enter Lecture URL (YouTube, etc.)")
    process_url = st.button("Process URL")

if not groq_api_key:
    st.error("API key is missing. Please add GROQ_API_KEY to your .env file.")
    st.stop()

# Logic to handle processing
if uploaded_file:
    # Save uploaded file temporarily
    file_extension = os.path.splitext(uploaded_file.name)[1]
    temp_filename = f"temp_lecture{file_extension}"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.current_file_path = temp_filename

elif url_input and process_url:
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        status_text.text("⏳ Downloading Audio from URL... (This may take a moment)")
        progress_bar.progress(10)
        
        from utils.download_engine import download_audio_from_url
        temp_filename = download_audio_from_url(url_input, "temp_lecture")
        
        progress_bar.progress(100)
        status_text.text("✅ Download Complete!")
        
        if temp_filename:
            st.session_state.current_file_path = temp_filename
        else:
             st.error("Failed to download audio. Please check the URL.")
             
    except Exception as e:
        st.error(f"❌ Error during download: {e}")
        progress_bar.empty()
        status_text.empty()

# Display Audio and Transcription Button
if 'current_file_path' in st.session_state and os.path.exists(st.session_state.current_file_path):
    st.audio(st.session_state.current_file_path)
    
    if st.button("Generate Notes", key="generate_btn"):
        progress_text = "Transcribing Audio... (Powered by Groq 🚀)"
        my_bar = st.progress(0, text=progress_text)

        try:
            my_bar.progress(20, text="Sending audio to Groq...")
            transcription = transcribe_audio(st.session_state.current_file_path, groq_api_key)
            
            my_bar.progress(80, text="Processing transcription...")
            st.session_state.transcription = transcription
            
            my_bar.progress(100, text="✅ Transcription Complete!")
            st.success("Transcription Complete!")
            my_bar.empty()
            
        except Exception as e:
            my_bar.empty()
            st.error(f"Transcription Failed: {e}")

# Display Results if transcription exists in session state
if 'transcription' in st.session_state:
    st.divider()
    
    # Create tabs for different outputs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Transcription", "📚 Study Notes", "❓ Quiz", "🃏 Flashcards"])
    
    with tab1:
        st.subheader("📝 Transcription")
        
        # Format transcription for better readability
        transcription_text = st.session_state.transcription
        
        # Add paragraph breaks for better readability (split long text into paragraphs)
        sentences = transcription_text.split('. ')
        formatted_paragraphs = []
        temp_paragraph = []
        
        for i, sentence in enumerate(sentences):
            temp_paragraph.append(sentence.strip())
            # Create a new paragraph every 5 sentences for readability
            if (i + 1) % 5 == 0 or i == len(sentences) - 1:
                formatted_paragraphs.append('. '.join(temp_paragraph) + '.')
                temp_paragraph = []
        
        formatted_transcription = '\n\n'.join(formatted_paragraphs)
        
        # Display in a scrollable container with styling
        st.markdown("""
        <style>
        .transcription-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            font-size: 16px;
            line-height: 1.8;
            color: #212529;
            white-space: pre-wrap;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .transcription-box::-webkit-scrollbar {
            width: 8px;
        }
        .transcription-box::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        .transcription-box::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }
        .transcription-box::-webkit-scrollbar-thumb:hover {
            background: #5568d3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display transcription in the styled scrollable box
        st.markdown(f'<div class="transcription-box">{formatted_transcription}</div>', unsafe_allow_html=True)
        
        st.markdown("")
        st.download_button("📥 Download Transcript", st.session_state.transcription, file_name="transcript.txt", key="download_transcript")

    with tab2:
        st.subheader("📚 Study Notes")
        if st.button("Generate/Refresh Notes", key="generate_notes_button"):
            with st.spinner("Generating Notes... (Powered by Groq ✨)"):
                try:
                    notes = generate_content(st.session_state.transcription, 'summary', groq_api_key)
                    st.session_state.notes = notes
                    st.success("Notes generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate notes: {e}")
        
        if 'notes' in st.session_state:
            # Display notes in a scrollable container matching transcription style
            st.markdown("""
            <style>
            .notes-box {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-left: 4px solid #667eea;
                border-radius: 8px;
                padding: 20px;
                max-height: 600px;
                overflow-y: auto;
                font-size: 16px;
                line-height: 1.8;
                color: #212529;
            }
            .notes-box::-webkit-scrollbar {
                width: 8px;
            }
            .notes-box::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 4px;
            }
            .notes-box::-webkit-scrollbar-thumb {
                background: #667eea;
                border-radius: 4px;
            }
            .notes-box::-webkit-scrollbar-thumb:hover {
                background: #5568d3;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Convert markdown to HTML for proper rendering in div
            notes_html = st.session_state.notes.replace('\n', '<br>')
            st.markdown(f'<div class="notes-box">{notes_html}</div>', unsafe_allow_html=True)
            
            st.markdown("")
            st.download_button("📥 Download Notes", st.session_state.notes, file_name="notes.md", key="download_notes")

    with tab3:
        st.subheader("❓ Interactive Quiz")
        if st.button("Generate/Refresh Quiz", key="generate_quiz_button"):
            with st.spinner("Generating Quiz..."):
                try:
                    quiz_json = generate_content(st.session_state.transcription, 'quiz', groq_api_key)
                    import json
                    # Try to parse JSON, handle potential markdown wrapping
                    quiz_json_clean = quiz_json.strip()
                    if quiz_json_clean.startswith("```"):
                        # Remove markdown code blocks
                        lines = quiz_json_clean.split('\n')
                        quiz_json_clean = '\n'.join([l for l in lines if not l.startswith('```')])
                    
                    quiz_data = json.loads(quiz_json_clean)
                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success("Quiz generated successfully!")
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse quiz data. Please try regenerating. Error: {e}")
                except Exception as e:
                    st.error(f"Failed to generate quiz: {e}")
        
        if 'quiz_data' in st.session_state:
            quiz_data = st.session_state.quiz_data
            
            if not st.session_state.get('quiz_submitted', False):
                # Display quiz questions
                st.markdown("### Answer the following questions:")
                for i, q in enumerate(quiz_data['questions']):
                    # Display question without HTML to avoid rendering issues
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    
                    # Initialize answer in session state if not present
                    if i not in st.session_state.quiz_answers:
                        st.session_state.quiz_answers[i] = None
                    
                    answer = st.radio(
                        f"Select your answer for question {i+1}:",
                        options=q['options'],
                        key=f"quiz_q_{i}",
                        index=None if st.session_state.quiz_answers.get(i) is None else q['options'].index(st.session_state.quiz_answers[i])
                    )
                    
                    if answer is not None:
                        st.session_state.quiz_answers[i] = answer
                    st.markdown("---")
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Submit Quiz", type="primary"):
                        st.session_state.quiz_submitted = True
                        st.rerun()
            else:
                # Show results
                st.markdown("### 📊 Quiz Results")
                correct_count = 0
                total_questions = len(quiz_data['questions'])
                
                for i, q in enumerate(quiz_data['questions']):
                    user_answer = st.session_state.quiz_answers.get(i, None)
                    correct_answer = q['options'][q['correct']]
                    is_correct = user_answer == correct_answer if user_answer is not None else False
                    
                    if is_correct:
                        correct_count += 1
                    
                    # Display question clearly
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    st.markdown("")  # Add spacing
                    
                    for option in q['options']:
                        if option == correct_answer:
                            st.markdown(f"<div class='correct-answer'>✅ {option} (Correct Answer)</div>", unsafe_allow_html=True)
                        elif option == user_answer and not is_correct:
                            st.markdown(f"<div class='incorrect-answer'>❌ {option} (Your Answer)</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='padding: 5px;'>{option}</div>", unsafe_allow_html=True)
                    st.markdown("---")
                
                # Display score
                percentage = (correct_count / total_questions) * 100
                st.markdown(f"""
                <div class='score-display'>
                    <h2>🎯 Your Score: {correct_count}/{total_questions}</h2>
                    <h3>{percentage:.1f}%</h3>
                    <p>{"🎉 Excellent!" if percentage >= 80 else "👍 Good job!" if percentage >= 60 else "📚 Keep studying!"}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Retake Quiz", key="retake_quiz_button"):
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                    st.rerun()

    with tab4:
        st.subheader("🃏 Flashcards")
        if st.button("Generate/Refresh Flashcards", key="generate_flashcards_button"):
            with st.spinner("Generating Flashcards..."):
                try:
                    flashcards_json = generate_content(st.session_state.transcription, 'flashcards', groq_api_key)
                    import json
                    # Try to parse JSON, handle potential markdown wrapping
                    flashcards_json_clean = flashcards_json.strip()
                    if flashcards_json_clean.startswith("```"):
                        # Remove markdown code blocks
                        lines = flashcards_json_clean.split('\n')
                        flashcards_json_clean = '\n'.join([l for l in lines if not l.startswith('```')])
                    
                    flashcards_data = json.loads(flashcards_json_clean)
                    st.session_state.flashcards_data = flashcards_data
                    st.session_state.current_card = 0
                    st.session_state.show_back = False
                    st.success("Flashcards generated successfully!")
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse flashcard data. Please try regenerating. Error: {e}")
                except Exception as e:
                    st.error(f"Failed to generate flashcards: {e}")
        
        if 'flashcards_data' in st.session_state:
            flashcards = st.session_state.flashcards_data['flashcards']
            current_idx = st.session_state.get('current_card', 0)
            show_back = st.session_state.get('show_back', False)
            
            # Progress indicator
            st.markdown(f"**Card {current_idx + 1} of {len(flashcards)}**")
            st.progress((current_idx + 1) / len(flashcards))
            
            # Display card
            card = flashcards[current_idx]
            if not show_back:
                # Show front
                st.markdown(f"""
                <div class='flashcard flashcard-front'>
                    <div>
                        <h3>Front</h3>
                        <p style='font-size: 22px; margin-top: 20px;'>{card['front']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show back
                st.markdown(f"""
                <div class='flashcard flashcard-back'>
                    <div>
                        <h3>Back</h3>
                        <p style='font-size: 20px; margin-top: 20px;'>{card['back']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Navigation buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("⬅️ Previous", disabled=(current_idx == 0)):
                    st.session_state.current_card = max(0, current_idx - 1)
                    st.session_state.show_back = False
                    st.rerun()
            
            with col2:
                if st.button("🔄 Flip Card"):
                    st.session_state.show_back = not show_back
                    st.rerun()
            
            with col3:
                if st.button("Reset Progress"):
                    st.session_state.current_card = 0
                    st.session_state.show_back = False
                    st.rerun()
            
            with col4:
                if st.button("Next ➡️", disabled=(current_idx == len(flashcards) - 1)):
                    st.session_state.current_card = min(len(flashcards) - 1, current_idx + 1)
                    st.session_state.show_back = False
                    st.rerun()

elif not uploaded_file:
    st.info("Please upload an audio file to get started.")
elif not (groq_api_key and gemini_api_key):
    st.warning("Please enter your API keys in the sidebar.")
