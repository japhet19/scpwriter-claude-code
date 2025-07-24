#!/usr/bin/env python3
"""Test robust multi-agent conversation with flexible handoffs."""

import asyncio
import re
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime

from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConversationCoordinator:
    """Coordinates conversation between multiple agents."""
    
    def __init__(self, agents: Dict[str, BaseAgent]):
        self.agents = agents
        self.conversation_history = []
        self.current_speaker = None
        self.turn_count = 0
        self.max_turns = 20
        
    def parse_next_speaker(self, message: str) -> Optional[str]:
        """Extract who should speak next from a message."""
        # Look for patterns like [@Alice], [Next: Bob], [Charlie's turn], etc.
        patterns = [
            r'\[@(\w+)\]',  # [@Alice]
            r'\[Next:\s*(\w+)\]',  # [Next: Bob]
            r'\[(\w+)\'s turn\]',  # [Alice's turn]
            r'\[(\w+),\s*your turn\]',  # [Bob, your turn]
            r'@(\w+)',  # @Charlie
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                name = match.group(1)
                # Normalize the name
                for agent_name in self.agents.keys():
                    if agent_name.lower() == name.lower():
                        return agent_name
        
        return None
    
    async def run_conversation(self, opening_speaker: str, opening_prompt: str):
        """Run a multi-agent conversation."""
        logger.info(f"Starting conversation with {opening_speaker}")
        
        self.current_speaker = opening_speaker
        current_prompt = opening_prompt
        
        while self.turn_count < self.max_turns:
            self.turn_count += 1
            
            # Get current agent
            if self.current_speaker not in self.agents:
                logger.error(f"Unknown speaker: {self.current_speaker}")
                break
            
            agent = self.agents[self.current_speaker]
            
            # Get response
            logger.info(f"\n--- Turn {self.turn_count}: {self.current_speaker} speaking ---")
            start_time = time.time()
            
            try:
                response = await asyncio.wait_for(
                    agent.respond(current_prompt, skip_callback=True),
                    timeout=60.0  # 60 second timeout
                )
                elapsed = time.time() - start_time
                logger.info(f"{self.current_speaker} responded in {elapsed:.1f}s")
                
            except asyncio.TimeoutError:
                logger.error(f"{self.current_speaker} timed out!")
                response = f"[{self.current_speaker} timed out - ending conversation]"
                break
            
            # Log the response
            self.conversation_history.append({
                "turn": self.turn_count,
                "speaker": self.current_speaker,
                "prompt": current_prompt,
                "response": response,
                "time": elapsed
            })
            
            print(f"\n{self.current_speaker}: {response}\n")
            
            # Parse next speaker
            next_speaker = self.parse_next_speaker(response)
            
            if not next_speaker:
                logger.info("No next speaker indicated - ending conversation")
                break
            
            if next_speaker == self.current_speaker:
                logger.warning(f"{self.current_speaker} tried to speak again - preventing loop")
                # Pick someone else
                next_speaker = [name for name in self.agents if name != self.current_speaker][0]
            
            # Prepare for next turn
            self.current_speaker = next_speaker
            current_prompt = f"{agent.name} said: {response}\n\nIt's your turn to respond."
        
        logger.info(f"\nConversation ended after {self.turn_count} turns")
        self.print_summary()
    
    def print_summary(self):
        """Print conversation summary."""
        print("\n" + "="*60)
        print("CONVERSATION SUMMARY")
        print("="*60)
        
        total_time = sum(turn["time"] for turn in self.conversation_history)
        print(f"Total turns: {len(self.conversation_history)}")
        print(f"Total time: {total_time:.1f}s")
        print(f"Average time per turn: {total_time/len(self.conversation_history):.1f}s")
        
        speaker_stats = {}
        for turn in self.conversation_history:
            speaker = turn["speaker"]
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {"count": 0, "total_time": 0}
            speaker_stats[speaker]["count"] += 1
            speaker_stats[speaker]["total_time"] += turn["time"]
        
        print("\nSpeaker statistics:")
        for speaker, stats in speaker_stats.items():
            avg_time = stats["total_time"] / stats["count"]
            print(f"  {speaker}: {stats['count']} turns, avg {avg_time:.1f}s/turn")


async def test_casual_conversation():
    """Test a casual conversation between three agents."""
    
    # Clear discussion file
    Path("discussions/story_discussion.md").write_text("")
    
    # Create three agents with distinct personalities
    alice = BaseAgent(
        name="Alice",
        system_prompt="""You are Alice, a friendly and curious person who loves asking questions.
        
When you speak:
- Be warm and enthusiastic
- Ask interesting questions to keep conversation flowing
- Always indicate who should speak next using [@Name] format
- Try to include everyone in the conversation
- Keep responses concise (2-3 sentences max)""",
        orchestrator_callback=None
    )
    
    bob = BaseAgent(
        name="Bob", 
        system_prompt="""You are Bob, a technical expert who enjoys explaining things.
        
When you speak:
- Give informative but concise answers
- Share interesting technical facts
- Always indicate who should speak next using [@Name] format
- Be helpful but not condescending
- Keep responses concise (2-3 sentences max)""",
        orchestrator_callback=None
    )
    
    charlie = BaseAgent(
        name="Charlie",
        system_prompt="""You are Charlie, a thoughtful mediator who helps conversations flow.
        
When you speak:
- Acknowledge what others have said
- Bridge between different topics smoothly
- Always indicate who should speak next using [@Name] format
- Keep the conversation balanced between all participants
- Keep responses concise (2-3 sentences max)""",
        orchestrator_callback=None
    )
    
    # Create coordinator
    agents = {"Alice": alice, "Bob": bob, "Charlie": charlie}
    coordinator = ConversationCoordinator(agents)
    
    # Start conversation
    opening_prompt = """We're having a casual conversation about technology and creativity. 
    Please introduce yourself briefly and share something interesting, then pass the conversation 
    to one of the others using [@Name] format."""
    
    await coordinator.run_conversation("Alice", opening_prompt)


async def test_decision_making_conversation():
    """Test a conversation where agents need to make a group decision."""
    
    # Clear discussion file  
    Path("discussions/story_discussion.md").write_text("")
    
    # Create three agents with decision-making roles
    leader = BaseAgent(
        name="Leader",
        system_prompt="""You are the team leader trying to reach a group decision.
        
When you speak:
- Summarize different viewpoints
- Guide toward consensus
- Ask for specific input when needed
- Always indicate who should speak next using [Next: Name] format
- Keep responses focused (2-3 sentences max)
- If everyone has spoken at least once, you can end with [Conversation complete]""",
        orchestrator_callback=None
    )
    
    analyst = BaseAgent(
        name="Analyst",
        system_prompt="""You are the analyst who provides data-driven insights.
        
When you speak:
- Share relevant facts and analysis
- Point out potential risks or benefits
- Be objective and balanced
- Always indicate who should speak next using [Next: Name] format
- Keep responses concise with key points""",
        orchestrator_callback=None
    )
    
    creative = BaseAgent(
        name="Creative",
        system_prompt="""You are the creative thinker who suggests innovative solutions.
        
When you speak:
- Propose creative alternatives
- Think outside the box
- Build on others' ideas
- Always indicate who should speak next using [Next: Name] format
- Keep responses imaginative but practical""",
        orchestrator_callback=None
    )
    
    # Create coordinator
    agents = {"Leader": leader, "Analyst": analyst, "Creative": creative}
    coordinator = ConversationCoordinator(agents)
    
    # Start conversation
    opening_prompt = """Our team needs to decide how to improve our office environment. 
    We have a budget of $10,000. Please share your initial thoughts and then pass to another team member."""
    
    await coordinator.run_conversation("Leader", opening_prompt)


async def main():
    """Run conversation tests."""
    print("\n" + "="*60)
    print("MULTI-AGENT CONVERSATION TEST")
    print("="*60)
    
    print("\n1. Testing casual conversation...")
    await test_casual_conversation()
    
    print("\n\n2. Testing decision-making conversation...")
    await test_decision_making_conversation()
    
    print("\n\nAll tests complete!")


if __name__ == "__main__":
    asyncio.run(main())