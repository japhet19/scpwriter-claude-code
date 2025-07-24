# SCP Writer - Multi-Agent Story Creation System

A collaborative AI system that uses three specialized Claude agents to write narrative-style SCP stories.

## Overview

SCP Writer orchestrates three AI agents working together:
- **Writing Expert/Orchestrator**: Manages the process and resolves disputes
- **SCP Writer**: Creates story outlines and writes the narrative
- **Reader**: Provides feedback from the target audience perspective

## Features

- Dynamic agent prompts based on story theme
- Checkpoint system at 1-page and 2-page marks
- Real-time collaboration through shared documents
- 3-page story limit with pacing management
- Narrative style (like "There Is No Antimemetics Division")

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run with a theme
python main.py "A memetic hazard that spreads through dreams"

# Interactive mode
python main.py

# Clean previous outputs
python main.py --clean "Your theme here"

# Run without progress monitoring
python main.py --no-monitor "Your theme here"
```

## Project Structure

- `agents/`: Agent implementations
- `utils/`: Supporting utilities
- `prompts/`: Agent prompt templates
- `discussions/`: Agent communication logs
- `output/`: Generated stories
- `orchestrator.py`: Main orchestration logic
- `main.py`: CLI entry point

## How It Works

1. User provides a story theme
2. Orchestrator analyzes request and creates custom prompts
3. Writer creates story outline
4. Reader reviews and approves outline
5. Writer begins story with checkpoint pauses
6. Reader provides feedback at checkpoints
7. Orchestrator ensures satisfying conclusion within 3 pages
8. Final story is saved to output directory