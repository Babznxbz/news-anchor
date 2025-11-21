# Advanced News Reading System with Interactive Q&A

import os
import re
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()

class NewsReadingSystem:
    def __init__(self, pdf_path, language='english'):
        self.pdf_path = pdf_path
        self.language = language
        self.pdf_text = ""
        self.translated_text = ""  # Store translated content
        self.sentences = []
        self.current_position = 0
        self.chunks = []
        self.model = None
        self.tts_model = None
        self.vector_store = None  # LangChain FAISS vector store
        self.embeddings = None
        self.setup()
    
    def extract_text_from_pdf(self):
        """Extract text from PDF with better formatting - remove extra line breaks"""
        print(f"📄 Reading PDF: {self.pdf_path}")
        try:
            reader = PdfReader(self.pdf_path)
            text = ""
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    # Clean the text: remove excessive line breaks and spaces
                    page_text = page_text.replace('\n', ' ').replace('\r', ' ')
                    # Remove multiple spaces
                    page_text = ' '.join(page_text.split())
                    text += page_text + " "
            
            print(f"✅ Extracted {len(text)} characters from {len(reader.pages)} pages")
            return text.strip()
        except Exception as e:
            print(f"❌ PDF extraction error: {e}")
            raise
    
    def split_into_sentences(self, text):
        """Split text into sentences for smooth news reading"""
        # Clean text first - remove extra spaces
        text = ' '.join(text.split())
        
        # Split by sentence endings (., !, ?)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter and clean sentences
        formatted_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Only keep sentences with at least 5 words (avoid fragments)
            if sentence and len(sentence.split()) >= 5:
                formatted_sentences.append(sentence)
        
        print(f"✅ Split into {len(formatted_sentences)} sentences for reading")
        return formatted_sentences
    
    def translate_text(self, text, target_language):
        """Translate text to target language using Gemini"""
        if target_language == 'english':
            return text
        
        try:
            print(f"🌐 Translating document to {target_language}...")
            
            lang_names = {
                'hindi': 'Hindi',
                'marathi': 'Marathi',
                'tamil': 'Tamil',
                'telugu': 'Telugu'
            }
            
            target_lang = lang_names.get(target_language, 'Hindi')
            
            prompt = f"""Translate the following English text to {target_lang}. 
            
Maintain the same meaning, structure, and professional tone. 
Translate naturally as it would appear in official documents in {target_lang}.

Text to translate:
{text}

Translation:"""
            
            response = self.model.generate_content(prompt)
            translated = response.text.strip()
            
            print(f"✅ Document translated to {target_language}")
            return translated
            
        except Exception as e:
            print(f"⚠️ Translation error: {e}, using original text")
            return text
    
    def chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks using LangChain for Q&A context"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        print(f"✅ Created {len(chunks)} text chunks with LangChain for Q&A")
        return chunks
    
    def format_as_news(self, text):
        """Format text for news reading"""
        # Add news introduction
        intro = "Hello! I am your news anchor. Today we have new topics to discuss from official documents. Let's begin."
        return intro, text
    
    def find_relevant_chunks(self, question, top_k=5):
        """Use LangChain FAISS vector store for semantic search with enhanced keyword fallback"""
        try:
            if self.vector_store:
                # Semantic search using FAISS - get more chunks for better context
                docs = self.vector_store.similarity_search(question, k=top_k)
                relevant_chunks = [doc.page_content for doc in docs]
                print(f"🔍 LangChain semantic search found {len(relevant_chunks)} relevant chunks")
                return relevant_chunks
            else:
                # Enhanced keyword matching fallback
                print("⚠️ Vector store not available, using enhanced keyword matching")
                question_lower = question.lower()
                question_words = set(question_lower.split())
                
                # Remove common stop words
                stop_words = {'the', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where', 'who', 'a', 'an', 'of', 'to'}
                question_words = question_words - stop_words
                
                scored_chunks = []
                
                for chunk in self.chunks:
                    chunk_lower = chunk.lower()
                    score = 0
                    
                    # Score based on word matches and partial matches
                    for word in question_words:
                        if word in chunk_lower:
                            score += 3  # Full word match
                        elif any(word in chunk_word for chunk_word in chunk_lower.split()):
                            score += 1  # Partial match
                    
                    if score > 0:
                        scored_chunks.append((score, chunk))
                
                scored_chunks.sort(reverse=True, key=lambda x: x[0])
                relevant_chunks = [chunk for _, chunk in scored_chunks[:top_k]]
                
                # If no matches found, return first few chunks as fallback
                if not relevant_chunks:
                    relevant_chunks = self.chunks[:top_k]
                    print(f"⚠️ No keyword matches, using first {top_k} chunks")
                else:
                    print(f"✅ Found {len(relevant_chunks)} relevant chunks via keyword matching")
                
                return relevant_chunks
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return self.chunks[:top_k] if self.chunks else []
    
    def setup(self):
        """Setup news reading system with Q&A using LangChain"""
        try:
            # Extract PDF text
            self.pdf_text = self.extract_text_from_pdf()
            
            # Setup Gemini with retry
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in .env file")
            
            genai.configure(api_key=api_key)
            
            # Model for Q&A and Translation
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'max_output_tokens': 200,
                }
            )
            
            # Translate content if needed
            if self.language != 'english':
                self.translated_text = self.translate_text(self.pdf_text, self.language)
                working_text = self.translated_text
            else:
                working_text = self.pdf_text
            
            # Split into sentences for reading (use translated text)
            self.sentences = self.split_into_sentences(working_text)
            
            # Create chunks for Q&A using original English text
            self.chunks = self.chunk_text(self.pdf_text)
            
            # Initialize LangChain embeddings and FAISS vector store
            try:
                print("🔍 Initializing LangChain FAISS vector store...")
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=api_key
                )
                
                # Create documents for vector store
                documents = [Document(page_content=chunk) for chunk in self.chunks]
                
                # Create FAISS vector store
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                print("✅ LangChain FAISS vector store ready for semantic search!")
            except Exception as e:
                print(f"⚠️ LangChain setup warning: {e}")
                print("⚠️ Falling back to keyword-based search")
                self.vector_store = None
            
            print("✅ News Reading System ready!")
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
            raise
    
    def get_news_intro(self, language='english'):
        """Get news introduction in selected language - Aaj Tak style (punchy, energetic)"""
        intros = {
            'english': "Welcome to news! Today's big story from official documents!",
            'hindi': "नमस्कार! आज की बड़ी खबर आधिकारिक दस्तावेजों से!",
            'marathi': "नमस्कार! आज ची मोठी बातमी अधिकृत कागदपत्रांमधून!",
            'tamil': "வணக்கம்! அதிகாரப்பூர்வ ஆவணங்களிலிருந்து இன்றைய பெரிய செய்தி!",
            'telugu': "నమస్కారం! అధికారిక పత్రాల నుండి నేటి పెద్ద వార్త!"
        }
        return intros.get(language.lower(), intros['english'])
    
    def get_next_sentence(self):
        """Get next sentence for reading"""
        if self.current_position < len(self.sentences):
            sentence = self.sentences[self.current_position]
            self.current_position += 1
            return sentence, self.current_position < len(self.sentences)
        return None, False
    
    def get_remaining_text(self):
        """Get all remaining text from current position"""
        if self.current_position < len(self.sentences):
            return ' '.join(self.sentences[self.current_position:])
        return ""
    
    def reset_position(self):
        """Reset reading position to start"""
        self.current_position = 0
    
    def get_progress(self):
        """Get reading progress percentage"""
        if len(self.sentences) > 0:
            return (self.current_position / len(self.sentences)) * 100
        return 0
    
    def ask_question(self, question):
        """Ask a question about the PDF with intelligent analysis and complete answers"""
        try:
            if not self.model or not self.chunks:
                return "System not initialized. Please check the PDF and API key."
            
            print(f"📋 Analyzing question: {question}")
            
            # Find relevant chunks with more context (top_k=5)
            relevant_chunks = self.find_relevant_chunks(question, top_k=5)
            
            if not relevant_chunks:
                return "I don't have information about that in the current document."
            
            context = "\n\n".join(relevant_chunks)
            print(f"📄 Using {len(relevant_chunks)} chunks for comprehensive analysis")
            
            # Create detailed prompt for complete answers
            prompt = f"""You are a professional news anchor answering questions based on official documents.

Official Document Content:
{context}

Viewer Question: {question}

Instructions:
1. Carefully read and analyze the document content above
2. If the answer IS in the document:
   - Provide the COMPLETE information (don't summarize if it's a list)
   - For lists, include ALL items mentioned
   - Be thorough and detailed
   - Use professional language: "According to the document..." or "The official records indicate..."
3. If the answer is NOT in the document:
   - Clearly state: "I don't have that specific information in this document."
4. Be factual, professional, and confident like a news anchor
5. Keep tone natural and conversational but authoritative

Your complete answer:"""
            
            print("🤖 Generating comprehensive answer with Gemini...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.2,  # Lower temperature for more factual, consistent answers
                    'top_p': 0.9,
                    'max_output_tokens': 800,  # More tokens for complete detailed answers
                }
            )
            
            answer = response.text.strip()
            print(f"✅ Answer generated successfully")
            return answer
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Question error: {error_msg}")
            
            # Handle quota errors specifically
            if "429" in error_msg or "quota" in error_msg.lower():
                return "I apologize, but the AI service is temporarily unavailable due to quota limits. Please wait a minute and try again."
            
            return "I apologize, but I'm experiencing technical difficulties. Please try again."

