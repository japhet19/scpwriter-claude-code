# SCP Writer - Multi-Agent Story Creation System

A collaborative AI system that uses three specialized Claude agents to write narrative-style SCP stories.

## Overview

SCP Writer uses a conversation coordinator pattern with three AI agents working together:
- **Writer**: Creates story outlines and writes the narrative
- **Reader**: Provides feedback from the target audience perspective  
- **Expert**: Resolves disputes when Writer and Reader disagree

## Features

- Simple conversation coordinator pattern for efficient agent handoffs
- Dynamic story configuration with flexible page limits (1-10 pages)
- Checkpoint system that adapts to story length
- Real-time streaming responses with Claude Sonnet 4
- Interactive mode for easy story configuration
- Optional progress monitoring with `--monitor` flag
- Automatic file cleanup on each run
- Narrative style (like "There Is No Antimemetics Division")

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Interactive mode (recommended) - prompts for all parameters
python main.py

# Run with a theme
python main.py "A memetic hazard that spreads through dreams"

# Specify page limit
python main.py --pages 5 "Your theme here"

# Enable progress monitoring
python main.py --monitor "Your theme here"

# Combine options
python main.py --pages 2 --monitor "A clock that runs backwards"
```

### Interactive Mode

When run without arguments, SCP Writer will guide you through setup:
1. Enter your story theme/concept
2. Choose page length (1-10 pages, default: 3)
3. Enable/disable progress monitoring
4. Confirm settings before starting

Files are automatically cleared on each run for a fresh start.

## Project Structure

- `agents/`: Agent implementations with Claude Code SDK integration
- `utils/`: Supporting utilities (text sanitization, checkpoints, etc.)
- `prompts/`: Agent prompt templates
- `discussions/`: Agent communication logs
- `output/`: Generated stories
- `scp_coordinator.py`: Conversation coordinator implementation
- `main.py`: Entry point with interactive mode

## How It Works

1. User provides a story theme
2. Orchestrator analyzes request and creates custom prompts
3. Writer creates story outline
4. Reader reviews and approves outline
5. Writer begins story with checkpoint pauses
6. Reader provides feedback at checkpoints
7. Orchestrator ensures satisfying conclusion within 3 pages
8. Final story is saved to output directory