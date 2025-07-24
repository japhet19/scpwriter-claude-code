#!/usr/bin/env python3
"""
SCP Writer - Simplified Multi-Agent Story Creation System
Uses ConversationCoordinator pattern for efficient agent collaboration.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

from scp_coordinator import SCPCoordinator, StoryConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def monitor_progress(coordinator: SCPCoordinator):
    """Monitor and display progress during story creation."""
    while coordinator.turn_count < coordinator.max_turns and not coordinator.story_complete:
        # Wait a bit before checking status
        await asyncio.sleep(5)
        
        # Display basic status
        print(f"\n--- Progress Update ---")
        print(f"Turn: {coordinator.turn_count}/{coordinator.max_turns}")
        print(f"Current Phase: {coordinator.current_phase}")
        print(f"Current Speaker: {coordinator.current_speaker}")
        
        # Check story progress if available
        story_content = coordinator.extract_story_from_discussion()
        if story_content:
            word_count = len(story_content.split())
            pages = word_count / 300
            print(f"Story Progress: {word_count} words ({pages:.1f} pages)")
        
        # Check discussion file for recent activity
        discussion_path = Path("discussions/story_discussion.md")
        if discussion_path.exists():
            lines = discussion_path.read_text(encoding='utf-8', errors='replace').splitlines()
            if lines:
                # Find last non-empty line
                for line in reversed(lines):
                    if line.strip():
                        print(f"Latest activity: {line[:80]}...")
                        break


def print_header():
    """Print the application header."""
    print("\n" + "="*60)
    print("SCP WRITER - Multi-Agent Story Creation System")
    print("="*60)
    print("Creating narrative-style SCP stories through AI collaboration")
    print("Using simplified coordinator with direct agent handoffs")
    print("="*60 + "\n")


async def create_story(theme: str, page_limit: int = 3, show_monitor: bool = False, protagonist_name: str = None):
    """Create an SCP story with the given theme."""
    print(f"\nStarting story creation with theme: '{theme}'")
    print(f"Target length: {page_limit} pages (~{page_limit * 300} words)")
    print("\nFile locations:")
    print(f"  - Agent discussion: discussions/story_discussion.md")
    print(f"  - Final story: output/story_output.md")
    print("\nInitializing Writer, Reader, and Expert agents...")
    
    # Create coordinator with story configuration
    story_config = StoryConfig(page_limit=page_limit, protagonist_name=protagonist_name)
    coordinator = SCPCoordinator(story_config)
    
    # Start progress monitoring if requested
    monitor_task = None
    if show_monitor:
        print("\nProgress monitoring enabled. Updates will appear every 5 seconds.")
        monitor_task = asyncio.create_task(monitor_progress(coordinator))
    
    try:
        # Run story creation
        await coordinator.run_story_creation(theme)
        
        print("\n" + "="*60)
        print("STORY CREATION COMPLETE!")
        print("="*60)
        
        # Display final story
        output_path = Path("output/story_output.md")
        if output_path.exists():
            content = output_path.read_text()
            word_count = len(content.split())
            print(f"\n✓ Story saved to: {output_path}")
            print(f"  Word count: {word_count} words ({word_count/300:.1f} pages)")
            
            # Display the story
            if word_count > 0:
                try:
                    if input("\nWould you like to read the story now? (y/n): ").lower() == 'y':
                        print("\n" + "="*60)
                        print("FINAL STORY")
                        print("="*60)
                        print(content)
                        print("="*60)
                except (EOFError, KeyboardInterrupt):
                    pass  # Skip if running in non-interactive mode
        else:
            print("\n⚠️  No story file was generated")
                
    except KeyboardInterrupt:
        print("\n\nStopping story creation...")
        
    except Exception as e:
        logger.error(f"Error during story creation: {e}")
        print(f"\n❌ Error: {e}")
        
    finally:
        # Cancel monitor task if running
        if monitor_task:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
                
        # Show discussion log if requested
        discussion_path = Path("discussions/story_discussion.md")
        if discussion_path.exists():
            try:
                if input("\nView agent discussion? (y/n): ").lower() == 'y':
                    print("\n" + "="*60)
                    print("AGENT DISCUSSION LOG")
                    print("="*60)
                    print(discussion_path.read_text())
            except (EOFError, KeyboardInterrupt):
                pass  # Skip if running in non-interactive mode


def main():
    """Main entry point for the SCP Writer."""
    parser = argparse.ArgumentParser(
        description="SCP Writer - Create SCP stories using multiple AI agents"
    )
    
    parser.add_argument(
        "theme",
        nargs="?",
        help="The theme or concept for the SCP story"
    )
    
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Target page limit for the story (default: 3)"
    )
    
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Show progress monitoring during story creation"
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Always clean files for fresh start
    print("Preparing fresh workspace...")
    discussion_path = Path("discussions/story_discussion.md")
    output_path = Path("output/story_output.md")
    
    # Ensure directories exist
    discussion_path.parent.mkdir(exist_ok=True)
    output_path.parent.mkdir(exist_ok=True)
    
    # Clear files
    discussion_path.write_text("", encoding='utf-8')
    output_path.write_text("", encoding='utf-8')
        
    print("✓ Files cleared")
    print(f"  - Discussion: {discussion_path}")
    print(f"  - Output: {output_path}\n")
    
    # Get parameters from args or interactive mode
    if args.theme:
        theme = args.theme
        page_limit = args.pages
        show_monitor = args.monitor
        protagonist_name = None  # No protagonist name from command line yet
    else:
        # Interactive mode - collect all parameters
        print("Welcome to SCP Writer interactive mode!")
        print("\nI'll help you create an SCP story. Let me ask you a few questions.\n")
        
        # Get theme
        print("What's the theme or concept for your SCP story?")
        print("Examples:")
        print("  - 'A library where books rewrite themselves based on who reads them'")
        print("  - 'A coffee shop where time moves differently for each customer'")
        print("  - 'An antimemetic entity that makes people forget their loved ones'")
        print()
        theme = input("Theme: ").strip()
        
        if not theme:
            print("❌ Error: Theme cannot be empty")
            sys.exit(1)
            
        # Get page limit
        print(f"\nHow many pages should the story be? (default: 3)")
        page_input = input("Pages [1-10]: ").strip()
        if page_input and page_input.isdigit():
            page_limit = min(max(int(page_input), 1), 10)  # Clamp between 1-10
        else:
            page_limit = 3
            
        # Get optional protagonist name
        print(f"\nWould you like to specify a protagonist name? (optional)")
        print("Leave blank for AI to create a unique character")
        protagonist_name = input("Protagonist name: ").strip()
            
        # Get monitor preference
        print(f"\nWould you like to see progress monitoring during creation?")
        monitor_input = input("Enable monitoring? (y/N): ").strip().lower()
        show_monitor = monitor_input in ['y', 'yes']
        
        # Show summary
        print("\n" + "="*60)
        print("STORY CONFIGURATION")
        print("="*60)
        print(f"Theme: {theme}")
        print(f"Target length: {page_limit} pages (~{page_limit * 300} words)")
        if protagonist_name:
            print(f"Protagonist: {protagonist_name}")
        else:
            print(f"Protagonist: AI will create unique character")
        print(f"Progress monitoring: {'Enabled' if show_monitor else 'Disabled'}")
        print("="*60)
        
        # Confirm
        if input("\nProceed with story creation? (Y/n): ").strip().lower() in ['n', 'no']:
            print("Story creation cancelled.")
            sys.exit(0)
    
    # Run the async story creation
    try:
        asyncio.run(create_story(theme, page_limit=page_limit, show_monitor=show_monitor, protagonist_name=protagonist_name))
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    
    print("\nThank you for using SCP Writer!")


if __name__ == "__main__":
    main()