# SCP Writer - Multi-Agent Story Creation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Claude](https://img.shields.io/badge/Claude-Opus%204-purple.svg)](https://www.anthropic.com/claude)

A collaborative AI system that uses three specialized Claude agents to write narrative-style SCP stories with real-time web visualization.

## Overview

SCP Writer uses a conversation coordinator pattern with three AI agents working together:
- **Writer**: Creates story outlines and writes the narrative
- **Reader**: Provides feedback from the target audience perspective  
- **Expert**: Resolves disputes when Writer and Reader disagree

## What are SCP Stories?

SCP stories are fictional scientific reports about paranormal objects and entities, written in a clinical documentary style. The SCP Foundation is a collaborative fiction project where anomalies are documented as if by a secret organization dedicated to Securing, Containing, and Protecting humanity from the paranormal. [Learn more about the SCP format](https://en.wikipedia.org/wiki/SCP_Foundation).

## Features

- Simple conversation coordinator pattern for efficient agent handoffs
- Dynamic story configuration with flexible page limits (1-10 pages)
- Checkpoint system that adapts to story length
- Real-time streaming responses with Claude Opus 4
- Interactive mode for easy story configuration
- Optional progress monitoring with `--monitor` flag
- Automatic file cleanup on each run
- Narrative style (like "There Is No Antimemetics Division")
- **NEW**: Web interface with immersive SCP Foundation terminal theme
- **NEW**: Real-time visualization of agent collaboration
- **NEW**: WebSocket streaming for live story generation updates

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher (for web interface)
- Claude Code CLI installed and authenticated ([Install guide](https://docs.anthropic.com/en/docs/claude-code/quickstart))

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/scpwriter.git
cd scpwriter

# Set up environment (optional - for model configuration)
cp .env.example .env
# Edit .env to configure Claude model preference if desired
```

### Backend (Python)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r api/requirements.txt  # For web interface
```

### Frontend (Optional - for web interface)
```bash
cd frontend
npm install
```

## Usage

### Command Line Interface

```bash
# Interactive mode (recommended) - prompts for all parameters
python cli.py

# Run with a theme
python cli.py "A memetic hazard that spreads through dreams"

# Specify page limit
python cli.py --pages 5 "Your theme here"

# Enable progress monitoring
python cli.py --monitor "Your theme here"

# Combine options
python cli.py --pages 2 --monitor "A clock that runs backwards"
```

### Web Interface

1. Start the backend API:
```bash
source venv/bin/activate
python api/server.py
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm run dev
```

3. Open http://localhost:3000 in your browser

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
- `cli.py`: Command-line entry point with interactive mode
- `api/`: FastAPI backend for web interface
- `frontend/`: Next.js web interface with terminal aesthetic

## Configuration

### Authentication Setup

This project uses the Claude Code SDK, which handles authentication through the Claude Code CLI. To set up:

1. **Install Claude Code CLI:**
   ```bash
   pip install claude-code
   ```

2. **Authenticate with Claude:**
   ```bash
   claude-code auth login
   ```

### Model Selection
The AI model can be configured via the `CLAUDE_MODEL` environment variable in your `.env` file:

```bash
# In your .env file
CLAUDE_MODEL=claude-opus-4-20250514
```

Available models:
- `claude-opus-4-20250514` - Most powerful, best for complex tasks ($15/$75 per million tokens)
- `claude-sonnet-4-20250514` - Balanced performance and cost
- `claude-haiku-4-20250514` - Fastest and most cost-effective

Default: `claude-opus-4-20250514` (if not specified)

## How It Works

1. **Theme Input**: User provides a story concept or theme
2. **Orchestration**: Coordinator analyzes request and creates custom prompts
3. **Outline Creation**: Writer agent drafts story structure
4. **Review Process**: Reader agent reviews and approves outline
5. **Story Writing**: Writer develops narrative with checkpoint pauses
6. **Feedback Loop**: Reader provides guidance at checkpoints
7. **Quality Control**: Orchestrator ensures coherent conclusion
8. **Output**: Final story saved as markdown

## Example Output

```markdown
# SCP-████: The Temporal Mirror

## Discovery Log
The object was discovered in an abandoned warehouse in ████████...

## Description
SCP-████ appears to be an ornate Victorian-era mirror measuring...

## Containment Procedures
SCP-████ is to be kept in a sealed containment chamber...
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The SCP Foundation community for inspiration
- Anthropic for Claude API access
- Contributors and users of this project

## Support

- **Issues**: [Report bugs or request features](https://github.com/yourusername/scpwriter/issues)
- **Discussions**: [Ask questions or share ideas](https://github.com/yourusername/scpwriter/discussions)

## Roadmap

- [ ] Support for multiple story formats beyond SCP
- [ ] Integration with other LLM providers
- [ ] Collaborative multiplayer story creation
- [ ] Story revision and editing workflows
- [ ] Export to various formats (PDF, EPUB, etc.)