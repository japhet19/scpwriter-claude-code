import logging
from pathlib import Path
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds dynamic prompts for agents based on templates and user requests."""
    
    def __init__(self):
        self.template_dir = Path("prompts")
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load prompt templates from files."""
        templates = {}
        
        template_files = {
            "orchestrator": "orchestrator.txt",
            "writer": "writer_template.txt",
            "reader": "reader_template.txt"
        }
        
        for key, filename in template_files.items():
            template_path = self.template_dir / filename
            if template_path.exists():
                templates[key] = template_path.read_text()
            else:
                logger.warning(f"Template file not found: {template_path}")
                templates[key] = ""
                
        return templates
    
    def build_writer_prompt(self, theme: str, additional_context: str = "") -> str:
        """
        Build a customized prompt for the SCP Writer agent.
        
        Args:
            theme: The story theme/request from the user
            additional_context: Any additional context from analysis
            
        Returns:
            Customized writer prompt
        """
        template = self.templates.get("writer", "")
        
        # Replace placeholders
        prompt = template.replace("{THEME}", theme)
        
        # Add additional context if provided
        if additional_context:
            prompt += f"\n\nAdditional Context:\n{additional_context}"
            
        return prompt
    
    def build_reader_prompt(self, persona: str, theme: str) -> str:
        """
        Build a customized prompt for the Reader agent.
        
        Args:
            persona: Description of the reader persona
            theme: The story theme for context
            
        Returns:
            Customized reader prompt
        """
        template = self.templates.get("reader", "")
        
        # Replace placeholders
        prompt = template.replace("{PERSONA}", persona)
        
        # Add theme context
        prompt += f"\n\nStory Theme: {theme}"
        
        return prompt
    
    def create_reader_persona(self, theme: str, analysis: Dict[str, Any]) -> str:
        """
        Create a reader persona based on the story theme and analysis.
        
        Args:
            theme: The story theme
            analysis: Analysis results from the orchestrator
            
        Returns:
            Persona description
        """
        # Extract tone and genre from analysis if available
        tone = "horror and mystery"  # default
        if "tone" in str(analysis).lower():
            if "scientific" in str(analysis).lower():
                tone = "scientific horror and philosophical speculation"
            elif "psychological" in str(analysis).lower():
                tone = "psychological horror and human drama"
            elif "cosmic" in str(analysis).lower():
                tone = "cosmic horror and existential dread"
                
        # Build persona based on theme
        persona_templates = {
            "antimemetic": f"""You are an avid reader of mind-bending SCP fiction who loves:
- Stories that challenge perception and memory
- Unreliable narrators and reality-questioning concepts  
- Subtle horror that gets under the skin
- Intelligent plots that reward careful reading
You appreciate {tone} and expect sophisticated narrative techniques.""",
            
            "containment": f"""You are a fan of classic SCP stories focusing on:
- Creative containment procedures and their implications
- The human cost of working with anomalies
- Bureaucratic horror and institutional mysteries
- Rich world-building within the Foundation
You enjoy {tone} and value authentic Foundation atmosphere.""",
            
            "temporal": f"""You are drawn to time-based anomaly stories featuring:
- Paradoxes and causality loops
- Characters dealing with temporal displacement
- The horror of losing one's place in time
- Complex plots that come together brilliantly
You seek {tone} with intricate plotting.""",
            
            "reality": f"""You love reality-bending SCP narratives with:
- Entities that defy physical laws
- Protagonists questioning what's real
- Layers of reality and metafictional elements
- Surreal imagery and dream logic
You crave {tone} that challenges conventional storytelling.""",
            
            "default": f"""You are an experienced SCP fiction reader who values:
- Original concepts and fresh takes on anomalies
- Strong character development and emotional stakes
- Atmospheric writing that builds tension effectively
- Satisfying conclusions that respect the reader's intelligence
You appreciate {tone} and expect quality narrative fiction."""
        }
        
        # Match theme to persona template
        theme_lower = theme.lower()
        if "memetic" in theme_lower or "antimemetic" in theme_lower:
            persona = persona_templates["antimemetic"]
        elif "contain" in theme_lower or "procedure" in theme_lower:
            persona = persona_templates["containment"]
        elif "time" in theme_lower or "temporal" in theme_lower:
            persona = persona_templates["temporal"]
        elif "reality" in theme_lower or "dimension" in theme_lower:
            persona = persona_templates["reality"]
        else:
            persona = persona_templates["default"]
            
        return persona
    
    def build_arbitration_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build a prompt for arbitration situations.
        
        Args:
            context: Context about the disagreement
            
        Returns:
            Arbitration prompt
        """
        base_prompt = """As the Writing Expert and Orchestrator, you need to resolve this disagreement.

Consider:
1. The reader represents your audience - their satisfaction is crucial
2. The writer's creative vision and narrative integrity
3. The story constraints (3-page limit, current progress)
4. The overall quality and impact of the final story

Make a decision that serves the story best while respecting both perspectives."""
        
        if "urgency" in context and context["urgency"] == "high":
            base_prompt += "\n\nThis is a critical decision that will significantly impact the story's conclusion."
            
        return base_prompt
    
    def build_checkpoint_prompt(self, checkpoint_type: str, progress: Dict[str, Any]) -> str:
        """
        Build prompts for checkpoint situations.
        
        Args:
            checkpoint_type: Type of checkpoint
            progress: Current story progress
            
        Returns:
            Checkpoint prompt
        """
        prompts = {
            "page_1_checkpoint": f"""Page 1 Checkpoint Review

Progress: {progress.get('current_pages', 0):.1f} pages written
Remaining: {progress.get('remaining_pages', 0):.1f} pages

Guide the reader to focus on:
- Story engagement and hook effectiveness
- Character and atmosphere establishment  
- Pacing appropriateness
- Areas for improvement

This is an early checkpoint - changes can still be made easily.""",
            
            "page_2_checkpoint": f"""Critical Page 2 Checkpoint

Progress: {progress.get('current_pages', 0):.1f} pages written
Remaining: {progress.get('remaining_pages', 0):.1f} pages
Words remaining: ~{progress.get('remaining_words', 0)}

This is the final major checkpoint. Ensure the reader evaluates:
- Can the story conclude satisfyingly in the remaining space?
- What must be resolved vs. what can be left ambiguous?
- Is immediate transition to conclusion needed?
- Any emergency concerns about the ending?"""
        }
        
        return prompts.get(checkpoint_type, "Checkpoint review needed.")
    
    def get_prompt_summary(self) -> Dict[str, int]:
        """Get a summary of loaded prompts."""
        return {
            "templates_loaded": len(self.templates),
            "orchestrator_length": len(self.templates.get("orchestrator", "")),
            "writer_template_length": len(self.templates.get("writer", "")),
            "reader_template_length": len(self.templates.get("reader", ""))
        }