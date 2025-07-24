import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
try:
    from claude_code_sdk import query, ClaudeCodeOptions
except ImportError:
    # Fallback for different SDK naming
    from claude_sdk import query, ClaudeCodeOptions
import re
import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.text_sanitizer import sanitize_text

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents in the SCP writer system."""
    
    def __init__(self, name: str, system_prompt: str, orchestrator_callback=None):
        self.name = name
        self.system_prompt = system_prompt
        self.session_id: Optional[str] = None
        self.conversation_history = []
        self.logger = logging.getLogger(f"agent.{name}")
        self.orchestrator_callback = orchestrator_callback
        
    def _extract_session_id(self, response: str) -> Optional[str]:
        """Extract session ID from Claude's response if available."""
        # Look for session_id in SystemMessage or ResultMessage
        import re
        
        # Try to find session_id in various formats
        patterns = [
            r"session_id['\"]:\s*['\"]([a-f0-9-]+)['\"]",  # In dict format
            r"session_id='([a-f0-9-]+)'",  # In repr format
            r"'session_id':\s*'([a-f0-9-]+)'",  # JSON style
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1)
        
        return None
    
    def _format_timestamp(self) -> str:
        """Generate a formatted timestamp for messages."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _read_discussion_file(self) -> str:
        """Read the current discussion file contents."""
        discussion_path = Path("discussions/story_discussion.md")
        if discussion_path.exists():
            return discussion_path.read_text(encoding='utf-8', errors='replace')
        return ""
    
    def _read_output_file(self) -> str:
        """Read the current story output file contents."""
        output_path = Path("output/story_output.md")
        if output_path.exists():
            return output_path.read_text(encoding='utf-8', errors='replace')
        return ""
    
    async def _append_to_discussion(self, message: str):
        """Append a message to the discussion file."""
        discussion_path = Path("discussions/story_discussion.md")
        timestamp = self._format_timestamp()
        
        # Sanitize the message before writing
        sanitized_message = sanitize_text(message)
        formatted_message = f"\n## [{self.name}] - [{timestamp}]\n{sanitized_message}\n---\n"
        
        with open(discussion_path, 'a', encoding='utf-8') as f:
            f.write(formatted_message)
        
        self.logger.info(f"Appended message to discussion file")
    
    async def respond(self, trigger_message: str, include_output: bool = False, skip_callback: bool = False, stream_output: bool = True) -> str:
        """
        Generate a response based on the trigger message and current context.
        
        Args:
            trigger_message: The message that triggered this response
            include_output: Whether to include the story output file in context
            skip_callback: Whether to skip triggering the orchestrator callback
            stream_output: Whether to print response in real-time as it streams
            
        Returns:
            The agent's response
        """
        # Build context from discussion and optionally output file
        discussion_content = self._read_discussion_file()
        context = f"Current discussion:\n{discussion_content}"
        
        if include_output:
            output_content = self._read_output_file()
            context += f"\n\nCurrent story output:\n{output_content}"
        
        # Create the prompt
        prompt = f"""
You are {self.name}. 

{context}

The latest message triggering your response:
{trigger_message}

