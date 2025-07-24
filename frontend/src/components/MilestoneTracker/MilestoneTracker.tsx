'use client'

import React from 'react'

interface MilestoneTrackerProps {
  milestones: Set<string>
  currentPhase: string | null
}

const MILESTONE_DEFINITIONS = [
  { id: 'theme_selected', label: 'Theme Selected', icon: '◆' },
  { id: 'initial_draft', label: 'Initial Draft', icon: '◈' },
  { id: 'feedback_received', label: 'Feedback', icon: '◊' },
  { id: 'revision_complete', label: 'Revision', icon: '◉' },
  { id: 'expert_review', label: 'Expert Review', icon: '◎' },
  { id: 'final_polish', label: 'Final Polish', icon: '●' },
  { id: 'story_complete', label: 'Complete', icon: '★' }
]

export default function MilestoneTracker({ milestones, currentPhase }: MilestoneTrackerProps) {
  const getCurrentMilestone = () => {
    // Map phases to milestone IDs
    const phaseToMilestone: Record<string, string> = {
      'brainstorming': 'theme_selected',
      'initial_draft': 'initial_draft',
      'feedback': 'feedback_received',
      'revision': 'revision_complete',
      'expert_review': 'expert_review',
      'final_polish': 'final_polish',
      'completed': 'story_complete'
    }
    
    return currentPhase ? phaseToMilestone[currentPhase.toLowerCase()] : null
  }

  const currentMilestoneId = getCurrentMilestone()

  return (
    <div className="milestone-container">
      <h3>STORY PROGRESS</h3>
      <div className="milestone-tracker">
        {MILESTONE_DEFINITIONS.map((milestone, index) => {
          const isCompleted = milestones.has(milestone.id)
          const isCurrent = milestone.id === currentMilestoneId
          const isPast = MILESTONE_DEFINITIONS.findIndex(m => m.id === currentMilestoneId) > index

          return (
            <div key={milestone.id} className="milestone-item">
              <div className={`milestone-dot ${isCompleted ? 'completed' : ''} ${isCurrent ? 'active' : ''}`}>
                {isCompleted && <span style={{ fontSize: '12px' }}>{milestone.icon}</span>}
              </div>
              {index < MILESTONE_DEFINITIONS.length - 1 && (
                <div className={`milestone-line ${(isCompleted || isPast) ? 'completed' : ''}`} />
              )}
              <div className="milestone-label">{milestone.label}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}