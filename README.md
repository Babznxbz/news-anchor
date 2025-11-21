# AI News Anchor - Multi-language News Reading System 🎙️

An intelligent AI-powered news reading system with interactive Q&A capabilities, supporting 5 Indian languages with energetic female voice anchors and synchronized video avatars.

## ✨ Features

### 🎯 Core Capabilities
- **Multi-language Support**: English, Hindi, Marathi, Tamil, Telugu
- **Energetic Voice Synthesis**: Edge TTS with dynamic Indian female voices
- **Interactive Q&A**: Ask questions during news reading with RAG-powered answers
- **Video Avatar Sync**: Animated talking avatar synchronized with speech
- **Document Translation**: Automatic translation using Google Gemini AI
- **Continuous Reading**: Sentence-by-sentence broadcasting with pause/resume

### 🎙️ Voice Configuration
| Language | Voice Name | Characteristics |
|----------|-----------|-----------------|
| English 🇮🇳 | Neerja | Energetic, Professional |
| Hindi 🇮🇳 | Swara | Dynamic, Clear |
| Marathi 🇮🇳 | Aarohi | Animated, Expressive |
| Tamil 🇮🇳 | Pallavi | Thrilling, Engaging |
| Telugu 🇮🇳 | Shruti | Vibrant, Enthusiastic |

**Voice Style**: Rate +15%, Pitch +5Hz, Volume +10% for energetic delivery

### 🤖 AI Technologies
- **LLM**: Google Gemini 2.0 Flash (Q&A and Translation)
- **TTS**: Microsoft Edge TTS (Indian Neural Voices)
- **Vector Store**: FAISS with LangChain (Semantic Search)
- **Embeddings**: Google Generative AI Embeddings
- **Fallback**: Enhanced keyword-based search

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.13.7 recommended)
- Google API Key (Gemini)
- PDF document to read

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/ai-news-anchor.git
cd ai-news-anchor
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
Create a `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
PDF_PATH=C:\path\to\your\document.pdf
```

5. **Run the application**
```bash
python working_voice_addo_fixed.py
```

6. **Open in browser**
```
http://localhost:5001
```

## 📋 Usage

### Starting News Reading
1. Open `http://localhost:5001` in your browser
2. Select your preferred language from the dropdown
3. Click **"Start Reading News"**
4. Listen to the intro, followed by document content

### Interactive Q&A
1. While news is playing, click **"Ask Question"**
2. News pauses automatically
3. Type your question and press Enter
4. AI analyzes the document and responds
5. Choose to continue or stop

### Controls
- **Start Reading**: Begin news broadcast
- **Ask Question**: Pause and ask about document
- **Stop**: End current session
- **Language Selector**: Switch between 5 languages

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (HTML/JS)                │
│  - Video Avatar (Talk/Listen)               │
│  - Language Selector                        │
│  - Control Buttons                          │
└──────────────┬──────────────────────────────┘
               │ Socket.IO
┌──────────────▼──────────────────────────────┐
│         Flask Backend                       │
│  - working_voice_addo_fixed.py              │
│  - Event Handlers                           │
│  - Session Management                       │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴─────────┬──────────────┐
    │                    │              │
┌───▼────────┐  ┌────────▼─────┐  ┌────▼──────┐
│ RAG System │  │ NewsAnchorAI │  │ Edge TTS  │
│ (LangChain)│  │  (Gemini)    │  │ (Voices)  │
│  - FAISS   │  │  - Q&A       │  │  - Speech │
│  - Chunks  │  │  - Translate │  │  - Prosody│
└────────────┘  └──────────────┘  └───────────┘
```

## 📁 Project Structure

```
ai-news-anchor/
├── working_voice_addo_fixed.py   # Main Flask server & speech engine
├── rag_system.py                 # RAG system with Q&A
├── lip_sync_manager.py           # Video synchronization
├── prompts.py                    # AI prompts
├── requirements.txt              # Dependencies
├── .env                          # Configuration (not in repo)
├── templates/
│   ├── addo_voice_avatar.html   # Main UI
│   └── working_addo_web.html    # Alternative UI
├── static/
│   └── videos/
│       ├── listening.mp4        # Idle avatar
│       └── talk (2)-vmake.mp4   # Talking avatar
├── temp_audio/                  # Generated speech files
└── chroma_db/                   # Vector database
```

## 🔧 Configuration

### Voice Settings
Edit `working_voice_addo_fixed.py`:
```python
# In NewsAnchorAI.setup_edge_voices()
self.edge_voices = {
    'english': 'en-IN-NeerjaNeural',
    'hindi': 'hi-IN-SwaraNeural',
    # ... modify voices here
}
```

### Prosody Settings
Adjust in `working_voice_addo_fixed.py`:
```python
communicate = edge_tts.Communicate(
    text, voice_name,
    rate='+15%',    # Speech speed
    pitch='+5Hz',   # Voice pitch
    volume='+10%'   # Volume level
)
```

### PDF Document
Update in `.env`:
```env
PDF_PATH=C:\path\to\your\document.pdf
```

## 🎬 Video Avatar

The system uses two video loops:
- **listening.mp4**: Plays when idle/listening
- **talk (2)-vmake.mp4**: Plays during speech (4-second loop)

Replace these files in `static/videos/` for custom avatars.

## 🐛 Troubleshooting

### Edge TTS Import Error
```bash
pip install --upgrade edge-tts
```

### Gemini Quota Exceeded
- Wait for quota reset (typically 1 minute)
- System automatically falls back to keyword search for Q&A

### No Audio Output
- Ensure pygame mixer is initialized
- Check system audio settings
- Verify Edge TTS is installed correctly

### PDF Not Loading
- Check `PDF_PATH` in `.env`
- Ensure PDF file exists and is readable
- Verify PyPDF2 is installed

## 📦 Dependencies

Major packages:
- **Flask** + **Flask-SocketIO**: Web server and real-time communication
- **edge-tts**: Microsoft Edge Text-to-Speech
- **pygame**: Audio playback
- **pydub**: Audio processing
- **google-generativeai**: Gemini AI for Q&A and translation
- **langchain**: RAG framework
- **faiss-cpu**: Vector similarity search
- **PyPDF2**: PDF text extraction

See `requirements.txt` for complete list.

## 🌟 Advanced Features

### Custom Intros
Edit `rag_system.py`:
```python
def get_news_intro(self, language='english'):
    intros = {
        'english': "Your custom intro here!",
        # ... add more
    }
```

### Chunking Configuration
Adjust in `rag_system.py`:
```python
def chunk_text(self, text, chunk_size=1000, overlap=200):
    # Modify chunk_size and overlap
```

## 📝 API Reference

### Socket.IO Events

#### Client → Server
- `start_reading`: Start news broadcast
- `stop_reading`: Stop current session
- `ask_question`: Pause for question
- `user_question`: Submit question text
- `continue_reading`: Resume after Q&A
- `set_language`: Change reading language

#### Server → Client
- `reading_started`: Broadcast began
- `news_intro`: Intro message
- `news_sentence`: New sentence to display
- `speech_started`: Avatar should talk
- `speech_ended`: Avatar should listen
- `question_answer`: Q&A response
- `news_completed`: Reading finished

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Microsoft Edge TTS for Indian neural voices
- Google Gemini for AI capabilities
- LangChain for RAG framework
- FAISS for vector search

## 📧 Contact

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for multilingual news broadcasting**