Based on your role and the current context, provide an appropriate response.
Remember to check both the discussion file and (if relevant) the output file.
"""
        
        # Set up options with session management
        # Try with model specification first, fallback to default if issues
        use_model = "claude-sonnet-4-20250514"  # Sonnet 4 for speed/cost
        
        if self.session_id:
            # Continue existing conversation
            options = ClaudeCodeOptions(
                resume=self.session_id,
                append_system_prompt=self.system_prompt,
                cwd=Path(".").absolute(),
                allowed_tools=["Read", "Edit"],  # Agents can read/write files
                max_turns=20,  # Allow multiple turns for complex edits
                model=use_model if use_model else None  # Optional model
            )
        else:
            # Start new conversation
            options = ClaudeCodeOptions(
                append_system_prompt=self.system_prompt,
                cwd=Path(".").absolute(),
                allowed_tools=["Read", "Edit"],  # Agents can read/write files
                max_turns=20,  # Allow multiple turns for complex edits
                model=use_model if use_model else None  # Optional model
            )
        
        try:
            response_text = ""
            tool_was_used = False
            
            # Print agent name if streaming
            if stream_output:
                print(f"\n{self.name}: ", end="", flush=True)
            
            async for message in query(prompt=prompt, options=options):
                # Track all messages for complete response
                class_name = message.__class__.__name__
                
                # Debug logging to understand message format
                self.logger.debug(f"Received {class_name}: {message}")
                
                if class_name == 'SystemMessage':
                    # Skip system messages but check for session ID
                    pass
                elif class_name == 'AssistantMessage' and hasattr(message, 'content'):
                    # Handle AssistantMessage with content list
                    if isinstance(message.content, list):
                        for block in message.content:
                            block_type = block.__class__.__name__
                            if block_type == 'TextBlock' and hasattr(block, 'text'):
                                text_chunk = block.text.strip()
                                if text_chunk:
                                    # Print complete text blocks as they arrive
                                    if stream_output:
                                        print(text_chunk)
                                    response_text += text_chunk + "\n"
                            elif block_type == 'ToolUseBlock':
                                # Tool is being used, we'll capture results later
                                tool_was_used = True
                                if stream_output and hasattr(block, 'name'):
                                    # Show tool use indicator
                                    print(f"[Using {block.name} tool...]")
                                self.logger.debug(f"Tool use detected: {block}")
                    elif isinstance(message.content, str):
                        if stream_output:
                            print(message.content.strip())
                        response_text += message.content.strip() + "\n"
                elif class_name == 'UserMessage':
                    # UserMessage often contains tool results
                    if hasattr(message, 'content'):
                        if isinstance(message.content, list):
                            for item in message.content:
                                if hasattr(item, 'content') and isinstance(item.content, str):
                                    # This is likely a tool result
                                    response_text += item.content.strip() + "\n"
                                elif isinstance(item, str):
                                    response_text += item.strip() + "\n"
                        elif isinstance(message.content, str):
                            response_text += message.content.strip() + "\n"
                elif class_name == 'TextBlock' and hasattr(message, 'text'):
                    # Direct TextBlock (shouldn't happen with our structure)
                    response_text += message.text.strip() + "\n"
                elif class_name == 'ResultMessage':
                    # Skip result messages but log them
                    self.logger.debug(f"Result message: {message}")
                elif hasattr(message, 'text') and not class_name.startswith('Tool'):
                    # Other messages with text attribute
                    response_text += message.text.strip() + "\n"
                elif hasattr(message, 'content') and isinstance(message.content, str):
                    # Messages with string content
                    response_text += message.content.strip() + "\n"
                
                # Extract session ID on first run
                if not self.session_id:
                    # Check for SystemMessage with session data
                    if hasattr(message, 'data') and isinstance(message.data, dict) and 'session_id' in message.data:
                        self.session_id = message.data['session_id']
                        self.logger.info(f"Session ID set from SystemMessage: {self.session_id}")
                        
                        # Register with session manager if available
                        if hasattr(self, 'session_manager') and self.session_manager:
                            self.session_manager.register_agent(self.name, self.session_id)
                    # Check if message has direct session_id attribute
                    elif hasattr(message, 'session_id'):
                        self.session_id = message.session_id
                        self.logger.info(f"Session ID set from attribute: {self.session_id}")
                    else:
                        # Try to extract from string representation
                        msg_str = str(message)
                        extracted_id = self._extract_session_id(msg_str)
                        if extracted_id:
                            self.session_id = extracted_id
                            self.logger.info(f"Session ID set from string: {self.session_id}")
            
            # Log the interaction
            self.conversation_history.append({
                "timestamp": self._format_timestamp(),
                "trigger": trigger_message,
                "response": response_text
            })
            
            # Clean up response text
            response_text = response_text.strip()
            
            # Only write non-empty responses to discussion file
            if response_text:
                await self._append_to_discussion(response_text)
                
                # Notify orchestrator if callback is set and not skipped
                if self.orchestrator_callback and not skip_callback:
                    await self.orchestrator_callback(self.name, response_text)
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    async def continue_session(self, new_prompt: str) -> str:
        """Continue an existing session with a new prompt."""
        if not self.session_id:
            self.logger.warning("No session ID found, starting new session")
            return await self.respond(new_prompt)
        
        options = ClaudeCodeOptions(
            resume=self.session_id,
            continue_conversation=True,
            append_system_prompt=self.system_prompt,
            cwd=Path(".").absolute(),
            allowed_tools=["Read", "Edit"],
            max_turns=1
        )
        
        try:
            response_text = ""
            tool_was_used = False
            
            async for message in query(prompt=new_prompt, options=options):
                # Track all messages for complete response
                class_name = message.__class__.__name__
                
                if class_name == 'SystemMessage':
                    # Skip system messages
                    pass
                elif class_name == 'AssistantMessage' and hasattr(message, 'content'):
                    # Handle AssistantMessage with content list
                    if isinstance(message.content, list):
                        for block in message.content:
                            block_type = block.__class__.__name__
                            if block_type == 'TextBlock' and hasattr(block, 'text'):
                                response_text += block.text.strip() + "\n"
                            elif block_type == 'ToolUseBlock':
                                # Tool is being used
                                tool_was_used = True
                                self.logger.debug(f"Tool use detected: {block}")
                    elif isinstance(message.content, str):
                        response_text += message.content.strip() + "\n"
                elif class_name == 'UserMessage':
                    # UserMessage often contains tool results
                    if hasattr(message, 'content'):
                        if isinstance(message.content, list):
                            for item in message.content:
                                if hasattr(item, 'content') and isinstance(item.content, str):
                                    # Tool result
                                    response_text += item.content.strip() + "\n"
                                elif isinstance(item, str):
                                    response_text += item.strip() + "\n"
                        elif isinstance(message.content, str):
                            response_text += message.content.strip() + "\n"
                elif class_name == 'TextBlock' and hasattr(message, 'text'):
                    # Direct TextBlock
                    response_text += message.text.strip() + "\n"
                elif class_name == 'ResultMessage':
                    # Skip but log
                    self.logger.debug(f"Result message: {message}")
                elif hasattr(message, 'text') and not class_name.startswith('Tool'):
                    # Other messages with text
                    response_text += message.text.strip() + "\n"
                elif hasattr(message, 'content') and isinstance(message.content, str):
                    # String content
                    response_text += message.content.strip() + "\n"
            
            # Log and append to discussion
            self.conversation_history.append({
                "timestamp": self._format_timestamp(),
                "prompt": new_prompt,
                "response": response_text
            })
            
            # Clean up response text
            response_text = response_text.strip()
            
            # Only write non-empty responses to discussion file
            if response_text:
                await self._append_to_discussion(response_text)
                
                # Notify orchestrator if callback is set and not skipped
                if self.orchestrator_callback and not skip_callback:
                    await self.orchestrator_callback(self.name, response_text)
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error continuing session: {e}")
            raise
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's conversation history."""
        return {
            "agent_name": self.name,
            "session_id": self.session_id,
            "message_count": len(self.conversation_history),
            "history": self.conversation_history
        }