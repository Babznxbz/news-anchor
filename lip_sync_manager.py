# Lip-Sync Manager for Voice-Video Synchronization

import time
import re

class LipSyncManager:
    """Manages timing between TTS voice and video lip movements"""
    
    def __init__(self):
        # Video timing (in seconds) - Updated for new video
        self.talk_video_duration = 5.0  # Duration of one loop of talk (2)-vmake.mp4
        self.listening_video_duration = 5.0  # Duration of listening.mp4
        
        # TTS timing estimates (words per minute) - News anchor style
        self.base_wpm = 140  # News anchor speaking rate (slightly slower, more clear)
        self.min_wpm = 110   # Slowest comfortable rate
        self.max_wpm = 170   # Fastest comfortable rate
    
    def estimate_speech_duration(self, text):
        """Estimate how long it will take to speak the text"""
        # Count words
        words = len(text.split())
        
        # Calculate duration at base rate (words per minute)
        duration_seconds = (words / self.base_wpm) * 60
        
        return duration_seconds
    
    def calculate_optimal_rate(self, text):
        """Calculate optimal TTS rate to match video timing"""
        words = len(text.split())
        
        # If very short response (1-5 words), use base rate
        if words <= 5:
            return self.base_wpm
        
        # Calculate how many video loops we need
        estimated_duration = self.estimate_speech_duration(text)
        num_loops = max(1, round(estimated_duration / self.talk_video_duration))
        
        # Target duration should be close to video loop timing
        target_duration = num_loops * self.talk_video_duration
        
        # Calculate required WPM to match target duration
        required_wpm = (words / target_duration) * 60
        
        # Clamp to comfortable range
        optimal_wpm = max(self.min_wpm, min(self.max_wpm, required_wpm))
        
        return int(optimal_wpm)
    
    def get_video_loops_needed(self, text):
        """Calculate how many video loops are needed for this text"""
        duration = self.estimate_speech_duration(text)
        loops = max(1, round(duration / self.talk_video_duration))
        return loops
    
    def split_text_for_natural_pauses(self, text):
        """Split text into chunks for natural pauses (matches video loops)"""
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            # If chunk is getting too long for one video loop, split it
            if len(test_chunk.split()) > 15:  # ~15 words per loop
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]

# Global instance
lip_sync_manager = LipSyncManager()
