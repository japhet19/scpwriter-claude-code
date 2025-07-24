'use client'

import React, { useState, useEffect } from 'react'
import styles from './Terminal.module.css'

interface TerminalProps {
  children: React.ReactNode
  title?: string
  showHeader?: boolean
}

export default function Terminal({ children, title = 'SCP FOUNDATION TERMINAL', showHeader = true }: TerminalProps) {
  const [time, setTime] = useState('')
  const [isFlickering, setIsFlickering] = useState(false)

  useEffect(() => {
    // Update time every second
    const timer = setInterval(() => {
      const now = new Date()
      setTime(now.toUTCString().slice(-12, -4))
    }, 1000)

    // Random flicker effect
    const flickerTimer = setInterval(() => {
      if (Math.random() < 0.05) { // 5% chance every second
        setIsFlickering(true)
        setTimeout(() => setIsFlickering(false), 150)
      }
    }, 1000)

    return () => {
      clearInterval(timer)
      clearInterval(flickerTimer)
    }
  }, [])

  return (
    <div className={`crt-container ${isFlickering ? 'crt-flicker' : ''}`}>
      <div className="terminal-window">
        {showHeader && (
          <div className="terminal-header">
            <div className="terminal-title text-glow">{title}</div>
            <div className="terminal-status">
              <span>SECURE CONNECTION</span>
              <span className="alert-amber">LVL-3</span>
              <span>{time} UTC</span>
            </div>
          </div>
        )}
        <div className={styles.terminalContent}>
          {children}
        </div>
      </div>
    </div>
  )
}