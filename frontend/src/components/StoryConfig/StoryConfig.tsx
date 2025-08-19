'use client'

import React, { useState } from 'react'
import styles from './StoryConfig.module.css'

interface StoryConfigProps {
  onSubmit: (config: StoryConfiguration) => void
}

export interface StoryConfiguration {
  theme: string
  pages: number
  protagonist?: string
  horrorLevel: number
  enableRedaction: boolean
}

const exampleThemes = [
  'A mirror that shows your greatest fear',
  'A door that opens to alternate realities',
  'A phone booth that calls the dead',
  'A painting that ages instead of its owner',
  'An elevator that goes to floors that don\'t exist'
]

export default function StoryConfig({ onSubmit }: StoryConfigProps) {
  const [theme, setTheme] = useState('')
  const [pages, setPages] = useState(3)
  const [protagonist, setProtagonist] = useState('')
  const [horrorLevel, setHorrorLevel] = useState(40)
  const [enableRedaction, setEnableRedaction] = useState(true)
  const [isGeneratingName, setIsGeneratingName] = useState(false)

  const generateProtagonistName = () => {
    setIsGeneratingName(true)
    const firstNames = ['Marcus', 'Elena', 'Raj', 'Yuki', 'Amara', 'Viktor', 'Zara', 'Chen']
    const lastNames = ['Thompson', 'Vasquez', 'Patel', 'Tanaka', 'Okafor', 'Petrov', 'Hassan', 'Wei']
    const titles = ['Agent', 'Dr.', 'Researcher', 'Specialist', 'Director', 'Professor']
    
    setTimeout(() => {
      const title = titles[Math.floor(Math.random() * titles.length)]
      const firstName = firstNames[Math.floor(Math.random() * firstNames.length)]
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)]
      setProtagonist(`${title} ${firstName} ${lastName}`)
      setIsGeneratingName(false)
    }, 500)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!theme.trim()) return
    
    onSubmit({
      theme,
      pages,
      protagonist: protagonist.trim() || undefined,
      horrorLevel,
      enableRedaction
    })
  }

  return (
    <form onSubmit={handleSubmit} className={styles.configForm}>
      <div className={styles.formHeader}>
        <h2 className="glitch-hover">┌─── ANOMALY GENERATION PARAMETERS ───────────────────┐</h2>
      </div>
      
      <div className={styles.formContent}>
        <div className={styles.infoSection}>
          <p className={styles.infoText}>
            <span className={styles.infoIcon}>ℹ</span>
            SCP stories are fictional scientific reports about paranormal objects and entities, 
            written in a clinical documentary style. 
            <a 
              href="https://en.wikipedia.org/wiki/SCP_Foundation" 
              target="_blank" 
              rel="noopener noreferrer"
              className={styles.infoLink}
            >
              Learn more about the SCP format →
            </a>
          </p>
        </div>
        <div className={styles.statusRow}>
          <span className="glitch-hover">DESIGNATION: SCP-[PENDING]</span>
          <span className="glitch-hover">CLASSIFICATION: [PENDING]</span>
        </div>

        <div className={styles.formGroup}>
          <label className={`${styles.label} glitch-hover`}>▼ ANOMALY DESCRIPTION</label>
          <textarea
            className="terminal-input"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            placeholder="Describe the anomalous object/entity..."
            rows={3}
            required
          />
          <div className={styles.examples}>
            <small>Examples:</small>
            {exampleThemes.map((example, idx) => (
              <button
                key={idx}
                type="button"
                className={styles.exampleButton}
                onClick={() => setTheme(example)}
              >
                • {example}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={`${styles.label} glitch-hover`}>▼ NARRATIVE PARAMETERS</label>
          <div className={styles.paramRow}>
            <span>Document Length:</span>
            <div className={styles.pageOptions}>
              {[1, 2, 3, 5, 10].map(num => (
                <label key={num} className="led-radio">
                  <input
                    type="radio"
                    name="pages"
                    value={num}
                    checked={pages === num}
                    onChange={() => setPages(num)}
                  />
                  <span className="led-indicator" />
                  <span>{num}</span>
                </label>
              ))}
              <span className={styles.pageLabel}>pages</span>
            </div>
          </div>
          
          <div className={styles.paramRow}>
            <span>Protagonist:</span>
            <div className={styles.protagonistInput}>
              <input
                type="text"
                className="terminal-input"
                value={protagonist}
                onChange={(e) => setProtagonist(e.target.value)}
                placeholder="Enter name or generate..."
              />
              <button
                type="button"
                className="terminal-button"
                onClick={generateProtagonistName}
                disabled={isGeneratingName}
              >
                {isGeneratingName ? 'GENERATING...' : 'GENERATE'}
              </button>
            </div>
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={`${styles.label} glitch-hover`}>▼ ADVANCED OPTIONS</label>
          <div className={styles.paramRow}>
            <span>Horror Level:</span>
            <div className={styles.sliderContainer}>
              <input
                type="range"
                min="0"
                max="100"
                value={horrorLevel}
                onChange={(e) => setHorrorLevel(Number(e.target.value))}
                className={styles.horrorSlider}
                style={{
                  background: `linear-gradient(to right, var(--terminal-green) 0%, var(--terminal-amber) 50%, var(--terminal-red) 100%)`
                }}
              />
              <span className={styles.sliderValue}>{horrorLevel}%</span>
            </div>
          </div>
          
          <div className={styles.paramRow}>
            <span>Redaction:</span>
            <div className={styles.toggleOptions}>
              <label className="led-radio">
                <input
                  type="radio"
                  name="redaction"
                  checked={enableRedaction}
                  onChange={() => setEnableRedaction(true)}
                />
                <span className="led-indicator" />
                <span>ON</span>
              </label>
              <label className="led-radio">
                <input
                  type="radio"
                  name="redaction"
                  checked={!enableRedaction}
                  onChange={() => setEnableRedaction(false)}
                />
                <span className="led-indicator" />
                <span>OFF</span>
              </label>
            </div>
          </div>
        </div>

        <div className={styles.formActions}>
          <button type="submit" className="terminal-button">
            INITIATE GENERATION
          </button>
          <button type="button" className="terminal-button" onClick={() => window.location.reload()}>
            ABORT MISSION
          </button>
        </div>
      </div>
      
      <div className={styles.formFooter}>
        <h2 className="glitch-hover">└──────────────────────────────────────────────────────┘</h2>
      </div>
    </form>
  )
}