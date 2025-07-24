import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages agent sessions and conversation tracking."""
    
    def __init__(self, session_file: str = "sessions.json"):
        self.session_file = Path(session_file)
        self.sessions: Dict[str, Dict] = {}
        self.active_project_id = str(uuid.uuid4())
        self._load_sessions()
    
    def _load_sessions(self):
        """Load existing sessions from file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    self.sessions = data.get('sessions', {})
                    self.active_project_id = data.get('active_project_id', self.active_project_id)
            except Exception as e:
                logger.error(f"Error loading sessions: {e}")
                self.sessions = {}
    
    def _save_sessions(self):
        """Save sessions to file."""
        try:
            data = {
                'active_project_id': self.active_project_id,
                'sessions': self.sessions,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    def register_agent(self, agent_name: str, session_id: Optional[str] = None) -> Optional[str]:
        """
        Register an agent with the session manager.
        
        Args:
            agent_name: Name of the agent
            session_id: Optional session ID if resuming
            
        Returns:
            The session ID for this agent (or None if not yet created)
        """
        if session_id:
            if session_id in self.sessions:
                # Resuming existing session
                self.sessions[session_id]['last_active'] = datetime.now().isoformat()
                logger.info(f"Resumed session {session_id} for agent {agent_name}")
            else:
                # New session with specific ID
                self.sessions[session_id] = {
                    'agent_name': agent_name,
                    'project_id': self.active_project_id,
                    'created_at': datetime.now().isoformat(),
                    'last_active': datetime.now().isoformat(),
                    'message_count': 0,
                    'status': 'active'
                }
                logger.info(f"Registered new session {session_id} for agent {agent_name}")
            
            self._save_sessions()
            return session_id
        else:
            # No session ID yet - agent will create one on first Claude interaction
            logger.info(f"Agent {agent_name} registered without session ID (will be set on first interaction)")
            return None
    
    def update_session(self, session_id: str, **kwargs):
        """Update session information."""
        if session_id in self.sessions:
            self.sessions[session_id].update(kwargs)
            self.sessions[session_id]['last_active'] = datetime.now().isoformat()
            self._save_sessions()
    
    def increment_message_count(self, session_id: str):
        """Increment the message count for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]['message_count'] += 1
            self.sessions[session_id]['last_active'] = datetime.now().isoformat()
            self._save_sessions()
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a specific session."""
        return self.sessions.get(session_id)
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions for the current project."""
        active_sessions = []
        for session_id, info in self.sessions.items():
            if (info.get('project_id') == self.active_project_id and 
                info.get('status') == 'active'):
                active_sessions.append({
                    'session_id': session_id,
                    **info
                })
        return active_sessions
    
    def get_agent_session(self, agent_name: str) -> Optional[str]:
        """Get the session ID for a specific agent in the current project."""
        for session_id, info in self.sessions.items():
            if (info.get('agent_name') == agent_name and 
                info.get('project_id') == self.active_project_id and
                info.get('status') == 'active'):
                return session_id
        return None
    
    def deactivate_session(self, session_id: str):
        """Mark a session as inactive."""
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = 'inactive'
            self.sessions[session_id]['ended_at'] = datetime.now().isoformat()
            self._save_sessions()
    
    def start_new_project(self) -> str:
        """Start a new project and deactivate all current sessions."""
        # Deactivate all sessions for current project
        for session_id, info in self.sessions.items():
            if info.get('project_id') == self.active_project_id:
                self.deactivate_session(session_id)
        
        # Create new project ID
        self.active_project_id = str(uuid.uuid4())
        self._save_sessions()
        
        logger.info(f"Started new project: {self.active_project_id}")
        return self.active_project_id
    
    def get_project_summary(self) -> Dict:
        """Get a summary of the current project."""
        active_sessions = self.get_active_sessions()
        return {
            'project_id': self.active_project_id,
            'active_agents': len(active_sessions),
            'agents': [s['agent_name'] for s in active_sessions],
            'total_messages': sum(s.get('message_count', 0) for s in active_sessions),
            'sessions': active_sessions
        }