'use client'

import React, { useEffect, useRef } from 'react'
import { AgentMessage } from '@/hooks/useWebSocket'

interface ActivityFeedProps {
  messages: AgentMessage[]
  currentActivity: string
}

export default function ActivityFeed({ messages, currentActivity }: ActivityFeedProps) {
  const feedRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom on new messages
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight
    }
  }, [messages])

  const getActivityDescription = (msg: AgentMessage): string => {
    if (msg.activity) return msg.activity

    switch (msg.type) {
      case 'agent_update':
        if (msg.state === 'thinking') {
          switch (msg.agent) {
            case 'Writer':
              return 'Writer is analyzing the theme and planning the narrative structure...'
            case 'Reader':
              return 'Reader is reviewing the story for clarity and coherence...'
            case 'Expert':
              return 'Expert is checking SCP formatting and containment procedures...'
            default:
              return `${msg.agent} is thinking...`
          }
        } else if (msg.state === 'writing') {
          switch (msg.agent) {
            case 'Writer':
              return 'Writer is composing the SCP narrative...'
            case 'Reader':
              return 'Reader is providing feedback on the story...'
            case 'Expert':
              return 'Expert is advising on technical details...'
            default:
              return `${msg.agent} is writing...`
          }
        }
        break
      case 'agent_message':
        if (msg.agent && msg.message) {
          const preview = msg.message.substring(0, 100) + (msg.message.length > 100 ? '...' : '')
          return `${msg.agent}: ${preview}`
        }
        break
      case 'status':
        return msg.message
      case 'error':
        return `⚠️ Error: ${msg.message}`
    }
    
    return msg.message
  }

  const getTimestamp = () => {
    const now = new Date()
    return now.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  }

  const getIcon = (msg: AgentMessage): string => {
    switch (msg.type) {
      case 'agent_update':
        return msg.state === 'thinking' ? '◌' : '▓'
      case 'agent_message':
        return '►'
      case 'status':
        return '●'
      case 'error':
        return '⚠'
      default:
        return '•'
    }
  }

  return (
    <div className="activity-feed-container">
      <h3>┌─── ACTIVITY MONITOR ─────────────────────────────────┐</h3>
      <div className="activity-feed" ref={feedRef}>
        {messages.slice(-10).map((msg, idx) => (
          <div key={idx} className="activity-entry" style={{ animationDelay: `${idx * 0.05}s` }}>
            <span className="activity-timestamp">{getTimestamp()}</span>
            <span className="activity-icon">{getIcon(msg)}</span>
            <span className="activity-text">{getActivityDescription(msg)}</span>
          </div>
        ))}
        {currentActivity && (
          <div className="activity-entry">
            <span className="activity-timestamp">{getTimestamp()}</span>
            <span className="activity-icon">◌</span>
            <span className="activity-text">{currentActivity}</span>
          </div>
        )}
      </div>
      <h3>└──────────────────────────────────────────────────────┘</h3>
    </div>
  )
}