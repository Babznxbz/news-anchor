#!/usr/bin/env python3
"""
NEWS READING SYSTEM - Continuous News Broadcasting with Interactive Q&A
Reads PDF as news broadcast, pauses for questions, resumes from exact position
Multi-language support: English, Hindi, Marathi
"""

import speech_recognition as sr
import os
from dotenv import load_dotenv
import google.generativeai as genai
import tempfile
import io
from prompts import AGENT_INSTRUCTION
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time
from rag_system import (
    initialize_rag, ask_pdf_question, get_news_intro, 
    get_next_sentence, get_remaining_text, reset_reading, get_progress, NewsReadingSystem
)
from lip_sync_manager import lip_sync_manager
import logging

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Web server setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'news-reading-system'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
current_language = 'english'
is_reading_news = False
is_paused_for_question = False
last_read_position = ""

class NewsAnchorAI:
    def __init__(self):
        print("📺 News Anchor AI starting...")
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone(device_index=0)
        except Exception as e:
            logging.warning(f"Default microphone not available, using system default: {e}")
            self.microphone = sr.Microphone()
        
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # AI
        self.setup_ai()
        
        # Edge TTS voices
        self.setup_edge_voices()
        
        print("✅ News Anchor AI ready!")
        
    def setup_ai(self):
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logging.error("GOOGLE_API_KEY not found in .env file")
                self.model = None
                print("⚠️ No AI - Please add GOOGLE_API_KEY to .env file")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'max_output_tokens': 200,
                }
            )
            print("✅ AI ready (Gemini 2.0 Flash)")
        except Exception as e:
            logging.error(f"AI setup error: {e}")
            self.model = None
            print(f"⚠️ AI error: {e}")
    
    def setup_edge_voices(self):
        """Initialize Edge TTS voices for all Indian languages - Energetic & Dynamic"""
        try:
            # Voice mapping for Edge TTS (Microsoft)
            # Using Indian female voices with natural, energetic delivery
            self.edge_voices = {
                'english': 'en-IN-NeerjaNeural',  # Indian English Female
                'hindi': 'hi-IN-SwaraNeural',     # Hindi Female  
                'marathi': 'mr-IN-AarohiNeural',  # Marathi Female
                'tamil': 'ta-IN-PallaviNeural',   # Tamil Female
                'telugu': 'te-IN-ShrutiNeural'    # Telugu Female
            }
            print("✅ Edge TTS voices configured (Energetic & Dynamic)")
            print("   🇮🇳 English: Neerja")
            print("   🇮🇳 Hindi: Swara")
            print("   🇮🇳 Marathi: Aarohi")
            print("   🇮🇳 Tamil: Pallavi")
            print("   🇮🇳 Telugu: Shruti")
                
        except Exception as e:
            logging.error(f"Edge TTS setup error: {e}")
            self.edge_voices = None
            print(f"⚠️ Edge TTS error: {e}")
    
    def speak(self, text, check_cancelled=None, language='english', session_id=None):
        """NEWS READING SPEECH - Professional News Anchor with Edge TTS (Natural Indian Female Voice)"""
        print(f"🗣️ Broadcasting: {text[:100]}...")
        
        try:
            # Check if cancelled before starting
            if check_cancelled and check_cancelled():
                logging.info("Speech cancelled before starting")
                return False
            
            if not self.edge_voices:
                logging.error("Edge TTS not configured")
                return False
            
            # Select voice based on language
            voice_name = self.edge_voices.get(language.lower(), self.edge_voices['english'])
            
            print(f"🎙️ Using Edge TTS: {voice_name}")
            
            # Use Edge TTS with direct import
            try:
                import pygame
                from pydub import AudioSegment
                import edge_tts
                import asyncio
                
                # Create temp MP3 file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    temp_file = fp.name
                
                # Generate speech with Edge TTS
                # Energetic & animated with dynamic variations in pitch and tone
                print(f"🔊 Generating energetic speech with {voice_name}...")
                
                # Run edge-tts async generation with prosody settings
                # - Fast rate for exciting moments (+15%)
                # - Higher pitch for enthusiasm (+5Hz)
                # - Stronger volume for presence (+10%)
                async def generate_speech():
                    communicate = edge_tts.Communicate(
                        text, 
                        voice_name,
                        rate='+15%',
                        pitch='+5Hz',
                        volume='+10%'
                    )
                    await communicate.save(temp_file)
                
                # Execute async function
                asyncio.run(generate_speech())
                
                # Load audio and apply processing
                audio = AudioSegment.from_mp3(temp_file)
                
                # Boost volume for stronger presence (+3dB)
                audio = audio + 3
                
                # Apply gentle bass boost for deeper voice
                audio = audio.low_pass_filter(3000).high_pass_filter(100)
                
                # Save processed audio
                processed_file = temp_file.replace('.mp3', '_processed.mp3')
                audio.export(processed_file, format="mp3", bitrate="128k")
                
                # Clean up original file
                os.remove(temp_file)
                temp_file = processed_file
                
                # Check cancellation
                if check_cancelled and check_cancelled():
                    print("🛑 Speech cancelled before playback")
                    os.remove(temp_file)
                    return False
                
                # Initialize pygame mixer
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=512)
                
                # Load and play audio
                pygame.mixer.music.load(temp_file)
                
                # Signal frontend to start talk video RIGHT NOW
                if session_id:
                    socketio.emit('speech_started', {}, room=session_id)
                
                # Play immediately with no delay
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    if check_cancelled and check_cancelled():
                        print("🛑 Speech cancelled during playback")
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                        return False
                    time.sleep(0.05)  # Reduced delay for better responsiveness
                
                # Signal frontend to switch to LISTENING VIDEO immediately
                if session_id:
                    socketio.emit('speech_ended', {}, room=session_id)
                
                # Unload music to free resources
                pygame.mixer.music.unload()
                
                # Clean up
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                print("✅ Speech completed")
                return True
                
            except ImportError as e:
                print(f"⚠️ TTS library error: {e}")
                return False
            
        except Exception as e:
            print(f"❌ TTS error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def listen(self):
        """Listen for user speech"""
        try:
            print("🎤 Listening...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
            
            print("🔄 Processing...")
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("🔇 Didn't understand")
            return None
        except Exception as e:
            print(f"❌ Listen error: {e}")
            return None
    
    def get_response(self, user_input):
        """Get AI response using RAG from PDF - News Anchor Style"""
        if not user_input:
            return "I didn't catch that. Could you please repeat your question?"
        
        user_lower = user_input.lower()
        
        # Handle greetings with news anchor personality
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return "Good evening! Welcome to the news desk. I'm here to help you with information from official documents. What would you like to know today?"
        
        if any(word in user_lower for word in ['thank', 'thanks']):
            return "You're very welcome! I'm here if you need any more information. Have a great day!"
        
        if any(word in user_lower for word in ['bye', 'goodbye', 'see you']):
            return "Thank you for tuning in! Stay informed and have a wonderful day ahead!"
        
        # Use RAG system to answer from PDF
        try:
            print(f"🔍 Researching document for: {user_input}")
            answer = ask_pdf_question(user_input)
            return answer
        except Exception as e:
            logging.error(f"RAG error: {e}")
            return "I'm experiencing technical difficulties accessing the document at the moment. Please try again in a moment."
    
    def run(self):
        """Main conversation loop"""
        print("\n📺 NEWS ANCHOR AI - LIVE")
        print("="*40)
        print("Say 'stop' to quit")
        
        # Initial greeting with news anchor style
        self.speak("Good evening! Welcome to the news desk. I'm here to help you with information from official documents. What would you like to know today?")
        
        # Calibrate microphone
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"✅ Threshold: {self.recognizer.energy_threshold}")
        
        # Main conversation loop
        while True:
            try:
                # Listen for user input
                user_input = self.listen()
                
                if user_input:
                    # Check for exit command
                    if any(word in user_input.lower() for word in ['stop', 'quit', 'exit', 'goodbye']):
                        self.speak("Goodbye, Sir. It was a pleasure serving you.")
                        break
                    
                    # Get and speak response
                    response = self.get_response(user_input)
                    self.speak(response)
                
            except KeyboardInterrupt:
                self.speak("Goodbye, Sir.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

# Global News Anchor instance
news_anchor = None

@app.route('/')
def index():
    return render_template('news_reading.html')

@app.route('/test')
def test():
    return render_template('test.html')

@socketio.on('connect')
def handle_connect():
    print(f'🌐 Client connected: {request.sid}')
    emit('connected', {'status': 'ready'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'🌐 Client disconnected: {request.sid}')

@socketio.on('set_language')
def handle_set_language(data):
    """Set reading language and reload document with translation"""
    global current_language
    from rag_system import news_system, initialize_rag
    
    new_language = data.get('language', 'english')
    
    if new_language != current_language:
        current_language = new_language
        print(f'🌍 Language changed to: {current_language}')
        
        # Reinitialize RAG system with new language
        try:
            print(f'📚 Reloading document for {current_language}...')
            if initialize_rag(language=current_language):
                print(f'✅ Document ready in {current_language}')
                emit('language_set', {'language': current_language, 'status': 'ready'})
            else:
                print(f'❌ Failed to load document')
                emit('language_set', {'language': current_language, 'status': 'error'})
        except Exception as e:
            print(f'❌ Failed to reload document: {e}')
            import traceback
            traceback.print_exc()
            emit('language_set', {'language': current_language, 'status': 'error'})
    else:
        emit('language_set', {'language': current_language, 'status': 'ready'})

@socketio.on('start_reading')
def handle_start_reading():
    """Start reading news from beginning"""
    global is_reading_news, is_paused_for_question, speech_cancelled
    
    is_reading_news = True
    is_paused_for_question = False
    speech_cancelled = False
    reset_reading()
    
    session_id = request.sid
    print(f'📰 Starting news broadcast for {session_id}')
    
    def read_news_continuously():
        global is_reading_news, is_paused_for_question, speech_cancelled
        
        # Send intro
        intro = get_news_intro(current_language)
        socketio.emit('news_intro', {'message': intro}, room=session_id)
        
        if news_anchor and not speech_cancelled:
            news_anchor.speak(intro, check_cancelled=lambda: speech_cancelled, language=current_language, session_id=session_id)
        
        # Read news continuously
        while is_reading_news:
            # Wait while paused for question
            if is_paused_for_question or speech_cancelled:
                print(f'⏸️ Loop paused - is_paused: {is_paused_for_question}, cancelled: {speech_cancelled}')
                time.sleep(0.1)  # Very short check for instant resume
                continue
            
            sentence, has_more = get_next_sentence()
            
            if sentence:
                # Send sentence to frontend
                socketio.emit('news_sentence', {
                    'sentence': sentence,
                    'has_more': has_more,
                    'progress': get_progress()
                }, room=session_id)
                
                # Speak sentence immediately
                if news_anchor and not speech_cancelled:
                    news_anchor.speak(sentence, check_cancelled=lambda: speech_cancelled or is_paused_for_question, language=current_language, session_id=session_id)
                
                # Check if paused during speech
                if is_paused_for_question or speech_cancelled:
                    print('⏸️ Paused during speech, waiting...')
                    continue
            
            if not has_more:
                # News finished
                socketio.emit('news_completed', {}, room=session_id)
                is_reading_news = False
                break
        
        print('✅ News reading completed or stopped')
    
    threading.Thread(target=read_news_continuously, daemon=True).start()
    emit('reading_started', {'status': 'broadcasting'})

@socketio.on('ask_question')
def handle_ask_question():
    """Pause news and enable question mode"""
    global is_paused_for_question, speech_cancelled
    
    is_paused_for_question = True
    speech_cancelled = True  # Stop current speech
    
    print('⏸️ News paused for question')
    emit('question_mode_enabled', {'status': 'paused'})

@socketio.on('user_question')
def handle_user_question(data):
    """Handle user question during news reading"""
    global is_paused_for_question, speech_cancelled
    
    question = data.get('question', '').strip()
    session_id = request.sid
    
    if not question:
        return
    
    print(f'❓ User question: {question}')
    
    # Get answer from document
    answer = ask_pdf_question(question)
    print(f'💬 Answer: {answer}')
    
    # Send answer to frontend
    socketio.emit('question_answer', {'question': question, 'answer': answer}, room=session_id)
    
    # Speak answer with news anchor style
    if news_anchor:
        speech_cancelled = False
        news_anchor.speak(answer, check_cancelled=lambda: speech_cancelled, language=current_language, session_id=session_id)
    
    # Always ask if user wants to continue
    continue_prompts = {
        'english': 'Can we continue with the news?',
        'hindi': 'क्या हम समाचार जारी रखें?',
        'marathi': 'आम्ही बातम्या सुरू ठेवू का?'
    }
    
    prompt = continue_prompts.get(current_language, continue_prompts['english'])
    socketio.emit('ask_continue', {'message': prompt}, room=session_id)
    
    if news_anchor:
        news_anchor.speak(prompt, check_cancelled=lambda: speech_cancelled, language=current_language, session_id=session_id)

@socketio.on('continue_reading')
def handle_continue_reading(data):
    """Resume news reading after question"""
    global is_paused_for_question, speech_cancelled, is_reading_news
    
    user_response = data.get('response', '').lower()
    
    print(f'▶️ Continue reading request received: {user_response}')
    
    # Clear all pause flags to resume reading
    is_paused_for_question = False
    speech_cancelled = False
    is_reading_news = True  # Ensure reading is still active
    
    print(f'✅ Flags reset - is_paused: {is_paused_for_question}, cancelled: {speech_cancelled}, reading: {is_reading_news}')
    print('▶️ News should resume now...')
    
    emit('reading_resumed', {'status': 'continuing'}, broadcast=False)
    emit('reading_started', {'status': 'broadcasting'}, broadcast=False)  # Re-activate reading UI state

@socketio.on('stop_reading')
def handle_stop_reading():
    """Stop news reading completely"""
    global is_reading_news, speech_cancelled
    
    is_reading_news = False
    speech_cancelled = True
    
    # Stop and cleanup pygame to allow restart
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    except:
        pass
    
    print('🛑 News reading stopped')
    emit('reading_stopped', {'status': 'stopped'})

# Global flag to cancel speech
speech_cancelled = False

@socketio.on('cancel_session')
def handle_cancel_session():
    """Handle session cancellation"""
    global speech_cancelled, is_reading_news
    speech_cancelled = True
    is_reading_news = False
    print('🛑 Session cancelled')

def run_web_server():
    """Run the web server"""
    print("🌐 Starting web server on http://localhost:5001")
    socketio.run(app, debug=False, host='0.0.0.0', port=5001)

def main():
    print("📰 NEWS READING SYSTEM")
    print("="*60)
    print("🎙️ Continuous News Broadcasting with Interactive Q&A")
    print("🌍 Multi-language Support: English, Hindi, Marathi, Tamil, Telugu")
    print("🎭 Voice Style: Energetic, Animated, Dynamic")
    print("🌐 Web Interface: http://localhost:5001")
    print("="*60)
    print()
    
    global news_anchor
    
    try:
        # Initialize News Reading System
        print("📚 Initializing News Reading System...")
        if initialize_rag():
            print("✅ News system ready with sentence-by-sentence reading!")
        else:
            print("⚠️ News system initialization failed")
            print("   Please check:")
            print("   1. PDF file exists at the specified path")
            print("   2. GOOGLE_API_KEY is set in .env file")
            return
        
        # Initialize News Anchor AI
        print()
        news_anchor = NewsAnchorAI()
        
        print()
        print("✅ Edge TTS ready! (Energetic & Dynamic Female Voices)")
        print("   🇮🇳 English: Neerja | Hindi: Swara | Marathi: Aarohi")
        print("   🇮🇳 Tamil: Pallavi | Telugu: Shruti")
        print("   🎭 Voice Style: Energetic, Animated, Thrilling")
        print("🎬 Talk video plays during speech, listening video when stopped")
        print()
        print("="*60)
        print("🚀 NEWS READING SYSTEM ACTIVE")
        print("="*60)
        print("📍 Open browser: http://localhost:5001")
        print("🌍 Select language: English/Hindi/Marathi/Tamil/Telugu")
        print("📰 Click 'Start Reading News' to begin")
        print("⏸️ Click 'Ask Question' button to pause and ask")
        print("🛑 Click 'Stop' button to end session")
        print("🎙️ Using Edge TTS (Energetic, Dynamic Indian Voices)")
        print()
        
        # Run web server
        run_web_server()
        
    except Exception as e:
        logging.error(f"System error: {e}")
        print(f"❌ Error: {e}")
        print("\nPlease check:")
        print("1. .env file exists with GOOGLE_API_KEY")
        print("2. PDF file path is correct")
        print("3. All dependencies are installed")

if __name__ == "__main__":
    main()
