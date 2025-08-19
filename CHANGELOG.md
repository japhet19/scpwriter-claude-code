# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-18

### Added
- Initial release of SCP Writer
- Multi-agent collaborative story generation system
- Three specialized Claude agents (Writer, Reader, Expert)
- Command-line interface with interactive mode
- Web interface with SCP Foundation terminal theme
- Real-time WebSocket streaming for story generation
- Configurable story length (1-10 pages)
- Dynamic checkpoint system based on story length
- Progress monitoring with `--monitor` flag
- Automatic file cleanup on each run
- Environment-based model configuration
- MIT License

### Features
- Narrative-style SCP story generation
- Custom theme/concept input
- Story outline creation and review process
- Quality control through agent collaboration
- Markdown output format
- FastAPI backend with WebSocket support
- Next.js frontend with terminal aesthetic

### Technical
- Python 3.8+ support
- Node.js 18+ support for web interface
- Claude Opus 4 integration via Claude Code SDK
- Configurable AI model selection
- Virtual environment support
- Comprehensive documentation

## [Unreleased]

### Planned
- Support for multiple story formats beyond SCP
- Integration with other LLM providers
- Collaborative multiplayer story creation
- Story revision and editing workflows
- Export to various formats (PDF, EPUB, etc.)
- Unit and integration tests
- Docker containerization
- Enhanced error handling and recovery

---

For a complete list of changes, see the [commit history](https://github.com/yourusername/scpwriter/commits/main).