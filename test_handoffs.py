#!/usr/bin/env python3
"""Test agent handoffs and measure response times."""

import asyncio
import time
import logging
from pathlib import Path
from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_simple_handoff():
    """Test a simple handoff between two agents."""
    print("\n=== Testing Simple Agent Handoff ===\n")
    
    # Clear discussion file
    Path("discussions/story_discussion.md").write_text("")
    
    # Track timings
    timings = []
    
    # Callback to track handoffs
    handoffs = []
    async def track_callback(agent_name, message):
        handoffs.append((agent_name, len(message), message[:50] + "..." if len(message) > 50 else message))
        print(f"\n✓ Callback from {agent_name}: {len(message)} chars")
    
    # Create first agent
    agent1 = BaseAgent(
        name="AGENT_1",
        system_prompt="You are Agent 1. When asked to start, respond with: 'Hello from Agent 1! I'm starting the process. [DONE]'",
        orchestrator_callback=track_callback
    )
    
    # Create second agent  
    agent2 = BaseAgent(
        name="AGENT_2",
        system_prompt="You are Agent 2. When you see a message from Agent 1, respond with: 'Hello from Agent 2! I received your message. [DONE]'",
        orchestrator_callback=track_callback
    )
    
    # Test first agent
    print("1. Testing Agent 1...")
    start = time.time()
    response1 = await agent1.respond("Please start the process.")
    elapsed1 = time.time() - start
    timings.append(("Agent 1", elapsed1))
    print(f"   Response: {response1}")
    print(f"   Time: {elapsed1:.2f}s")
    
    # Test second agent
    print("\n2. Testing Agent 2...")
    start = time.time()
    response2 = await agent2.respond("Agent 1 said hello. Please respond.")
    elapsed2 = time.time() - start
    timings.append(("Agent 2", elapsed2))
    print(f"   Response: {response2}")
    print(f"   Time: {elapsed2:.2f}s")
    
    # Show results
    print("\n=== Results ===")
    print(f"Total handoffs tracked: {len(handoffs)}")
    for agent, chars, preview in handoffs:
        print(f"  - {agent}: {chars} chars - {preview}")
    
    print(f"\nTotal time: {sum(t[1] for t in timings):.2f}s")
    for agent, elapsed in timings:
        print(f"  - {agent}: {elapsed:.2f}s")
    
    # Check discussion file
    discussion = Path("discussions/story_discussion.md").read_text()
    print(f"\nDiscussion file length: {len(discussion)} chars")
    print("First 200 chars:", discussion[:200])


async def test_scp_writer_prompt():
    """Test the SCP Writer with a simplified prompt."""
    print("\n\n=== Testing SCP Writer Directly ===\n")
    
    # Clear files
    Path("discussions/story_discussion.md").write_text("")
    Path("output/story_output.md").write_text("")
    
    # Create a simplified SCP writer
    writer = BaseAgent(
        name="SCP_WRITER",
        system_prompt="""You are an SCP Writer. When asked to create an outline, respond with a simple outline like:

**Story Outline: The Rewriting Library**

1. **Opening**: Dr. Chen discovers the library
2. **Middle**: Testing reveals books change per reader  
3. **Ending**: The library itself is alive

This outline explores identity and perception.

[DONE]""",
        orchestrator_callback=None
    )
    
    print("Testing SCP Writer with outline request...")
    start = time.time()
    response = await writer.respond("Please create a story outline about a library where books rewrite themselves.")
    elapsed = time.time() - start
    
    print(f"\nResponse received in {elapsed:.2f}s:")
    print(f"Length: {len(response)} chars")
    print(f"Content:\n{response}")
    
    if "[DONE]" in response:
        print("\n✓ Completion signal found")
    else:
        print("\n✗ No completion signal found")


async def main():
    """Run all tests."""
    await test_simple_handoff()
    await test_scp_writer_prompt()
    
    print("\n\n=== All Tests Complete ===")

if __name__ == "__main__":
    asyncio.run(main())