#!/usr/bin/env python3
"""Debug agent responses to understand empty responses."""

import asyncio
import logging
from pathlib import Path
from agents.base_agent import BaseAgent

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Patch BaseAgent to add debug logging
original_respond = BaseAgent.respond

async def debug_respond(self, trigger_message, include_output=False, skip_callback=False):
    """Patched respond method with debug logging."""
    print(f"\n{'='*60}")
    print(f"DEBUG: {self.name} responding")
    print(f"Trigger message: {trigger_message[:100]}...")
    print(f"System prompt: {self.system_prompt[:100]}...")
    print(f"Include output: {include_output}")
    print(f"{'='*60}\n")
    
    # Call original with debug
    try:
        from claude_code_sdk import query, ClaudeCodeOptions
        
        # Build context
        discussion_content = self._read_discussion_file()
        context = f"Current discussion:\n{discussion_content}"
        
        if include_output:
            output_content = self._read_output_file()
            context += f"\n\nCurrent story output:\n{output_content}"
        
        prompt = f"""
You are {self.name}. 

{context}

The latest message triggering your response:
{trigger_message}

Based on your role and the current context, provide an appropriate response.
Remember to check both the discussion file and (if relevant) the output file.
"""
        
        print(f"Full prompt length: {len(prompt)} chars")
        print(f"Context length: {len(context)} chars")
        
        # Create options
        options = ClaudeCodeOptions(
            append_system_prompt=self.system_prompt,
            cwd=Path(".").absolute(),
            allowed_tools=["Read", "Write", "Edit"],
            max_turns=1
        )
        
        print("\nQuerying Claude SDK...")
        response_text = ""
        message_count = 0
        
        async for message in query(prompt=prompt, options=options):
            message_count += 1
            class_name = message.__class__.__name__
            print(f"  Message {message_count}: {class_name}")
            
            if class_name == 'AssistantMessage' and hasattr(message, 'content'):
                if isinstance(message.content, list):
                    for i, block in enumerate(message.content):
                        print(f"    Block {i}: {block.__class__.__name__}")
                        if hasattr(block, 'text'):
                            print(f"    Text: {block.text[:100]}...")
                            response_text += block.text.strip() + "\n"
            elif hasattr(message, 'result'):
                print(f"  Result: {str(message.result)[:100]}...")
        
        print(f"\nFinal response text: {len(response_text)} chars")
        print(f"First 200 chars: {response_text[:200]}...")
        
        # Continue with original
        response = await original_respond(self, trigger_message, include_output, skip_callback)
        
        print(f"\nActual response returned: {len(response)} chars")
        return response
        
    except Exception as e:
        print(f"\nERROR in debug_respond: {e}")
        import traceback
        traceback.print_exc()
        raise

# Apply patch
BaseAgent.respond = debug_respond


async def test_scp_writer_issue():
    """Test why SCP Writer returns empty responses."""
    print("\n=== Testing SCP Writer Issue ===\n")
    
    # Clear files
    Path("discussions/story_discussion.md").write_text("")
    Path("output/story_output.md").write_text("")
    
    # Create writer with actual prompt from system
    writer_prompt = """You are an SCP Writer specializing in narrative-format stories.
Write a 3-page story about a mysterious library where books rewrite themselves.
When asked to create an outline, provide a detailed story outline."""
    
    writer = BaseAgent(
        name="SCP_WRITER",
        system_prompt=writer_prompt,
        orchestrator_callback=None
    )
    
    # Test with the actual trigger message
    trigger = """Based on the theme and requirements in your system prompt, create a detailed story outline.

Include:
1. Core Concept/Anomaly: What is the central anomalous element?
2. Main Character(s): Who are they and how do they relate to the anomaly?
3. Story Structure:
   - Beginning: How does the story open? What hooks the reader?
   - Middle: How does tension build? What is revealed?
   - End: What is the climax/resolution? Any twist?
4. Key Themes: What deeper ideas does the story explore?
5. Tone/Atmosphere: What feeling should readers have?

Write your outline in the discussion file. When complete, end your message with [DONE] to signal you're ready for feedback."""
    
    response = await writer.respond(trigger)
    
    print(f"\n\nFINAL RESULT:")
    print(f"Response length: {len(response)} chars")
    print(f"Response content:\n{response}")


async def main():
    """Run debug test."""
    await test_scp_writer_issue()

if __name__ == "__main__":
    asyncio.run(main())