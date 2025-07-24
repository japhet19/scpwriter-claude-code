import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from agents import WritingExpertAgent, SCPWriterAgent, ReaderAgent
from utils import SessionManager, CheckpointManager, PromptBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StoryOrchestrator:
    """Main orchestrator that manages the entire SCP story writing process."""
    
    def __init__(self):
        # Initialize core components
        self.session_manager = SessionManager()
        self.checkpoint_manager = CheckpointManager()
        self.prompt_builder = PromptBuilder()
        
        # Initialize orchestrator agent with callback
        self.orchestrator = WritingExpertAgent(self.session_manager, orchestrator_callback=self.agent_callback)
        self.orchestrator.set_checkpoint_manager(self.checkpoint_manager)
        
        # Other agents will be initialized after prompt creation
        self.writer_agent: Optional[SCPWriterAgent] = None
        self.reader_agent: Optional[ReaderAgent] = None
        
        # Process state
        self.is_running = False
        self.current_phase = "initialization"
        self.story_complete = False
        self.pending_decision = False
        self.last_speaker = None
        self.last_message = None
        
    async def agent_callback(self, agent_name: str, message: str):
        """Called by agents after they write to discussion file."""
        logger.info(f"Callback from {agent_name}")
        self.last_speaker = agent_name
        self.last_message = message
        
        # Only trigger decision if agent signals completion with [DONE]
        if "[DONE]" in message or "---END---" in message:
            logger.info(f"{agent_name} signaled completion")
            self.pending_decision = True
        else:
            logger.info(f"{agent_name} still working, no decision needed")
        
    async def initialize_project(self, user_request: str) -> Dict[str, Any]:
        """Initialize a new story project with the user's request."""
        logger.info(f"Initializing project with request: {user_request}")
        
        # Start new project in session manager
        project_id = self.session_manager.start_new_project()
        logger.info(f"Started project: {project_id}")
        
        # Reset checkpoint manager
        self.checkpoint_manager.reset()
        
        # Initialize project through orchestrator
        init_result = await self.orchestrator.initialize_project(user_request)
        
        # Create customized prompts
        writer_prompt = self.prompt_builder.build_writer_prompt(
            theme=user_request,
            additional_context=init_result['analysis'].get('analysis', '')
        )
        
        # Create reader persona
        reader_persona = self.prompt_builder.create_reader_persona(
            theme=user_request,
            analysis=init_result['analysis']
        )
        
        reader_prompt = self.prompt_builder.build_reader_prompt(
            persona=reader_persona,
            theme=user_request
        )
        
        # Initialize writer and reader agents with custom prompts and callback
        self.writer_agent = SCPWriterAgent(writer_prompt, orchestrator_callback=self.agent_callback)
        self.reader_agent = ReaderAgent(reader_prompt, reader_persona, orchestrator_callback=self.agent_callback)
        
        # Note: Agents will register their sessions when they first interact with Claude
        # No pre-registration needed
        
        logger.info("All agents initialized and registered")
        
        return {
            "project_id": project_id,
            "agents_initialized": True
        }
    
    async def run_story_creation(self, user_request: str):
        """Run the complete story creation process."""
        self.is_running = True
        
        try:
            # Initialize project
            await self.initialize_project(user_request)
            
            # Start the process with outline creation
            await self.start_outline_phase()
            
            # Main control loop
            while self.is_running and not self.story_complete:
                # Process pending decisions
                if self.pending_decision:
                    await self.process_next_turn()
                
                # Check for story completion
                if await self.check_story_completion():
                    self.story_complete = True
                    break
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                    
            logger.info("Story creation process completed")
            
        except Exception as e:
            logger.error(f"Error in story creation: {e}")
            raise
            
        finally:
            self.is_running = False
    
    async def start_outline_phase(self):
        """Start the outline creation phase."""
        self.current_phase = "outline"
        logger.info("Starting outline phase")
        
        # Write the initial message
        message = "SCP_WRITER: Please create your story outline based on the theme and requirements.\n\n[DONE]"
        await self.orchestrator._append_to_discussion(message)
        
        # Trigger the decision process
        self.pending_decision = True
        self.last_speaker = "ORCHESTRATOR"
        self.last_message = message
    
    async def process_next_turn(self):
        """Process the next turn based on the last speaker and message."""
        logger.info(f"Processing next turn after {self.last_speaker}")
        
        # Decide who should respond next
        next_agent = await self.orchestrator.decide_next_agent(self.last_speaker, self.last_message)
        logger.info(f"Next agent to respond: {next_agent}")
        
        # Route to appropriate agent
        if next_agent == "SCP_WRITER" and self.writer_agent:
            await self.handle_writer_turn(self.last_message)
        elif next_agent == "READER" and self.reader_agent:
            await self.handle_reader_turn(self.last_message)
        else:
            await self.handle_orchestrator_turn(self.last_message)
        
        # Clear pending decision
        self.pending_decision = False
    
    
    async def handle_writer_turn(self, trigger_message: str):
        """Handle the writer's turn."""
        logger.info("Writer's turn")
        
        # Determine appropriate action based on phase
        if self.current_phase == "outline":
            # Create outline
            await self.writer_agent.create_outline()
        elif self.current_phase == "writing":
            # Continue writing story
            await self.writer_agent.continue_story()
        elif self.current_phase == "revision":
            # Incorporate feedback
            await self.writer_agent.incorporate_feedback(trigger_message)
            
        if self.writer_agent.session_id:
            self.session_manager.increment_message_count(self.writer_agent.session_id)
    
    async def handle_reader_turn(self, trigger_message: str):
        """Handle the reader's turn."""
        logger.info("Reader's turn")
        
        # Determine what to review
        if "outline" in self.current_phase:
            await self.reader_agent.review_outline()
        elif "checkpoint" in trigger_message.lower():
            # Extract checkpoint type
            checkpoint_type = self.checkpoint_manager.last_checkpoint
            page_count = self.checkpoint_manager.page_count
            remaining = self.checkpoint_manager.get_remaining_pages()
            
            await self.reader_agent.review_checkpoint(
                checkpoint_type, page_count, remaining
            )
        elif self.current_phase == "final_review":
            await self.reader_agent.review_final_story()
            
        if self.reader_agent.session_id:
            self.session_manager.increment_message_count(self.reader_agent.session_id)
    
    async def handle_orchestrator_turn(self, trigger_message: str):
        """Handle the orchestrator's turn."""
        logger.info("Orchestrator's turn")
        
        # Orchestrator manages process flow
        if "outline approved" in trigger_message.lower():
            self.current_phase = "writing"
            self.checkpoint_manager.mark_checkpoint_complete("outline_approval")
            
            message = "Outline approved. SCP_WRITER, please begin writing the story in story_output.md.\n\n[DONE]"
            await self.orchestrator._append_to_discussion(message)
            # Trigger callback for orchestrator messages
            if self.orchestrator.orchestrator_callback:
                await self.orchestrator.orchestrator_callback("ORCHESTRATOR", message)
            await self.writer_agent.start_story()
            
        if self.orchestrator.session_id:
            self.session_manager.increment_message_count(self.orchestrator.session_id)
    
    async def trigger_checkpoint_review(self, checkpoint_type: str):
        """Trigger a checkpoint review."""
        logger.info(f"Triggering checkpoint: {checkpoint_type}")
        
        # Notify writer to pause
        await self.writer_agent.handle_checkpoint_pause(checkpoint_type)
        
        # Orchestrator announces checkpoint
        await self.orchestrator.handle_checkpoint(checkpoint_type)
        
        # Mark checkpoint for tracking
        self.checkpoint_manager.mark_checkpoint_complete(checkpoint_type)
        
        # Reader will respond to the checkpoint announcement
    
    async def notify_conclusion_needed(self):
        """Notify that the story needs to start concluding."""
        logger.info("Notifying conclusion needed")
        
        remaining_words = self.checkpoint_manager.get_remaining_words()
        guidance = await self.orchestrator.provide_pacing_guidance(
            self.checkpoint_manager.page_count
        )
        
        # Writer responds to pacing guidance
        await self.writer_agent.write_conclusion(remaining_words)
    
    async def check_story_completion(self) -> bool:
        """Check if the story is complete."""
        if self.current_phase == "completed":
            return True
        
        # Only check for completion if we're actually in the writing phase
        # and have written something
        if self.current_phase not in ["writing", "revision", "concluding"]:
            return False
            
        # Check if any content exists in the output file
        output_content = Path("output/story_output.md").read_text()
        if len(output_content.strip()) < 100:  # Less than ~20 words
            return False
            
        # Now check with orchestrator
        if await self.orchestrator.evaluate_story_completion():
            self.current_phase = "completed"
            await self.finalize_story()
            return True
            
        return False
    
    async def finalize_story(self):
        """Finalize the completed story."""
        logger.info("Finalizing story")
        
        # Get final stats
        final_stats = {
            "project_summary": self.session_manager.get_project_summary(),
            "checkpoint_summary": self.checkpoint_manager.get_progress_summary()
        }
        
        # Save final output
        output_path = Path("output/story_output.md")
        final_path = Path(f"output/story_final_{self.session_manager.active_project_id}.md")
        
        if output_path.exists():
            import shutil
            shutil.copy(output_path, final_path)
            logger.info(f"Final story saved to: {final_path}")
        
        # Log completion
        logger.info("Story creation completed successfully")
        logger.info(f"Final stats: {final_stats}")
        
        return final_stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            "is_running": self.is_running,
            "current_phase": self.current_phase,
            "story_complete": self.story_complete,
            "agents_active": all([
                self.orchestrator is not None,
                self.writer_agent is not None,
                self.reader_agent is not None
            ]),
            "progress": self.checkpoint_manager.get_progress_summary() if self.checkpoint_manager else None,
            "sessions": self.session_manager.get_project_summary() if self.session_manager else None
        }