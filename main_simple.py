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


def print_header():
    """Print the application header."""
    print("\n" + "="*60)
    print("SCP WRITER - Multi-Agent Story Creation System")
    print("="*60)
    print("Creating narrative-style SCP stories through AI collaboration")
    print("Using simplified coordinator with direct agent handoffs")
    print("="*60 + "\n")


async def create_story(theme: str, page_limit: int = 3):
    """Create an SCP story with the given theme."""
    print(f"\nStarting story creation with theme: '{theme}'")
    print(f"Target length: {page_limit} pages (~{page_limit * 300} words)")
    print("\nFile locations:")
    print(f"  - Agent discussion: discussions/story_discussion.md")
    print(f"  - Final story: output/story_output.md")
    print("\nInitializing Writer, Reader, and Expert agents...")
    
    # Create coordinator with story configuration
    story_config = StoryConfig(page_limit=page_limit)
    coordinator = SCPCoordinator(story_config)
    
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
        "--clean",
        action="store_true",
        help="Clean output directories before starting"
    )
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Clean directories if requested
    if args.clean:
        print("Cleaning output files...")
        discussion_path = Path("discussions/story_discussion.md")
        output_path = Path("output/story_output.md")
        
        # Ensure directories exist
        discussion_path.parent.mkdir(exist_ok=True)
        output_path.parent.mkdir(exist_ok=True)
        
        # Clear files instead of deleting them
        discussion_path.write_text("", encoding='utf-8')
        output_path.write_text("", encoding='utf-8')
            
        print("✓ Files cleared")
        print(f"  - Discussion: {discussion_path}")
        print(f"  - Output: {output_path}\n")
    
    # Get theme from args or prompt
    if args.theme:
        theme = args.theme
    else:
        print("Enter the theme or concept for your SCP story.")
        print("Examples:")
        print("  - 'A library where books rewrite themselves based on who reads them'")
        print("  - 'A coffee shop where time moves differently for each customer'")
        print("  - 'An antimemetic entity that makes people forget their loved ones'")
        print()
        theme = input("Theme: ").strip()
        
        if not theme:
            print("❌ Error: Theme cannot be empty")
            sys.exit(1)
    
    # Run the async story creation
    try:
        asyncio.run(create_story(theme, page_limit=args.pages))
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    
    print("\nThank you for using SCP Writer!")


if __name__ == "__main__":
    main()