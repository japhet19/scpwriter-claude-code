#!/usr/bin/env python3
"""Test the flexible page limit configuration."""

import asyncio
from scp_coordinator import StoryConfig, SCPCoordinator

async def test_story_config():
    """Test StoryConfig with different page limits."""
    
    print("Testing StoryConfig...")
    
    # Test different page limits
    configs = [
        StoryConfig(page_limit=1),
        StoryConfig(page_limit=3),
        StoryConfig(page_limit=5),
        StoryConfig(page_limit=10),
    ]
    
    for config in configs:
        print(f"\nPage Limit: {config.page_limit}")
        print(f"  Total Words: {config.total_words}")
        print(f"  Checkpoint 1: {config.checkpoint_1_words} words")
        print(f"  Checkpoint 2: {config.checkpoint_2_words} words")
        print(f"  Scope Guidance: {config.get_scope_guidance()}")

async def test_outline_evaluation():
    """Test outline complexity evaluation."""
    
    print("\n\nTesting Outline Evaluation...")
    
    coordinator = SCPCoordinator(StoryConfig(page_limit=3))
    
    # Simple outline
    simple_outline = """
    Story Outline: The Mirror
    - Opening: Dr. Chen finds a strange mirror
    - Middle: Mirror shows alternate realities
    - End: Chen must choose which reality to keep
    
    Main character: Dr. Chen
    Single location: Foundation lab
    """
    
    # Complex outline  
    complex_outline = """
    Story Outline: The Bibliotheca Vitae
    
    Characters: Dr. Chen, Marcus Wright, The Proprietor, Dr. Martinez, Lily Chen
    
    Part 1: Discovery
    - Scene 1: Chen finds coffee mug
    - Scene 2: Bookstore discovery
    - Scene 3: First reading of journal
    
    Part 2: Investigation  
    - Scene 4: Meeting Wright
    - Scene 5: Warehouse of unfinished books
    - Scene 6: Pattern discovery
    
    Part 3: Revelation
    - Scene 7: Page 67 transformation
    - Scene 8: The arithmetic of loss
    - Scene 9: Wright's confession
    
    Part 4: Choice
    - Scene 10: Final confrontation
    - Scene 11: The 713 bells
    
    Multiple detailed plot threads with page-by-page progression...
    """
    
    # Test evaluations
    for outline, name in [(simple_outline, "Simple"), (complex_outline, "Complex")]:
        ok, msg = coordinator.evaluate_outline_scope(outline)
        print(f"\n{name} Outline: {'OK' if ok else 'TOO COMPLEX'}")
        print(f"  {msg}")

async def main():
    """Run all tests."""
    await test_story_config()
    await test_outline_evaluation()
    print("\n\nAll tests complete!")

if __name__ == "__main__":
    asyncio.run(main())