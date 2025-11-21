# 📺 News Anchor AI - Setup Guide

## 🎯 Features
- **Professional News Anchor AI** with female voice
- **Smart Document Q&A** using RAG (Retrieval Augmented Generation)
- **Real-time Avatar Synchronization** with lip-sync
- **Web Interface** with voice and text input
- **Advanced Chunking** for better document understanding

---

## 📋 Requirements

- Python 3.8 or higher
- Microphone (for voice input)
- Chrome or Edge browser (for Web Speech API)
- Google Gemini API Key (free)

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Key

Edit the `.env` file and add your Google API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

**Get your free API key**: https://makersuite.google.com/app/apikey

### 3. Set PDF Path (Optional)

Update the PDF path in `.env`:

```env
PDF_PATH=C:\Path\To\Your\Document.pdf
```

Or it will use the default path specified in `rag_system.py`

### 4. Run the Application

```powershell
python working_voice_addo_fixed.py
```

### 5. Open Web Interface

Open your browser and go to:
```
http://localhost:5001
```

---

## 🎬 How to Use

1. **Click "Start News Broadcast"** - Avatar shows listening video
2. **Ask Your Question** - Type or speak your question
3. **Get Answer** - News anchor responds with broadcasting video
4. **Continue Conversation** - System automatically returns to listening mode

---

## 🎥 Video Files

The system uses two videos:
- `listening.mp4` - Shows when waiting for input
- `talk (2)-vmake.mp4` - Shows when broadcasting news

Both files should be in: `static/videos/`

---

## 🎙️ Voice Settings

The system automatically selects the best female voice available:
- **Priority**: Zira → Hazel → Susan → Female → Default
- **Speed**: 140 WPM (news anchor pace)
- **Style**: Professional broadcasting tone

---

## 🔧 Troubleshooting

### "Could not find PyAudio"
```powershell
pip install pyaudio
```

### "PDF file not found"
- Check the PDF_PATH in `.env`
- Ensure the file exists at that location
- Use absolute paths (e.g., `C:\Users\...`)

### "GOOGLE_API_KEY not found"
- Add your API key to `.env` file
- Make sure there are no spaces around the `=`
- Restart the application

### Avatar not syncing properly
- Clear browser cache (Ctrl+F5)
- Check that both video files exist
- Ensure videos play in your browser

### No voice output
- Check system volume
- Verify microphone permissions
- Try running as administrator

---

## 📊 Advanced Features

### Smart Document Chunking
- Splits PDF into 3000-word chunks with 500-word overlap
- Finds most relevant chunks for each question
- Uses all pages (not just first 15K characters)

### News Anchor Style
- Professional broadcasting language
- Conversational yet authoritative tone
- Short, clear responses (2-3 sentences)
- Natural presentation style

### Lip-Sync Algorithm
- Calculates optimal speech rate
- Matches video loop timing
- Smooth transitions between states

---

## 🛠️ Configuration Options

### Change Speech Rate
Edit `lip_sync_manager.py`:
```python
self.base_wpm = 140  # Adjust between 110-170
```

### Change Response Length
Edit `rag_system.py`:
```python
'max_output_tokens': 200,  # Increase for longer responses
```

### Change Video Loop Duration
Edit `lip_sync_manager.py`:
```python
self.talk_video_duration = 5.0  # Match your video length
```

---

## 📝 Project Structure

```
friday_jarvis/
├── working_voice_addo_fixed.py  # Main application
├── rag_system.py                # Document Q&A system
├── lip_sync_manager.py          # Voice-video sync
├── prompts.py                   # AI personality
├── requirements.txt             # Dependencies
├── .env                         # Configuration
├── templates/
│   └── working_addo_web.html   # Web interface
└── static/
    └── videos/
        ├── listening.mp4
        └── talk (2)-vmake.mp4
```

---

## 🎯 Usage Tips

1. **Ask Clear Questions** - Be specific about what you need
2. **Wait for Response** - Let the anchor finish speaking
3. **Use Keywords** - Include relevant terms from the document
4. **Keep Questions Brief** - System works best with focused queries

---

## 🤝 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all configuration settings
3. Ensure all files are in the correct locations
4. Try restarting the application

---

## 📄 License

This project is for educational and personal use.

---

**Enjoy your AI News Anchor! 📺🎙️**
