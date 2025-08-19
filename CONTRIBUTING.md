# Contributing to SCP Writer

Thank you for your interest in contributing to SCP Writer! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher (for the web interface)
- Claude Code CLI installed and authenticated

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/scpwriter.git
   cd scpwriter
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r api/requirements.txt  # For web interface backend
   ```

3. **Set up frontend (optional):**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Authenticate with Claude Code:**
   ```bash
   # Install Claude Code CLI if not already installed
   pip install claude-code
   
   # Authenticate with Claude
   claude-code auth login
   ```

5. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env to configure Claude model preference if desired
   ```

## Development Workflow

### Running the Project

**CLI Mode:**
```bash
python cli.py
```

**Web Interface:**
```bash
# Terminal 1: Start backend
python api/server.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Code Style

- **Python:** Follow PEP 8 guidelines
- **JavaScript/TypeScript:** Use the project's ESLint configuration
- **Commits:** Use clear, descriptive commit messages

### Testing

Before submitting a PR, ensure:
1. Your code runs without errors
2. Existing functionality isn't broken
3. New features include appropriate error handling

## Making Changes

### Workflow

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add: Description of your changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request on GitHub

### Pull Request Guidelines

- **Title:** Use a clear, descriptive title
- **Description:** Explain what changes you made and why
- **Screenshots:** Include screenshots for UI changes
- **Testing:** Describe how you tested your changes
- **Issues:** Reference any related issues

### Commit Message Format

We follow a simple format for commit messages:

```
Type: Brief description

Longer explanation if needed.
```

Types:
- `Add:` New feature or file
- `Fix:` Bug fix
- `Update:` Enhancement to existing feature
- `Remove:` Removed feature or file
- `Refactor:` Code refactoring
- `Docs:` Documentation changes

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Python and Node.js versions
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

### Feature Requests

We welcome feature suggestions! Please:
- Check existing issues first
- Explain the use case
- Describe your proposed solution
- Consider implementation complexity

### Code Contributions

Areas where we especially welcome contributions:
- New story generation features
- UI/UX improvements
- Performance optimizations
- Documentation improvements
- Bug fixes
- Test coverage

### Documentation

Help us improve:
- README clarity
- Code comments
- API documentation
- Usage examples

## Project Structure

```
scpwriter/
├── agents/          # AI agent implementations
├── api/            # FastAPI backend
├── frontend/       # Next.js web interface
├── prompts/        # Agent prompt templates
├── utils/          # Utility functions
├── cli.py          # CLI entry point
└── scp_coordinator.py  # Core orchestration logic
```

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in GitHub Discussions
- Reach out to maintainers

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to SCP Writer! 🚀