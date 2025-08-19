'use client'

import { useState, useEffect } from 'react'
import Terminal from '@/components/Terminal/Terminal'
import BootSequence from '@/components/BootSequence/BootSequence'
import StoryConfig, { StoryConfiguration } from '@/components/StoryConfig/StoryConfig'
import MessageTabs from '@/components/MessageTabs/MessageTabs'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Howl } from 'howler'

// Define sound effects
const sounds = {
  boot: new Howl({ src: ['/sounds/boot.mp3'], volume: 0.3 }),
  keypress: new Howl({ src: ['/sounds/keypress.mp3'], volume: 0.1 }),
  alert: new Howl({ src: ['/sounds/alert.mp3'], volume: 0.4 }),
  success: new Howl({ src: ['/sounds/success.mp3'], volume: 0.3 }),
}

export default function Home() {
  const [showBoot, setShowBoot] = useState(true)
  const [currentView, setCurrentView] = useState<'config' | 'generation' | 'complete'>('config')
  const [generatedStory, setGeneratedStory] = useState<string | null>(null)
  
  const {
    isConnected,
    connect,
    generateStory,
    messages,
    isGenerating,
    currentAgent,
    currentPhase,
    agentStates,
    currentActivity
  } = useWebSocket()

  useEffect(() => {
    // Connect to WebSocket when component mounts
    connect()
  }, [connect])

  const handleBootComplete = () => {
    setShowBoot(false)
    // sounds.boot.play()
  }

  const handleStorySubmit = (config: StoryConfiguration) => {
    if (!isConnected) {
      alert('Not connected to server. Please refresh and try again.')
      return
    }
    
    generateStory({
      theme: config.theme,
      pages: config.pages,
      protagonist: config.protagonist
    })
    
    setCurrentView('generation')
    // sounds.alert.play()
  }

  // Monitor for story completion
  useEffect(() => {
    const completedMessage = messages.find(msg => msg.type === 'completed')
    if (completedMessage && completedMessage.story) {
      setGeneratedStory(completedMessage.story)
      setCurrentView('complete')
      // sounds.success.play()
    }
  }, [messages])

  if (showBoot) {
    return (
      <Terminal showHeader={false}>
        <BootSequence onComplete={handleBootComplete} />
      </Terminal>
    )
  }

  return (
    <Terminal>
      {currentView === 'config' && (
        <StoryConfig onSubmit={handleStorySubmit} />
      )}
      
      {currentView === 'generation' && (
        <div className="generation-view">
          <div className="matrix-rain">
            <div className="matrix-column matrix-column-1">
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
            </div>
            <div className="matrix-column matrix-column-2">
              <span className="matrix-char">█</span>
              <span className="matrix-char">▓</span>
              <span className="matrix-char">▒</span>
              <span className="matrix-char">░</span>
              <span className="matrix-char">█</span>
              <span className="matrix-char">▓</span>
              <span className="matrix-char">▒</span>
            </div>
            <div className="matrix-column matrix-column-3">
              <span className="matrix-char">S</span>
              <span className="matrix-char">C</span>
              <span className="matrix-char">P</span>
              <span className="matrix-char">-</span>
              <span className="matrix-char">X</span>
              <span className="matrix-char">X</span>
              <span className="matrix-char">X</span>
            </div>
            <div className="matrix-column matrix-column-4">
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
            </div>
            <div className="matrix-column matrix-column-5">
              <span className="matrix-char">▲</span>
              <span className="matrix-char">▼</span>
              <span className="matrix-char">◆</span>
              <span className="matrix-char">◇</span>
              <span className="matrix-char">●</span>
              <span className="matrix-char">○</span>
            </div>
            <div className="matrix-column matrix-column-6">
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
            </div>
            <div className="matrix-column matrix-column-7">
              <span className="matrix-char">█</span>
              <span className="matrix-char">▓</span>
              <span className="matrix-char">▒</span>
              <span className="matrix-char">░</span>
              <span className="matrix-char">█</span>
            </div>
            <div className="matrix-column matrix-column-8">
              <span className="matrix-char">K</span>
              <span className="matrix-char">E</span>
              <span className="matrix-char">T</span>
              <span className="matrix-char">E</span>
              <span className="matrix-char">R</span>
            </div>
            <div className="matrix-column matrix-column-9">
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">1</span>
            </div>
            <div className="matrix-column matrix-column-10">
              <span className="matrix-char">▲</span>
              <span className="matrix-char">▼</span>
              <span className="matrix-char">◆</span>
              <span className="matrix-char">◇</span>
            </div>
            <div className="matrix-column matrix-column-11">
              <span className="matrix-char">0</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">1</span>
              <span className="matrix-char">0</span>
              <span className="matrix-char">0</span>
            </div>
            <div className="matrix-column matrix-column-12">
              <span className="matrix-char">█</span>
              <span className="matrix-char">▓</span>
              <span className="matrix-char">▒</span>
              <span className="matrix-char">░</span>
            </div>
            <div className="matrix-column matrix-column-13">
              <span className="matrix-char">E</span>
              <span className="matrix-char">U</span>
              <span className="matrix-char">C</span>
              <span className="matrix-char">L</span>
              <span className="matrix-char">I</span>
              <span className="matrix-char">D</span>
            </div>
          </div>
          <div className="data-stream">
            <div className="data-flow data-flow-1">ANOMALY DETECTED... CLASSIFICATION PENDING... CONTAINMENT PROTOCOLS INITIALIZING...</div>
            <div className="data-flow data-flow-2">SECURE CONTAIN PROTECT... AGENT NETWORK ACTIVE... PROCESSING DATA STREAMS...</div>
            <div className="data-flow data-flow-3">FOUNDATION DATABASE ACCESS... CROSS-REFERENCING ANOMALOUS PROPERTIES...</div>
            <div className="data-flow data-flow-4">NARRATIVE SYNTHESIS IN PROGRESS... DEPLOYING CREATIVE ALGORITHMS...</div>
          </div>
          <h2>GENERATING ANOMALY DOCUMENTATION...</h2>
          
          <div className="agent-status">
            <h3>┌─── AGENT STATUS MONITOR ──────────────────────────────┐</h3>
            <div className="agents-grid">
              <div className={`agent-box ${agentStates.Writer}`}>
                <div className="particle-system">
                  <div className="particle particle-1"></div>
                  <div className="particle particle-2"></div>
                  <div className="particle particle-3"></div>
                </div>
                <div className="agent-container">
                  <div className="agent-icon">
                    ╭─────╮
                    <br />│ {agentStates.Writer === 'thinking' ? '◌◌◌' : agentStates.Writer === 'writing' ? '▓▓▓' : '   '} │
                    <br />╰─────╯
                  </div>
                  <div className="agent-name">WRITER</div>
                  <div className="agent-status">
                    {agentStates.Writer === 'thinking' && <span>ANALYZING<span className="dots"><span>.</span><span>.</span><span>.</span></span></span>}
                    {agentStates.Writer === 'writing' && <span>COMPOSING<span className="cursor-blink">▊</span></span>}
                    {agentStates.Writer === 'waiting' && <span>STANDBY</span>}
                  </div>
                </div>
              </div>
              <div className={`agent-box ${agentStates.Reader}`}>
                <div className="particle-system">
                  <div className="particle particle-1"></div>
                  <div className="particle particle-2"></div>
                  <div className="particle particle-3"></div>
                </div>
                <div className="agent-container">
                  <div className="agent-icon">
                    ╭─────╮
                    <br />│ {agentStates.Reader === 'thinking' ? '◌◌◌' : agentStates.Reader === 'writing' ? '▓▓▓' : '   '} │
                    <br />╰─────╯
                  </div>
                  <div className="agent-name">READER</div>
                  <div className="agent-status">
                    {agentStates.Reader === 'thinking' && <span>REVIEWING<span className="dots"><span>.</span><span>.</span><span>.</span></span></span>}
                    {agentStates.Reader === 'writing' && <span>FEEDBACK<span className="cursor-blink">▊</span></span>}
                    {agentStates.Reader === 'waiting' && <span>STANDBY</span>}
                  </div>
                </div>
              </div>
              <div className={`agent-box ${agentStates.Expert}`}>
                <div className="particle-system">
                  <div className="particle particle-1"></div>
                  <div className="particle particle-2"></div>
                  <div className="particle particle-3"></div>
                </div>
                <div className="agent-container">
                  <div className="agent-icon">
                    ╭─────╮
                    <br />│ {agentStates.Expert === 'thinking' ? '◌◌◌' : agentStates.Expert === 'writing' ? '▓▓▓' : '   '} │
                    <br />╰─────╯
                  </div>
                  <div className="agent-name">EXPERT</div>
                  <div className="agent-status">
                    {agentStates.Expert === 'thinking' && <span>ANALYZING<span className="dots"><span>.</span><span>.</span><span>.</span></span></span>}
                    {agentStates.Expert === 'writing' && <span>ADVISING<span className="cursor-blink">▊</span></span>}
                    {agentStates.Expert === 'waiting' && <span>STANDBY</span>}
                  </div>
                </div>
              </div>
            </div>
            <h3>└───────────────────────────────────────────────────────┘</h3>
          </div>
          
          <MessageTabs messages={messages} currentActivity={currentActivity} />
          
          <div className="current-status">
            <span>PHASE: {currentPhase?.toUpperCase() || 'INITIALIZING'}</span>
            {currentAgent && <span className="status-separator">│</span>}
            {currentAgent && <span>ACTIVE: {currentAgent.toUpperCase()}</span>}
          </div>
        </div>
      )}
      
      {currentView === 'complete' && generatedStory && (
        <div className="story-view">
          <div className="story-header">
            <h2>SCP FOUNDATION</h2>
            <h3>SECURE. CONTAIN. PROTECT.</h3>
            <hr />
            <div className="classification">
              <span>Item #: SCP-XXXX</span>
              <span>Level 3/XXXX</span>
            </div>
            <div className="classification">
              <span>Object Class: [PENDING]</span>
              <span>Classified</span>
            </div>
          </div>
          
          <div className="story-content">
            <pre>{generatedStory}</pre>
          </div>
          
          <div className="story-actions">
            <button 
              className="terminal-button"
              onClick={() => {
                navigator.clipboard.writeText(generatedStory)
                alert('Story copied to clipboard!')
              }}
            >
              COPY TO CLIPBOARD
            </button>
            <button 
              className="terminal-button"
              onClick={() => {
                setCurrentView('config')
                setGeneratedStory(null)
              }}
            >
              GENERATE NEW STORY
            </button>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .generation-view {
          padding: 20px;
        }
        
        .agent-status {
          margin: 20px 0;
        }
        
        .agents-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
          margin: 20px 0;
        }
        
        .agent-box {
          text-align: center;
          padding: 20px;
          border: 1px solid var(--terminal-green);
          opacity: 0.5;
          transition: all 0.3s;
        }
        
        .agent-box.active {
          opacity: 1;
          background: rgba(0, 255, 0, 0.1);
          box-shadow: 0 0 20px var(--terminal-green);
        }
        
        .agent-icon {
          font-size: 24px;
          margin-bottom: 10px;
        }
        
        .agent-name {
          font-size: 14px;
          margin-bottom: 5px;
        }
        
        .agent-status {
          font-size: 12px;
          opacity: 0.8;
        }
        
        .transmission-log {
          margin: 20px 0;
        }
        
        .log-content {
          background: var(--terminal-bg);
          padding: 15px;
          max-height: 300px;
          overflow-y: auto;
          font-size: 13px;
          line-height: 1.6;
        }
        
        .log-entry {
          margin-bottom: 5px;
        }
        
        .agent-label {
          color: var(--terminal-amber);
          margin-right: 10px;
        }
        
        .current-status {
          margin-top: 20px;
          padding: 10px;
          border: 1px solid var(--terminal-green);
          background: rgba(0, 255, 0, 0.05);
          text-align: center;
          font-size: 13px;
          letter-spacing: 1px;
        }
        
        .status-separator {
          margin: 0 15px;
          opacity: 0.5;
        }
        
        .story-view {
          padding: 20px;
        }
        
        .story-header {
          text-align: center;
          margin-bottom: 30px;
        }
        
        .story-header h2 {
          font-size: 24px;
          margin-bottom: 5px;
        }
        
        .story-header h3 {
          font-size: 14px;
          opacity: 0.8;
          margin-bottom: 20px;
        }
        
        .classification {
          display: flex;
          justify-content: space-between;
          margin: 5px 0;
          font-size: 14px;
        }
        
        .story-content {
          background: var(--terminal-bg);
          border: 1px solid var(--terminal-green);
          padding: 20px;
          margin: 20px 0;
          font-family: 'Share Tech Mono', monospace;
          line-height: 1.6;
          max-height: 500px;
          overflow-y: auto;
          overflow-x: hidden;
          max-width: 100%;
        }
        
        .story-content pre {
          white-space: pre-wrap;
          word-wrap: break-word;
          word-break: break-word;
          overflow-wrap: break-word;
          margin: 0;
          font-family: inherit;
        }
        
        .story-actions {
          display: flex;
          gap: 20px;
          justify-content: center;
        }
      `}</style>
    </Terminal>
  )
}