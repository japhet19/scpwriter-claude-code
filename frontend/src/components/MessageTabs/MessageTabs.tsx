'use client'

import React, { useState, useEffect, useRef } from 'react'
import ActivityFeed from '@/components/ActivityFeed/ActivityFeed'
import { AgentMessage } from '@/hooks/useWebSocket'

interface MessageTabsProps {
  messages: AgentMessage[]
  currentActivity: string
}

export default function MessageTabs({ messages, currentActivity }: MessageTabsProps) {
  const [activeTab, setActiveTab] = useState<'activity' | 'fullLog'>('activity')
  const fullLogRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when switching to full log or new messages arrive
  useEffect(() => {
    if (activeTab === 'fullLog' && fullLogRef.current) {
      fullLogRef.current.scrollTop = fullLogRef.current.scrollHeight
    }
  }, [activeTab, messages])

  const getFullMessageContent = (msg: AgentMessage): string => {
    if (msg.type === 'agent_message' && msg.message) {
      return msg.message
    }
    return msg.message || ''
  }

  return (
    <div className="message-tabs-container">
      <div className="tab-header">
        <button 
          className={`tab-button ${activeTab === 'activity' ? 'active' : ''}`}
          onClick={() => setActiveTab('activity')}
        >
          ◊ ACTIVITY
        </button>
        <button 
          className={`tab-button ${activeTab === 'fullLog' ? 'active' : ''}`}
          onClick={() => setActiveTab('fullLog')}
        >
          ▤ FULL LOG
        </button>
      </div>

      {activeTab === 'activity' && (
        <ActivityFeed messages={messages} currentActivity={currentActivity} />
      )}

      {activeTab === 'fullLog' && (
        <div className="full-log-container">
          <h3>┌─── AGENT CONVERSATION LOG ───────────────────────────┐</h3>
          <div className="full-log-content" ref={fullLogRef}>
            {messages.map((msg, idx) => (
              <div key={idx} className="full-log-entry">
                {msg.agent && (
                  <div className="log-header">
                    <span className="log-agent">[{msg.agent}]</span>
                    {msg.turn && <span className="log-turn">Turn {msg.turn}</span>}
                    {msg.phase && <span className="log-phase">{msg.phase}</span>}
                  </div>
                )}
                <div className="log-message">
                  <pre>{getFullMessageContent(msg)}</pre>
                </div>
                <div className="log-divider">─────────────────────────────────────</div>
              </div>
            ))}
          </div>
          <h3>└──────────────────────────────────────────────────────┘</h3>
        </div>
      )}
    </div>
  )
}