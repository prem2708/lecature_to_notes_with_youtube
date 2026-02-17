from groq import Groq

def generate_content(text, prompt_type, api_key):
    """
    Generates content (notes, quiz, flashcards) using Groq API.
    
    Args:
        text (str): Input text (transcribed lecture).
        prompt_type (str): Type of content to generate ('summary', 'quiz', 'flashcards').
        api_key (str): Groq API Key.
        
    Returns:
        str: Generated content.
    """
    if not api_key:
        raise ValueError("Groq API Key is missing.")

    try:
        client = Groq(api_key=api_key)
        # Using llama-3.3-70b-versatile for high-quality content generation
        model_id = 'llama-3.3-70b-versatile'

        prompts = {
            'summary': f"""
                You are an expert academic assistant. Your goal is to create a highly structured and comprehensive study guide from the following lecture transcript.
                
                Strictly follow this format:
                # 🎓 Lecture Summary
                [A concise, high-level summary of the entire lecture (150-200 words)]
                
                ## 🔑 Key Concepts & Definitions
                - **[Concept 1]**: [Clear and precise definition]
                - **[Concept 2]**: [Clear and precise definition]
                ...
                
                ## 📝 Detailed Notes
                [Organize the content into logical sections with headings. Use bullet points for readability.]
                - [Point 1]
                - [Point 2]
                
                ## 🧠 Key Takeaways
                [Bullet list of the most important things to remember]
                
                Transcript:
                {text}
            """,
            'quiz': f"""
                Create a 10-question multiple-choice quiz based on the lecture transcript.
                
                IMPORTANT: You MUST respond with ONLY valid JSON in this exact format (no markdown, no code blocks):
                {{
                  "questions": [
                    {{
                      "question": "Question text here?",
                      "options": ["Option A", "Option B", "Option C", "Option D"],
                      "correct": 0
                    }}
                  ]
                }}
                
                Rules:
                - "correct" is the index (0-3) of the correct option
                - Focus on key concepts, not trivial details
                - Make options clear and distinct
                - Ensure exactly 10 questions
                
                Transcript:
                {text}
            """,
            'flashcards': f"""
                Create 10 high-quality flashcards from the lecture transcript.
                
                IMPORTANT: You MUST respond with ONLY valid JSON in this exact format (no markdown, no code blocks):
                {{
                  "flashcards": [
                    {{
                      "front": "Concept or question here",
                      "back": "Definition or answer here"
                    }}
                  ]
                }}
                
                Rules:
                - Focus on key terms, definitions, and important concepts
                - Keep front concise (concept/term/question)
                - Make back comprehensive but clear
                - Ensure exactly 10 flashcards
                
                Transcript:
                {text}
            """
        }

        if prompt_type not in prompts:
            return "Invalid prompt type."

        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are an expert academic assistant."},
                {"role": "user", "content": prompts[prompt_type]}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {str(e)}"
