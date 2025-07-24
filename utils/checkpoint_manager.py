import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages story checkpoints and tracks progress through the writing process."""
    
    def __init__(self, words_per_page: int = 275):
        self.words_per_page = words_per_page
        self.checkpoints = {
            "outline_approval": False,
            "page_1_review": False,
            "page_2_review": False,
            "final_approval": False
        }
        self.page_count = 0.0
        self.word_count = 0
        self.last_checkpoint = None
        self.checkpoint_history = []
        
    def count_words(self, text: str) -> int:
        """Count words in the given text."""
        # Simple word counting - split by whitespace
        words = text.split()
        return len(words)
    
    def update_page_count(self, output_file_path: str = "output/story_output.md") -> float:
        """
        Update the current page count based on the output file.
        
        Returns:
            Current page count as a float
        """
        try:
            output_path = Path(output_file_path)
            if output_path.exists():
                content = output_path.read_text()
                self.word_count = self.count_words(content)
                self.page_count = self.word_count / self.words_per_page
                logger.info(f"Updated page count: {self.page_count:.2f} pages ({self.word_count} words)")
            else:
                self.page_count = 0.0
                self.word_count = 0
                
        except Exception as e:
            logger.error(f"Error updating page count: {e}")
            
        return self.page_count
    
    def should_pause_for_review(self) -> Optional[str]:
        """
        Check if the story should pause for a checkpoint review.
        
        Returns:
            Checkpoint name if review needed, None otherwise
        """
        # Update page count first
        self.update_page_count()
        
        # Check for page 1 checkpoint
        if self.page_count >= 1.0 and not self.checkpoints["page_1_review"]:
            return "page_1_checkpoint"
            
        # Check for page 2 checkpoint
        elif self.page_count >= 2.0 and not self.checkpoints["page_2_review"]:
            return "page_2_checkpoint"
            
        # Check if we're approaching the limit without proper pacing
        elif self.page_count >= 2.7 and not self.checkpoints["page_2_review"]:
            # Emergency checkpoint - too close to limit without final review
            logger.warning("Emergency checkpoint - approaching 3-page limit without page 2 review")
            return "page_2_checkpoint"
            
        return None
    
    def mark_checkpoint_complete(self, checkpoint_name: str):
        """Mark a checkpoint as completed."""
        checkpoint_map = {
            "outline_approval": "outline_approval",
            "page_1_checkpoint": "page_1_review",
            "page_2_checkpoint": "page_2_review",
            "final_approval": "final_approval"
        }
        
        if checkpoint_name in checkpoint_map:
            checkpoint_key = checkpoint_map[checkpoint_name]
            self.checkpoints[checkpoint_key] = True
            self.last_checkpoint = checkpoint_name
            
            # Add to history
            self.checkpoint_history.append({
                "checkpoint": checkpoint_name,
                "timestamp": datetime.now().isoformat(),
                "page_count": self.page_count,
                "word_count": self.word_count
            })
            
            logger.info(f"Checkpoint completed: {checkpoint_name}")
    
    def get_remaining_words(self) -> int:
        """Calculate remaining words before hitting the 3-page limit."""
        max_words = self.words_per_page * 3
        remaining = max_words - self.word_count
        return max(0, remaining)
    
    def get_remaining_pages(self) -> float:
        """Calculate remaining pages before hitting the limit."""
        return max(0, 3.0 - self.page_count)
    
    def get_progress_summary(self) -> Dict:
        """Get a summary of the current progress."""
        return {
            "current_pages": round(self.page_count, 2),
            "current_words": self.word_count,
            "remaining_pages": round(self.get_remaining_pages(), 2),
            "remaining_words": self.get_remaining_words(),
            "checkpoints_completed": self.checkpoints,
            "last_checkpoint": self.last_checkpoint,
            "can_reach_ending": self.can_reach_satisfying_ending()
        }
    
    def can_reach_satisfying_ending(self) -> Tuple[bool, str]:
        """
        Evaluate if there's enough space for a satisfying ending.
        
        Returns:
            Tuple of (can_reach_ending, reason)
        """
        remaining_words = self.get_remaining_words()
        
        if remaining_words < 100:
            return False, "Less than 100 words remaining - not enough for proper conclusion"
        elif remaining_words < 200:
            return True, "Limited space - need immediate transition to conclusion"
        elif remaining_words < 300:
            return True, "Adequate space for conclusion with one final scene"
        else:
            return True, "Sufficient space for proper story conclusion"
    
    def should_start_conclusion(self) -> bool:
        """Determine if the writer should start wrapping up the story."""
        # Start conclusion if we're past 2.5 pages or have less than 200 words left
        return self.page_count >= 2.5 or self.get_remaining_words() < 200
    
    def get_pacing_recommendation(self) -> str:
        """Get a pacing recommendation based on current progress."""
        if self.page_count < 0.5:
            return "Early development - establish atmosphere and core concept"
        elif self.page_count < 1.0:
            return "Building tension - develop the anomaly and its implications"
        elif self.page_count < 1.5:
            return "Mid-story - escalate stakes and reveal key information"
        elif self.page_count < 2.0:
            return "Approaching climax - build toward revelation or crisis"
        elif self.page_count < 2.5:
            return "Begin resolution - start tying up plot threads"
        else:
            return "Final stretch - focus on satisfying conclusion"
    
    def reset(self):
        """Reset checkpoint manager for a new story."""
        self.checkpoints = {
            "outline_approval": False,
            "page_1_review": False,
            "page_2_review": False,
            "final_approval": False
        }
        self.page_count = 0.0
        self.word_count = 0
        self.last_checkpoint = None
        self.checkpoint_history = []
        logger.info("Checkpoint manager reset for new story")