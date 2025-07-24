import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .base_agent import BaseAgent
from utils.session_manager import SessionManager

logger = logging.getLogger(__name__)


class WritingExpertAgent(BaseAgent):
    """
    The Writing Expert/Orchestrator agent that manages the entire SCP writing process.
    This agent creates prompts for other agents, monitors progress, and makes decisions.
    """
    
    def __init__(self, session_manager: SessionManager, orchestrator_callback=None):
        # Stable system prompt for the orchestrator
        system_prompt = self._load_orchestrator_prompt()
        super().__init__("ORCHESTRATOR", system_prompt, orchestrator_callback)
        
        self.session_manager = session_manager
        self.checkpoint_manager = None  # Will be set by main orchestrator
        self.current_phase = "initialization"
        self.story_theme = ""
        self.target_length = 3  # pages
        self.agents_initialized = False
        self.writer_agent = None
        self.reader_agent = None
        
    def _load_orchestrator_prompt(self) -> str:
        """Load the stable orchestrator prompt from file."""
        prompt_path = Path("prompts/orchestrator.txt")
        if prompt_path.exists():
            return prompt_path.read_text()
        
        # Default prompt if file doesn't exist
        return """You are the Writing Expert and Orchestrator for an SCP story writing team.

Your responsibilities:
1. Analyze user requests and create appropriate prompts for the SCP Writer and Reader agents
2. Monitor the writing process and enforce checkpoints at 1-page and 2-page marks
3. Resolve disagreements between Writer and Reader agents
4. Ensure the story reaches a satisfying conclusion within the 3-page limit
5. Make decisions about who should respond next in the discussion

Key principles:
- Quality over speed - ensure the story is engaging and well-paced
- The Reader's satisfaction is paramount - they represent the audience
- At the 2-page checkpoint, critically evaluate if the story can conclude satisfyingly
- You have veto power but use it judiciously
- Foster constructive collaboration between agents

Communication style:
- Clear, decisive, and constructive
- Provide specific guidance when needed
- Acknowledge good ideas from both agents
- Keep the process moving forward efficiently"""
    
    def set_checkpoint_manager(self, checkpoint_manager):
        """Set the checkpoint manager instance."""
        self.checkpoint_manager = checkpoint_manager
    
    async def analyze_user_request(self, user_request: str) -> Dict[str, str]:
        """
        Analyze the user's story request and extract key information.
        
        Returns:
            Dict containing theme, genre, and other relevant details
        """
        analysis_prompt = f"""
Analyze this SCP story request and extract key information:

User request: "{user_request}"

Provide a structured analysis including:
1. Main theme or concept
2. Expected tone (horror, mystery, scientific, etc.)
3. Any specific elements requested
4. Suggested reader persona type
5. Key narrative elements to emphasize

Format your response as a clear, structured analysis.
"""
        
        response = await self.respond(analysis_prompt)
        
        # Store the theme for later use
        self.story_theme = user_request
        
        return {
            "analysis": response,
            "theme": user_request
        }
    
    async def create_agent_prompts(self, analysis: Dict[str, str]) -> Tuple[str, str]:
        """
        Create customized prompts for the SCP Writer and Reader agents.
        
        Returns:
            Tuple of (writer_prompt, reader_prompt)
        """
        prompt_creation = f"""
Based on this analysis of the user's request:
{analysis['analysis']}

Create two specialized system prompts:

1. SCP WRITER PROMPT:
- Should emphasize narrative-style SCP writing (like "There Is No Antimemetics Division")
- Include the specific theme: {analysis['theme']}
- Mention the 3-page limit and checkpoint system
- Emphasize creating engaging, atmospheric storytelling

2. READER PROMPT:
- Create a persona that represents the target audience for this type of story
- Include their preferences, expectations, and what would satisfy them
- Mention their role in providing feedback at checkpoints
- Emphasize the importance of pacing and satisfying conclusions

Provide both prompts clearly separated and labeled.
"""
        
        response = await self.respond(prompt_creation)
        
        # Parse the response to extract both prompts
        # This is simplified - in production would use more robust parsing
        lines = response.split('\n')
        writer_prompt = ""
        reader_prompt = ""
        current_section = ""
        
        for line in lines:
            if "SCP WRITER PROMPT" in line.upper():
                current_section = "writer"
            elif "READER PROMPT" in line.upper():
                current_section = "reader"
            elif current_section == "writer":
                writer_prompt += line + "\n"
            elif current_section == "reader":
                reader_prompt += line + "\n"
        
        return writer_prompt.strip(), reader_prompt.strip()
    
    async def decide_next_agent(self, last_speaker: str, last_message: str) -> str:
        """
        Decide which agent should respond next based on the conversation flow.
        
        Returns:
            The name of the agent who should respond next
        """
        decision_prompt = f"""
Review the latest message in the discussion:

Last speaker: {last_speaker}
Message: {last_message}

Current phase: {self.current_phase}
Checkpoint status: {self.checkpoint_manager.checkpoints if self.checkpoint_manager else 'Not initialized'}

Based on the conversation flow and current needs, who should respond next?
Options:
1. "SCP_WRITER" - If the writer needs to provide content or respond to feedback
2. "READER" - If the reader needs to review content or provide feedback
3. "ORCHESTRATOR" - If you need to intervene, resolve a dispute, or guide the process

Respond with just the agent name. Do not write [DONE] as this is just a decision.
"""
        
        response = await self.respond(decision_prompt, skip_callback=True)
        
        # Extract agent name from response
        if "SCP_WRITER" in response.upper():
            return "SCP_WRITER"
        elif "READER" in response.upper():
            return "READER"
        else:
            return "ORCHESTRATOR"
    
    async def handle_checkpoint(self, checkpoint_type: str) -> str:
        """
        Handle checkpoint events and coordinate the review process.
        
        Returns:
            Instructions for the agents
        """
        if checkpoint_type == "page_1_checkpoint":
            message = """CHECKPOINT REACHED: Page 1 Review

SCP_WRITER: Please pause your writing.
READER: Please review the story in story_output.md and provide feedback on:
- Engagement and atmosphere
- Character/concept development
- Pacing and flow
- Any concerns or suggestions

Focus on constructive feedback that will improve the remaining 2 pages.

[DONE]"""
            
        elif checkpoint_type == "page_2_checkpoint":
            message = """CRITICAL CHECKPOINT: Page 2 Review

SCP_WRITER: Please pause your writing.
READER: This is a critical review point. Please evaluate:
- Can the story reach a satisfying conclusion in the remaining ~300 words?
- What plot threads need resolution?
- Is the pacing appropriate for a strong ending?
- Specific suggestions for the conclusion

This feedback will determine the final page's direction.

[DONE]"""
            
        else:
            message = f"Checkpoint {checkpoint_type} reached. Proceeding with review."
        
        await self._append_to_discussion(message)
        # Since this is a direct message, trigger callback manually
        if self.orchestrator_callback:
            await self.orchestrator_callback(self.name, message)
        return message
    
    async def resolve_disagreement(self, writer_position: str, reader_position: str) -> str:
        """
        Resolve disagreements between Writer and Reader agents.
        
        Returns:
            The arbitration decision
        """
        arbitration_prompt = f"""
There is a disagreement between the Writer and Reader:

WRITER'S POSITION:
{writer_position}

READER'S POSITION:
{reader_position}

As the Writing Expert, analyze both positions and make a decision that:
1. Serves the story's best interests
2. Respects the Reader's perspective (they represent the audience)
3. Maintains narrative quality and pacing
4. Considers the remaining page budget

Provide a clear decision and brief reasoning.
"""
        
        decision = await self.respond(arbitration_prompt)
        
        await self._append_to_discussion(f"ARBITRATION DECISION:\n{decision}\n\n[DONE]")
        # Since this is a direct message, trigger callback manually
        if self.orchestrator_callback:
            await self.orchestrator_callback(self.name, f"ARBITRATION DECISION:\n{decision}\n\n[DONE]")
        return decision
    
    async def evaluate_story_completion(self) -> bool:
        """
        Evaluate whether the story is complete and satisfactory.
        
        Returns:
            True if the story is complete, False otherwise
        """
        evaluation_prompt = """
Review the current story in story_output.md and the discussion history.

Evaluate:
1. Is the story complete with a satisfying ending?
2. Are all major plot points resolved?
3. Does it meet the quality standards for an SCP narrative?
4. Is it within the 3-page limit?

Respond with either:
- "COMPLETE" if the story is finished and satisfactory
- "NEEDS_WORK: [specific issues]" if more work is needed
"""
        
        response = await self.respond(evaluation_prompt, include_output=True)
        
        return "COMPLETE" in response.upper()
    
    async def provide_pacing_guidance(self, current_page: float) -> str:
        """
        Provide pacing guidance based on current progress.
        
        Returns:
            Guidance message for the writer
        """
        pages_remaining = self.target_length - current_page
        
        guidance_prompt = f"""
Current progress: {current_page:.1f} pages written
Remaining: {pages_remaining:.1f} pages

Based on the story so far, provide specific pacing guidance:
1. What needs to be accomplished in the remaining space?
2. Should the writer accelerate toward the climax?
3. Any plot threads that need immediate attention?

Be specific and actionable.
"""
        
        guidance = await self.respond(guidance_prompt, include_output=True)
        
        await self._append_to_discussion(f"PACING GUIDANCE:\n{guidance}\n\n[DONE]")
        # Since this is a direct message, trigger callback manually
        if self.orchestrator_callback:
            await self.orchestrator_callback(self.name, f"PACING GUIDANCE:\n{guidance}\n\n[DONE]")
        return guidance
    
    async def initialize_project(self, user_request: str) -> Dict[str, Any]:
        """
        Initialize a new story project with the given request.
        
        Returns:
            Project initialization details
        """
        self.current_phase = "initialization"
        
        # Clear previous discussion and output files
        Path("discussions/story_discussion.md").write_text("")
        Path("output/story_output.md").write_text("")
        
        # Announce project start
        announcement = f"""PROJECT INITIATED: SCP Story Writing

User Request: "{user_request}"
Target Length: 3 pages maximum
Style: Narrative format (similar to "There Is No Antimemetics Division")

I will now analyze this request and create specialized prompts for our writing team.\n\n[DONE]"""
        
        await self._append_to_discussion(announcement)
        # Since this is a direct message, trigger callback manually
        if self.orchestrator_callback:
            await self.orchestrator_callback(self.name, announcement)
        
        # Analyze request
        analysis = await self.analyze_user_request(user_request)
        
        # Create agent prompts
        writer_prompt, reader_prompt = await self.create_agent_prompts(analysis)
        
        self.current_phase = "outline_development"
        
        return {
            "analysis": analysis,
            "writer_prompt": writer_prompt,
            "reader_prompt": reader_prompt,
            "project_initialized": True
        }