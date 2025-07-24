import logging
from pathlib import Path
from typing import Optional, Dict, Any

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SCPWriterAgent(BaseAgent):
    """
    The SCP Writer agent responsible for creating story outlines and writing the narrative.
    """
    
    def __init__(self, system_prompt: str, orchestrator_callback=None):
        super().__init__("SCP_WRITER", system_prompt, orchestrator_callback)
        self.outline_created = False
        self.story_started = False
        self.current_phase = "waiting"
        self.checkpoint_paused = False
        
    async def create_outline(self) -> str:
        """Create the initial story outline based on the theme."""
        self.current_phase = "outlining"
        
        outline_prompt = """Based on the theme and requirements in your system prompt, create a detailed story outline.

Include:
1. Core Concept/Anomaly: What is the central anomalous element?
2. Main Character(s): Who are they and how do they relate to the anomaly?
3. Story Structure:
   - Beginning: How does the story open? What hooks the reader?
   - Middle: How does tension build? What is revealed?
   - End: What is the climax/resolution? Any twist?
4. Key Themes: What deeper ideas does the story explore?
5. Tone/Atmosphere: What feeling should readers have?

Respond with your complete outline. When complete, end your message with [DONE] to signal you're ready for feedback."""
        
        response = await self.respond(outline_prompt)
        self.outline_created = True
        return response
    
    async def start_story(self) -> str:
        """Begin writing the story in the output file after outline approval."""
        self.current_phase = "writing"
        self.story_started = True
        
        start_prompt = """Your outline has been approved. Now begin writing the story in story_output.md.

Remember:
- Write in narrative style, not clinical SCP documentation
- Focus on atmosphere and character engagement
- You have approximately 3 pages (825 words) total
- You'll pause at 1-page (~275 words) for feedback
- Make the opening compelling to hook readers immediately

Begin writing the story now. Signal completion with [DONE]."""
        
        response = await self.respond(start_prompt)
        return response
    
    async def continue_story(self, after_checkpoint: bool = False) -> str:
        """Continue writing the story after a pause or checkpoint."""
        if after_checkpoint:
            continue_prompt = """Review the reader's feedback from the checkpoint, then continue writing the story in story_output.md.

Take the feedback seriously and adjust your approach if needed.
Remember your page limit and current progress.
Continue building toward your planned conclusion."""
        else:
            continue_prompt = """Continue writing the story in story_output.md from where you left off.

Maintain consistency with what you've already written.
Keep track of your pacing and remaining page budget."""
        
        response = await self.respond(continue_prompt, include_output=True)
        return response
    
    async def handle_checkpoint_pause(self, checkpoint_type: str) -> str:
        """Handle a checkpoint pause in writing."""
        self.checkpoint_paused = True
        
        pause_acknowledgment = f"""I've reached the {checkpoint_type} and will pause for reader feedback.

Current status:
- Phase: {self.current_phase}
- Checkpoint: {checkpoint_type}
- Awaiting: Reader review of story progress

I'll wait for the reader's feedback before continuing.

[DONE]"""
        
        await self._append_to_discussion(pause_acknowledgment)
        return pause_acknowledgment
    
    async def incorporate_feedback(self, feedback: str) -> str:
        """Process and respond to reader feedback."""
        feedback_prompt = f"""The reader has provided the following feedback:

{feedback}

Please respond to this feedback:
1. Acknowledge the key points raised
2. Explain how you'll address concerns
3. Clarify any misunderstandings
4. State your plan for moving forward

If you disagree with any feedback, explain your reasoning respectfully.

End your response with [DONE]."""
        
        response = await self.respond(feedback_prompt)
        self.checkpoint_paused = False
        return response
    
    async def write_conclusion(self, remaining_words: int) -> str:
        """Write the story conclusion with word budget awareness."""
        self.current_phase = "concluding"
        
        conclusion_prompt = f"""You need to bring the story to a satisfying conclusion.

Remaining word budget: approximately {remaining_words} words

Requirements:
- Resolve the main conflict or mystery
- Provide emotional closure for characters
- Maintain the tone and quality of earlier sections
- Don't rush - use your remaining words effectively
- Ensure the ending resonates with the story's themes

Complete the story now in story_output.md. Signal completion with [DONE]."""
        
        response = await self.respond(conclusion_prompt, include_output=True)
        return response
    
    async def handle_pacing_guidance(self, guidance: str) -> str:
        """Respond to pacing guidance from the orchestrator."""
        pacing_prompt = f"""The orchestrator has provided the following pacing guidance:

{guidance}

Acknowledge this guidance and explain how you'll adjust your writing approach.
Then continue writing with these considerations in mind. Signal completion with [DONE]."""
        
        response = await self.respond(pacing_prompt)
        return response
    
    async def revise_section(self, section: str, reason: str) -> str:
        """Revise a section of the story based on feedback."""
        revision_prompt = f"""You need to revise the following section:

{section}

Reason for revision: {reason}

Edit the story in story_output.md to improve this section while maintaining continuity with the rest of the story. Signal completion with [DONE]."""
        
        response = await self.respond(revision_prompt, include_output=True)
        return response
    
    def get_writer_status(self) -> Dict[str, Any]:
        """Get the current status of the writer."""
        return {
            "agent_name": self.name,
            "current_phase": self.current_phase,
            "outline_created": self.outline_created,
            "story_started": self.story_started,
            "checkpoint_paused": self.checkpoint_paused,
            "session_active": self.session_id is not None
        }