# Initialize system with configurable path
PDF_PATH = os.getenv('PDF_PATH', r"C:\Users\adity\Downloads\Bihar Voter Verification Required Documents.pdf")
news_system = None

def initialize_rag(language='english'):
    """Initialize News Reading System with error handling"""
    global news_system
    try:
        if not os.path.exists(PDF_PATH):
            print(f"❌ PDF file not found: {PDF_PATH}")
            print("   Please update the PDF_PATH in .env or check the file location")
            return False
        
        news_system = NewsReadingSystem(PDF_PATH, language=language)
        return True
    except Exception as e:
        print(f"❌ Failed to initialize News System: {e}")
        import traceback
        traceback.print_exc()
        return False

def ask_pdf_question(question):
    """Ask question about the news content"""
    global news_system
    
    if not news_system:
        print("📚 News system not initialized, initializing now...")
        if not initialize_rag():
            return "I apologize, but the system is currently unavailable. Please check the PDF file path and try again."
    
    if news_system:
        return news_system.ask_question(question)
    else:
        return "I'm unable to access the document at this time. Please ensure the PDF file is available."

def get_news_intro(language='english'):
    """Get news introduction"""
    global news_system
    if news_system:
        return news_system.get_news_intro(language)
    return "Hello! Welcome to the news."

def get_next_sentence():
    """Get next sentence for reading"""
    global news_system
    if news_system:
        return news_system.get_next_sentence()
    return None, False

def get_remaining_text():
    """Get remaining news text"""
    global news_system
    if news_system:
        return news_system.get_remaining_text()
    return ""

def reset_reading():
    """Reset to beginning"""
    global news_system
    if news_system:
        news_system.reset_position()

def get_progress():
    """Get reading progress"""
    global news_system
    if news_system:
        return news_system.get_progress()
    return 0
