#!/usr/bin/env python3
"""Test orchestration with mock agents for fast debugging."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockAgent:
    """Mock agent that returns predefined responses instantly."""
    
    def __init__(self, name: str, responses: Dict[str, str], orchestrator_callback=None):
        self.name = name
        self.responses = responses
        self.orchestrator_callback = orchestrator_callback
        self.call_count = 0
        self.session_id = f"mock-session-{name}"
        
    async def respond(self, trigger_message: str, include_output: bool = False, skip_callback: bool = False):
        """Return a predefined response based on the trigger."""
        self.call_count += 1
        
        # Find matching response
        response = None
        for key, value in self.responses.items():
            if key.lower() in trigger_message.lower():
                response = value
                break
        
        if response is None:
            response = f"[{self.name}] No response configured for: {trigger_message[:50]}..."
        
        # Log the interaction
        logger.info(f"{self.name} responding to: {trigger_message[:50]}...")
        logger.info(f"{self.name} response: {response[:50]}...")
        
        # Append to discussion
        await self._append_to_discussion(response)
        
        # Trigger callback if needed
        if self.orchestrator_callback and not skip_callback:
            await self.orchestrator_callback(self.name, response)
        
        return response
    
    async def _append_to_discussion(self, message: str):
        """Append message to discussion file."""
        discussion_path = Path("discussions/story_discussion.md")
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_message = f"\n## [{self.name}] - [{timestamp}]\n{message}\n---\n"
        
        with open(discussion_path, 'a') as f:
            f.write(formatted_message)


async def test_full_orchestration():
    """Test the full orchestration flow with mock agents."""
    print("\n=== Testing Full Orchestration with Mock Agents ===\n")
    
    # Clear files
    Path("discussions/story_discussion.md").write_text("")
    Path("output/story_output.md").write_text("")
    
    # Import orchestrator components
    from orchestrator import StoryOrchestrator
    from utils import SessionManager, CheckpointManager
    
    # Create orchestrator
    orchestrator = StoryOrchestrator()
    
    # Create mock responses
    orchestrator_responses = {
        "analyze": "Analysis: Library with books that change. Mystery tone. Dr. Chen as protagonist.\n\n[DONE]",
        "create": "Writer Prompt: Write about library.\nReader Prompt: Review as Dr. Chen.\n\n[DONE]",
        "decide": "SCP_WRITER",
        "who should respond": "SCP_WRITER",
        "evaluate": "NEEDS_WORK: No story written yet"
    }
    
    writer_responses = {
        "outline": """**Story Outline: The Index**

1. Opening: Dr. Chen finds unmarked library
2. Middle: Books change based on reader's memories  
3. Climax: Chen realizes the library writes HER
4. Theme: Identity and observation

[DONE]""",
        "begin writing": "I'll start writing the story now...",
        "story": """Dr. Chen pushed open the unmarked door...

[First page of story content]

[DONE]"""
    }
    
    reader_responses = {
        "review": "The outline is intriguing! I like the personal stakes. Proceed.\n\n[DONE]",
        "feedback": "Good start, but needs more atmosphere.\n\n[DONE]"
    }
    
    # Replace real agents with mocks
    orchestrator.orchestrator = MockAgent(
        "ORCHESTRATOR", 
        orchestrator_responses,
        orchestrator.agent_callback
    )
    orchestrator.orchestrator.set_checkpoint_manager = lambda x: None
    orchestrator.orchestrator.current_phase = "initialization"
    
    # Create mock writer and reader
    orchestrator.writer_agent = MockAgent(
        "SCP_WRITER",
        writer_responses,
        orchestrator.agent_callback
    )
    
    orchestrator.reader_agent = MockAgent(
        "READER", 
        reader_responses,
        orchestrator.agent_callback
    )
    
    # Manually run through the phases
    print("1. Starting outline phase...")
    orchestrator.current_phase = "outline"
    message = "SCP_WRITER: Please create your story outline.\n\n[DONE]"
    await orchestrator.orchestrator._append_to_discussion(message)
    orchestrator.pending_decision = True
    orchestrator.last_speaker = "ORCHESTRATOR"
    orchestrator.last_message = message
    
    # Process the decision
    print("\n2. Processing orchestrator decision...")
    await orchestrator.process_next_turn()
    
    # Check results
    print("\n3. Checking results...")
    discussion = Path("discussions/story_discussion.md").read_text()
    print(f"Discussion length: {len(discussion)} chars")
    print(f"Number of messages: {discussion.count('##')}")
    
    # Show agent call counts
    print("\n4. Agent activity:")
    print(f"  - Orchestrator calls: {orchestrator.orchestrator.call_count}")
    print(f"  - Writer calls: {orchestrator.writer_agent.call_count}")
    print(f"  - Reader calls: {orchestrator.reader_agent.call_count}")
    
    print("\n=== Mock Test Complete ===")


async def test_decision_flow():
    """Test just the decision flow logic."""
    print("\n\n=== Testing Decision Flow ===\n")
    
    # Test different message patterns
    test_cases = [
        ("WRITER", "Here's my outline", False),  # No [DONE]
        ("WRITER", "Here's my outline\n\n[DONE]", True),  # Has [DONE]
        ("READER", "Reviewing now...", False),
        ("READER", "Looks good! ---END---", True),  # Alternative marker
    ]
    
    from orchestrator import StoryOrchestrator
    orch = StoryOrchestrator()
    
    for agent, message, should_trigger in test_cases:
        await orch.agent_callback(agent, message)
        print(f"{agent}: '{message[:20]}...' -> pending={orch.pending_decision} (expected: {should_trigger})")
        assert orch.pending_decision == should_trigger, f"Failed for {agent}"
        orch.pending_decision = False  # Reset
    
    print("\n✓ All decision flow tests passed!")


async def main():
    """Run all mock tests."""
    await test_decision_flow()
    await test_full_orchestration()

if __name__ == "__main__":
    asyncio.run(main())