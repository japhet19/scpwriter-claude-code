#!/usr/bin/env python3
"""
SCP Writer - Multi-Agent Story Creation System
A collaborative AI system that uses three specialized agents to write SCP stories.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from orchestrator import StoryOrchestrator

# Configure logging for main
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
    print("="*60 + "\n")


def print_status(status: dict):
    """Print the current system status."""
    print("\n--- System Status ---")
    print(f"Running: {status.get('is_running', False)}")
    print(f"Phase: {status.get('current_phase', 'Unknown')}")
    print(f"Story Complete: {status.get('story_complete', False)}")
    
    if status.get('progress'):
        progress = status['progress']
        print(f"\n--- Story Progress ---")
        print(f"Pages: {progress.get('current_pages', 0):.2f} / 3.00")
        print(f"Words: {progress.get('current_words', 0)}")
        print(f"Remaining: {progress.get('remaining_words', 0)} words")
        
    if status.get('sessions'):
        sessions = status['sessions']
        print(f"\n--- Active Agents ---")
        for agent in sessions.get('agents', []):
            print(f"  - {agent}")


async def monitor_progress(orchestrator: StoryOrchestrator):
    """Monitor and display progress during story creation."""
    while orchestrator.is_running:
        # Wait a bit before checking status
        await asyncio.sleep(5)
        
        # Get and display status
        status = orchestrator.get_status()
        print_status(status)
        
        # Check discussion file for recent activity
        discussion_path = Path("discussions/story_discussion.md")
        if discussion_path.exists():
            lines = discussion_path.read_text().splitlines()
            if lines:
                print(f"\nLatest discussion entry: {lines[-1][:80]}...")


async def create_story(theme: str, show_discussion: bool = True):
    """Create an SCP story with the given theme."""
    print(f"\nStarting story creation with theme: '{theme}'")
    print("Agents are initializing...\n")
    
    # Create orchestrator
    orchestrator = StoryOrchestrator()
    
    # Start progress monitoring if requested
    monitor_task = None
    if show_discussion:
        monitor_task = asyncio.create_task(monitor_progress(orchestrator))
    
    try:
        # Run story creation
        await orchestrator.run_story_creation(theme)
        
        # Get final status
        final_status = orchestrator.get_status()
        print("\n" + "="*60)
        print("STORY CREATION COMPLETE!")
        print("="*60)
        print_status(final_status)
        
        # Display final story location
        output_path = Path("output/story_output.md")
        if output_path.exists():
            print(f"\n✓ Story saved to: {output_path}")
            print(f"  Word count: {len(output_path.read_text().split())} words")
            
            # Optionally display the story
            if input("\nWould you like to read the story now? (y/n): ").lower() == 'y':
                print("\n" + "="*60)
                print("FINAL STORY")
                print("="*60)
                print(output_path.read_text())
                print("="*60)
                
    except KeyboardInterrupt:
        print("\n\nStopping story creation...")
        orchestrator.is_running = False
        
    except Exception as e:
        logger.error(f"Error during story creation: {e}")
        print(f"\n❌ Error: {e}")
        
    finally:
        # Cancel monitor task if running
        if monitor_task:
            monitor_task.cancel()
            
        # Show discussion log if requested
        if show_discussion:
            discussion_path = Path("discussions/story_discussion.md")
            if discussion_path.exists() and input("\nView full agent discussion? (y/n): ").lower() == 'y':
                print("\n" + "="*60)
                print("AGENT DISCUSSION LOG")
                print("="*60)
                print(discussion_path.read_text())


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
        "--no-monitor",
        action="store_true",
        help="Don't show progress monitoring during creation"
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
        print("Cleaning output directories...")
        discussion_path = Path("discussions/story_discussion.md")
        output_path = Path("output/story_output.md")
        
        if discussion_path.exists():
            discussion_path.unlink()
        if output_path.exists():
            output_path.unlink()
            
        print("✓ Directories cleaned\n")
    
    # Get theme from args or prompt
    if args.theme:
        theme = args.theme
    else:
        print("Enter the theme or concept for your SCP story.")
        print("Examples:")
        print("  - 'An antimemetic entity that makes people forget their loved ones'")
        print("  - 'A temporal anomaly in a small town diner'")
        print("  - 'A reality-bending artist whose paintings come alive'")
        print()
        theme = input("Theme: ").strip()
        
        if not theme:
            print("❌ Error: Theme cannot be empty")
            sys.exit(1)
    
    # Run the async story creation
    try:
        asyncio.run(create_story(theme, show_discussion=not args.no_monitor))
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    
    print("\nThank you for using SCP Writer!")


if __name__ == "__main__":
    main()