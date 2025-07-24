# SCP Writer Frontend

A terminal-themed web interface for the SCP Writer multi-agent story generation system.

## Features

- **Immersive Terminal Experience**: Complete with CRT effects, scanlines, and glitch animations
- **Real-time Agent Visualization**: Watch Writer, Reader, and Expert agents collaborate in real-time
- **Interactive Story Configuration**: Configure story parameters with a retro-futuristic interface
- **WebSocket Streaming**: Live updates as the story is being generated
- **SCP Foundation Theming**: Authentic SCP document styling with classification stamps

## Tech Stack

- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Socket.io** for WebSocket communication
- **Howler.js** for sound effects

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Backend Requirements

The frontend requires the FastAPI backend to be running on port 8000:

```bash
cd ../api
source ../venv/bin/activate
python main.py
```

## Project Structure

```
src/
├── app/              # Next.js app directory
├── components/       # React components
│   ├── Terminal/     # Main terminal container
│   ├── BootSequence/ # Landing page boot animation
│   └── StoryConfig/  # Story configuration form
├── hooks/           # Custom React hooks
│   └── useWebSocket # WebSocket connection management
└── styles/          # Global styles
    └── terminal.css # Terminal theme styles
```

## Components

### Terminal
The main container that provides the CRT monitor aesthetic with:
- Scanline effects
- Random flicker animation
- Header with real-time UTC clock
- Green phosphor glow effects

### BootSequence
Landing page animation that simulates a terminal boot sequence:
- ASCII art SCP logo
- Progressive loading messages
- Animated progress bar

### StoryConfig
Interactive form for story configuration:
- Theme/anomaly description input
- Page length selection (1-10 pages)
- Optional protagonist name with generator
- Horror level slider
- Redaction toggle

## Customization

### Colors
Edit CSS variables in `terminal.css`:
```css
:root {
  --terminal-green: #00ff00;
  --terminal-amber: #ffb000;
  --terminal-red: #ff0040;
  --terminal-bg: #0a0a0a;
}
```

### Sound Effects
Place sound files in `public/sounds/`:
- `boot.mp3` - System startup
- `keypress.mp3` - Typing sounds
- `alert.mp3` - Notifications
- `success.mp3` - Story completion

## Future Enhancements

- [ ] Three.js anomaly visualizations
- [ ] Story archive with search
- [ ] User profiles and clearance levels
- [ ] Redaction tool for generated stories
- [ ] Export to PDF with SCP formatting
- [ ] VR mode for immersive reading

## Development

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load fonts.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.