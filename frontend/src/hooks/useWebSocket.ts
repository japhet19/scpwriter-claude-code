import { useEffect, useRef, useState, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'

export interface AgentMessage {
  type: 'status' | 'agent_message' | 'completed' | 'error' | 'agent_update'
  agent?: string
  message: string
  turn?: number
  phase?: string
  story?: string
  state?: 'thinking' | 'writing' | 'waiting'
  activity?: string
}

export interface StoryGenerationParams {
  theme: string
  pages: number
  protagonist?: string
}

export interface AgentStates {
  Writer: 'thinking' | 'writing' | 'waiting'
  Reader: 'thinking' | 'writing' | 'waiting'
  Expert: 'thinking' | 'writing' | 'waiting'
}

export function useWebSocket(url: string = 'http://localhost:8000') {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [currentPhase, setCurrentPhase] = useState<string | null>(null)
  const [agentStates, setAgentStates] = useState<AgentStates>({
    Writer: 'waiting',
    Reader: 'waiting',
    Expert: 'waiting'
  })
  const [currentActivity, setCurrentActivity] = useState<string>('')
  const socketRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(`${url.replace('http', 'ws')}/ws/generate`)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      const data: AgentMessage = JSON.parse(event.data)
      
      setMessages(prev => [...prev, data])
      
      if (data.agent) {
        setCurrentAgent(data.agent)
      }
      
      if (data.phase) {
        setCurrentPhase(data.phase)
      }
      
      // Handle agent state updates
      if (data.type === 'agent_update' && data.agent && data.state) {
        setAgentStates(prev => ({
          ...prev,
          [data.agent as keyof AgentStates]: data.state
        }))
        
        if (data.activity) {
          setCurrentActivity(data.activity)
        }
      }
      
      // Reset all agents to waiting when a new one becomes active
      if (data.type === 'agent_message' && data.agent) {
        setAgentStates(prev => ({
          Writer: data.agent === 'Writer' ? 'writing' : 'waiting',
          Reader: data.agent === 'Reader' ? 'writing' : 'waiting',
          Expert: data.agent === 'Expert' ? 'writing' : 'waiting'
        }))
      }
      
      if (data.type === 'completed' || data.type === 'error') {
        setIsGenerating(false)
        setCurrentAgent(null)
        setCurrentPhase(null)
        setAgentStates({
          Writer: 'waiting',
          Reader: 'waiting',
          Expert: 'waiting'
        })
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
      setIsGenerating(false)
    }

    socketRef.current = ws
  }, [url])

  const generateStory = useCallback((params: StoryGenerationParams) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    setMessages([])
    setIsGenerating(true)
    socketRef.current.send(JSON.stringify(params))
  }, [])

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }
  }, [])

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    isConnected,
    connect,
    disconnect,
    generateStory,
    messages,
    isGenerating,
    currentAgent,
    currentPhase,
    agentStates,
    currentActivity
  }
}