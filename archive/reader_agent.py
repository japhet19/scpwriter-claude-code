import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ReaderAgent(BaseAgent):
    """
    The Reader agent representing the target audience, providing feedback on the story.
    """
    
    def __init__(self, system_prompt: str, persona_description: str = "", orchestrator_callback=None):
        super().__init__("READER", system_prompt, orchestrator_callback)
        self.persona_description = persona_description
        self.reviewed_checkpoints = []
        self.satisfaction_level = "neutral"
        self.concerns = []
        
    async def review_outline(self) -> str:
        """Review the story outline and provide initial feedback."""
        review_prompt = """Review the writer's story outline in the discussion file.

Consider:
1. Does the concept excite you as a reader?
2. Is the anomaly/concept original and intriguing?
3. Are the characters relatable or interesting?
4. Does the planned story arc promise a satisfying journey?
5. Any concerns about the planned execution?

Provide specific, constructive feedback. Be honest about what works and what might need adjustment.

End your review with [DONE]."""
        
        response = await self.respond(review_prompt)
        self.reviewed_checkpoints.append("outline")
        return response
    
    async def review_checkpoint(self, checkpoint_type: str, page_count: float, remaining_pages: float) -> str:
        """Review the story at a specific checkpoint."""
        if checkpoint_type == "page_1_checkpoint":
            review_prompt = f"""Read the story so far in story_output.md (approximately 1 page written).

Evaluate:
1. Is the opening engaging? Are you hooked?
2. Is the atmosphere effectively established?
3. Are the characters compelling?
4. Is the pacing appropriate?
5. Any concerns or suggestions for improvement?

You have about {remaining_pages:.1f} pages remaining. Consider if the story is on track."""
            
        elif checkpoint_type == "page_2_checkpoint":
            review_prompt = f"""Read the story in story_output.md (approximately 2 pages written).

CRITICAL EVALUATION - only {remaining_pages:.1f} pages remain!

Assess:
1. Can the story reach a satisfying conclusion in the remaining space?
2. What plot elements MUST be resolved?
3. Is the pacing appropriate for a strong ending?
4. Should the writer start transitioning to the conclusion?
5. Any threads that should be dropped to focus on core resolution?

This is your last chance to influence the ending. Be specific about what needs to happen.

End your review with [DONE]."""
        
        else:
            review_prompt = f"""Review the current story progress at {checkpoint_type}."""
        
        response = await self.respond(review_prompt, include_output=True)
        self.reviewed_checkpoints.append(checkpoint_type)
        
        # Update satisfaction based on checkpoint
        if checkpoint_type == "page_2_checkpoint":
            await self._evaluate_ending_potential(remaining_pages)
            
        return response
    
    async def _evaluate_ending_potential(self, remaining_pages: float) -> None:
        """Privately evaluate if the story can end well."""
        evaluation_prompt = f"""Based on your reading, internally assess:
- Can this story end satisfyingly in {remaining_pages:.1f} pages?
- Rate your confidence: high/medium/low

Just respond with your confidence level."""
        
        response = await self.respond(evaluation_prompt, include_output=True)
        
        if "low" in response.lower():
            self.concerns.append("ending_risk")
            self.satisfaction_level = "concerned"
        elif "high" in response.lower():
            self.satisfaction_level = "optimistic"
        else:
            self.satisfaction_level = "cautious"
    
    async def review_final_story(self) -> str:
        """Provide final review of the completed story."""
        final_review_prompt = """Read the complete story in story_output.md.

Provide your final assessment:
1. Did the story deliver on its promise?
2. Was the ending satisfying?
3. Were all important elements resolved?
4. How was the overall pacing?
5. Would you recommend this story to other readers?

Give an honest but balanced review. Acknowledge both strengths and weaknesses.

End your review with [DONE]."""
        
        response = await self.respond(final_review_prompt, include_output=True)
        self.reviewed_checkpoints.append("final")
        return response
    
    async def express_concern(self, issue: str) -> str:
        """Express a specific concern about the story's direction."""
        concern_prompt = f"""You have a concern about: {issue}

Express this concern clearly and constructively in the discussion.
Explain why this matters from a reader's perspective.
Suggest potential solutions if possible.

End your concern with [DONE]."""
        
        response = await self.respond(concern_prompt)
        self.concerns.append(issue)
        return response
    
    async def praise_element(self, element: str) -> str:
        """Praise a specific element of the story."""
        praise_prompt = f"""You particularly enjoyed: {element}

Express your appreciation for this element.
Explain why it works well from a reader's perspective.
Encourage the writer to maintain or build on this strength.

End your message with [DONE]."""
        
        response = await self.respond(praise_prompt)
        return response
    
    async def negotiate_feedback(self, writer_response: str) -> str:
        """Respond when the writer disagrees with feedback."""
        negotiation_prompt = f"""The writer has responded to your feedback:

{writer_response}

Consider their perspective, but remember you represent the readers.
If you still feel your feedback is valid, explain why.
If they've convinced you, acknowledge it.
Find a constructive path forward.

End your response with [DONE]."""
        
        response = await self.respond(negotiation_prompt)
        return response
    
    async def emergency_intervention(self) -> str:
        """Intervene when the story is going seriously off track."""
        intervention_prompt = """You need to make an emergency intervention.

The story is at risk of an unsatisfying conclusion or major issues.
Be direct but constructive about what needs to change NOW.
This is your strongest feedback - use it wisely.

End your intervention with [DONE]."""
        
        response = await self.respond(intervention_prompt, include_output=True)
        self.concerns.append("emergency_intervention")
        return response
    
    def get_reader_status(self) -> Dict[str, Any]:
        """Get the current status of the reader."""
        return {
            "agent_name": self.name,
            "persona": self.persona_description,
            "reviewed_checkpoints": self.reviewed_checkpoints,
            "satisfaction_level": self.satisfaction_level,
            "active_concerns": self.concerns,
            "session_active": self.session_id is not None
        }
    
    def should_intervene(self) -> bool:
        """Determine if the reader should proactively intervene."""
        # Intervene if there are ending concerns and we're past page 2
        return "ending_risk" in self.concerns and "page_2_checkpoint" in self.reviewed_checkpoints