'use client'

import React, { useState, useEffect } from 'react'
import styles from './BootSequence.module.css'

interface BootSequenceProps {
  onComplete: () => void
}

const bootMessages = [
  { text: 'INITIALIZING SCP FOUNDATION SYSTEMS...', delay: 0 },
  { text: 'LOADING KERNEL... ', delay: 500, progress: true },
  { text: 'VERIFYING CLEARANCE...', delay: 1500 },
  { text: 'ACCESS LEVEL: RESEARCHER', delay: 2000 },
  { text: '', delay: 2200 },
  { text: 'WELCOME TO ANOMALY NARRATIVE GENERATION SYSTEM (ANGS)', delay: 2400 },
  { text: 'TYPE \'help\' FOR COMMANDS OR CLICK \'BEGIN\' TO START', delay: 2800 }
]

export default function BootSequence({ onComplete }: BootSequenceProps) {
  const [currentLine, setCurrentLine] = useState(0)
  const [showProgress, setShowProgress] = useState(false)
  const [progress, setProgress] = useState(0)
  const [displayedMessages, setDisplayedMessages] = useState<string[]>([])

  useEffect(() => {
    if (currentLine < bootMessages.length) {
      const message = bootMessages[currentLine]
      const timer = setTimeout(() => {
        if (message.progress) {
          setShowProgress(true)
          // Animate progress bar
          let prog = 0
          const progInterval = setInterval(() => {
            prog += 10
            setProgress(prog)
            if (prog >= 100) {
              clearInterval(progInterval)
              setShowProgress(false)
              setDisplayedMessages(prev => [...prev, message.text + '[████████████] 100%'])
              setCurrentLine(currentLine + 1)
            }
          }, 50)
        } else {
          setDisplayedMessages(prev => [...prev, message.text])
          setCurrentLine(currentLine + 1)
        }
      }, message.delay)

      return () => clearTimeout(timer)
    } else {
      // Boot sequence complete
      setTimeout(onComplete, 500)
    }
  }, [currentLine, onComplete])

  return (
    <div className={styles.bootSequence}>
      <pre className={styles.asciiLogo}>
{`   ███████╗ ██████╗██████╗ 
   ██╔════╝██╔════╝██╔══██╗
   ███████╗██║     ██████╔╝
   ╚════██║██║     ██╔═══╝ 
   ███████║╚██████╗██║     
   ╚══════╝ ╚═════╝╚═╝     
   SECURE. CONTAIN. PROTECT.`}
      </pre>
      <div className={styles.bootMessages}>
        {displayedMessages.map((msg, idx) => (
          <div key={idx} className={styles.bootLine}>
            {'>'} {msg}
          </div>
        ))}
        {showProgress && (
          <div className={styles.progressContainer}>
            {'>'} LOADING KERNEL... [
            <span className={styles.progressBar}>
              {'█'.repeat(Math.floor(progress / 10))}
              {'░'.repeat(10 - Math.floor(progress / 10))}
            </span>
            ] {progress}%
          </div>
        )}
        <span className="cursor" />
      </div>
    </div>
  )
}