"""
FastAPI backend for SCP Writer with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scp_coordinator import SCPCoordinator, StoryConfig
from utils.text_sanitizer import sanitize_text

# Store active websocket connections
active_connections: Dict[str, WebSocket] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting SCP Writer API...")
    yield
    # Shutdown
    print("Shutting down SCP Writer API...")

app = FastAPI(
    title="SCP Writer API",
    description="Backend API for SCP story generation with AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SCP Writer API", "status": "operational"}

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    # Accept without subprotocol for Safari compatibility
    await websocket.accept()
    connection_id = id(websocket)
    active_connections[str(connection_id)] = websocket
    
    # Add keep-alive ping task for Safari
    async def send_ping():
        try:
            while True:
                await asyncio.sleep(20)  # Ping every 20 seconds
                if str(connection_id) in active_connections:
                    await websocket.send_json({"type": "ping"})
        except:
            pass
    
    ping_task = asyncio.create_task(send_ping())
    
    try:
        while True:
            # Receive story parameters
            data = await websocket.receive_text()
            params = json.loads(data)
            
            theme = params.get("theme", "")
            page_limit = params.get("pages", 3)
            protagonist_name = params.get("protagonist")
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "status",
                "message": "Initializing story generation...",
                "phase": "initialization"
            })
            
            # Create story configuration
            story_config = StoryConfig(
                page_limit=page_limit,
                protagonist_name=protagonist_name
            )
            
            # Create coordinator
            coordinator = SCPCoordinator(story_config)
            
            # Create custom agent wrapper for streaming
            class StreamingAgent:
                def __init__(self, original_agent, websocket, coordinator):
                    self.original_agent = original_agent
                    self.websocket = websocket
                    self.coordinator = coordinator
                    # Copy necessary attributes
                    self.name = original_agent.name
                    self.session_id = original_agent.session_id
                    self.system_prompt = original_agent.system_prompt
                    
                async def respond(self, prompt: str, skip_callback: bool = False):
                    # Send thinking state update
                    await self.websocket.send_json({
                        "type": "agent_update",
                        "agent": self.name,
                        "state": "thinking",
                        "activity": self._get_thinking_activity(),
                        "message": f"{self.name} is processing..."
                    })
                    
                    # Small delay to ensure state is visible
                    await asyncio.sleep(0.5)
                    
                    # Send writing state update
                    await self.websocket.send_json({
                        "type": "agent_update",
                        "agent": self.name,
                        "state": "writing",
                        "activity": self._get_writing_activity(),
                        "message": f"{self.name} is composing response..."
                    })
                    
                    # Get response from original agent
                    response = await self.original_agent.respond(prompt, skip_callback)
                    
                    # Stream the actual message
                    await self.websocket.send_json({
                        "type": "agent_message",
                        "agent": self.name,
                        "message": sanitize_text(response),
                        "turn": self.coordinator.turn_count,
                        "phase": self.coordinator.current_phase
                    })
                    
                    # Send milestone update if applicable
                    milestone = self._get_milestone_for_phase(self.coordinator.current_phase)
                    if milestone:
                        await self.websocket.send_json({
                            "type": "agent_update",
                            "agent": self.name,
                            "state": "waiting",
                            "milestone": milestone,
                            "message": f"Milestone reached: {milestone}"
                        })
                    
                    return response
                
                def _get_thinking_activity(self):
                    activities = {
                        "Writer": "Analyzing theme and narrative structure...",
                        "Reader": "Preparing to review story elements...",
                        "Expert": "Checking SCP database and protocols..."
                    }
                    return activities.get(self.name, f"{self.name} is thinking...")
                
                def _get_writing_activity(self):
                    activities = {
                        "Writer": "Crafting SCP narrative...",
                        "Reader": "Providing detailed feedback...",
                        "Expert": "Documenting containment procedures..."
                    }
                    return activities.get(self.name, f"{self.name} is writing...")
                
                def _get_milestone_for_phase(self, phase):
                    if not phase:
                        return None
                    phase_lower = phase.lower()
                    milestones = {
                        "brainstorming": "theme_selected",
                        "initial_draft": "initial_draft",
                        "feedback": "feedback_received",
                        "revision": "revision_complete",
                        "expert_review": "expert_review",
                        "final_polish": "final_polish"
                    }
                    return milestones.get(phase_lower)
            
            # Override run_conversation to wrap agents after initialization
            original_run_conversation = coordinator.run_conversation
            
            async def wrapped_run_conversation(opening_speaker: str, opening_prompt: str):
                # Wrap agents with streaming capability
                for agent_name in coordinator.agents:
                    coordinator.agents[agent_name] = StreamingAgent(
                        coordinator.agents[agent_name], 
                        websocket, 
                        coordinator
                    )
                # Call original method
                return await original_run_conversation(opening_speaker, opening_prompt)
            
            coordinator.run_conversation = wrapped_run_conversation
            
            # Run story generation
            try:
                await coordinator.run_story_creation(theme)
                
                # Send completion message
                story_path = Path("output/story_output.md")
                if story_path.exists():
                    story_content = story_path.read_text(encoding='utf-8', errors='replace')
                    
                    # Send final milestone
                    await websocket.send_json({
                        "type": "agent_update",
                        "agent": "System",
                        "state": "completed",
                        "milestone": "story_complete",
                        "message": "Story generation complete!"
                    })
                    
                    await websocket.send_json({
                        "type": "completed",
                        "story": sanitize_text(story_content),
                        "message": "Story generation complete!"
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Story generation completed but no output file found"
                    })
                    
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error during story generation: {str(e)}"
                })
    
    except WebSocketDisconnect:
        del active_connections[str(connection_id)]
        print(f"Client {connection_id} disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if str(connection_id) in active_connections:
            del active_connections[str(connection_id)]
    finally:
        # Clean up ping task
        ping_task.cancel()
        if str(connection_id) in active_connections:
            del active_connections[str(connection_id)]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(active_connections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, ws_ping_interval=20, ws_ping_timeout=20)