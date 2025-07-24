import logging
import asyncio
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AgentFileHandler(FileSystemEventHandler):
    """Handles file system events for agent communication files."""
    
    def __init__(self, orchestrator_callback: Callable, checkpoint_callback: Callable):
        super().__init__()
        self.orchestrator_callback = orchestrator_callback
        self.checkpoint_callback = checkpoint_callback
        self.last_discussion_update = datetime.now()
        self.last_output_update = datetime.now()
        self.debounce_seconds = 1  # Avoid multiple triggers for same edit
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        current_time = datetime.now()
        
        # Handle discussion file changes
        if file_path.name == "story_discussion.md":
            # Debounce check
            if (current_time - self.last_discussion_update).seconds >= self.debounce_seconds:
                self.last_discussion_update = current_time
                logger.info("Discussion file modified")
                # Call orchestrator to process the update
                asyncio.create_task(self.orchestrator_callback("discussion_update"))
                
        # Handle output file changes
        elif file_path.name == "story_output.md":
            # Debounce check
            if (current_time - self.last_output_update).seconds >= self.debounce_seconds:
                self.last_output_update = current_time
                logger.info("Output file modified")
                # Check for checkpoint conditions
                asyncio.create_task(self.checkpoint_callback("output_update"))


class FileWatcher:
    """Monitors discussion and output files for changes."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.observer = Observer()
        self.is_running = False
        self.watch_paths = {
            "discussions": Path("discussions"),
            "output": Path("output")
        }
        
    def _ensure_files_exist(self):
        """Ensure monitored files exist."""
        discussion_file = self.watch_paths["discussions"] / "story_discussion.md"
        output_file = self.watch_paths["output"] / "story_output.md"
        
        # Create files if they don't exist
        if not discussion_file.exists():
            discussion_file.touch()
            logger.info("Created discussion file")
            
        if not output_file.exists():
            output_file.touch()
            logger.info("Created output file")
    
    async def on_discussion_modified(self, event_type: str):
        """Handle discussion file modifications."""
        try:
            logger.info(f"Processing discussion modification: {event_type}")
            
            # Read the discussion file to get the latest message
            discussion_path = self.watch_paths["discussions"] / "story_discussion.md"
            content = discussion_path.read_text()
            
            # Extract the last message (after the last separator)
            messages = content.split("---")
            if messages and messages[-1].strip():
                # Parse the last message
                last_message = messages[-1].strip()
                
                # Extract speaker name from message format: ## [AGENT_NAME] - [TIMESTAMP]
                import re
                speaker_match = re.search(r'## \[([^\]]+)\]', last_message)
                
                if speaker_match:
                    last_speaker = speaker_match.group(1)
                    
                    # Don't process if orchestrator is talking to itself
                    if last_speaker != "ORCHESTRATOR":
                        # Let orchestrator decide who should respond next
                        await self.orchestrator.process_discussion_update(last_speaker, last_message)
                        
        except Exception as e:
            logger.error(f"Error processing discussion modification: {e}")
    
    async def on_output_modified(self, event_type: str):
        """Handle output file modifications."""
        try:
            logger.info(f"Processing output modification: {event_type}")
            
            # Check if we need to trigger a checkpoint
            if self.orchestrator.checkpoint_manager:
                checkpoint = self.orchestrator.checkpoint_manager.should_pause_for_review()
                
                if checkpoint:
                    logger.info(f"Triggering checkpoint: {checkpoint}")
                    await self.orchestrator.trigger_checkpoint_review(checkpoint)
                else:
                    # Update progress tracking
                    progress = self.orchestrator.checkpoint_manager.get_progress_summary()
                    logger.info(f"Story progress: {progress['current_pages']:.2f} pages")
                    
                    # Check if writer should start wrapping up
                    if self.orchestrator.checkpoint_manager.should_start_conclusion():
                        await self.orchestrator.notify_conclusion_needed()
                        
        except Exception as e:
            logger.error(f"Error processing output modification: {e}")
    
    def start(self):
        """Start watching files."""
        if self.is_running:
            logger.warning("File watcher already running")
            return
            
        # Ensure files exist
        self._ensure_files_exist()
        
        # Create event handler
        handler = AgentFileHandler(
            orchestrator_callback=self.on_discussion_modified,
            checkpoint_callback=self.on_output_modified
        )
        
        # Schedule observers for both directories
        for name, path in self.watch_paths.items():
            if path.exists():
                self.observer.schedule(handler, str(path), recursive=False)
                logger.info(f"Watching {name} directory: {path}")
            else:
                logger.error(f"Watch path does not exist: {path}")
        
        # Start observer
        self.observer.start()
        self.is_running = True
        logger.info("File watcher started")
    
    def stop(self):
        """Stop watching files."""
        if not self.is_running:
            return
            
        self.observer.stop()
        self.observer.join()
        self.is_running = False
        logger.info("File watcher stopped")
    
    async def wait_for_file_change(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for a file change event.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if a change was detected, False if timeout
        """
        start_time = datetime.now()
        
        while self.is_running:
            # Check timeout
            if timeout and (datetime.now() - start_time).seconds > timeout:
                return False
                
            # Small delay to avoid busy waiting
            await asyncio.sleep(0.1)
            
        return True
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Get statistics about the monitored files."""
        stats = {}
        
        discussion_file = self.watch_paths["discussions"] / "story_discussion.md"
        output_file = self.watch_paths["output"] / "story_output.md"
        
        if discussion_file.exists():
            discussion_stat = discussion_file.stat()
            stats["discussion"] = {
                "size": discussion_stat.st_size,
                "modified": datetime.fromtimestamp(discussion_stat.st_mtime).isoformat(),
                "lines": len(discussion_file.read_text().splitlines())
            }
            
        if output_file.exists():
            output_stat = output_file.stat()
            output_text = output_file.read_text()
            stats["output"] = {
                "size": output_stat.st_size,
                "modified": datetime.fromtimestamp(output_stat.st_mtime).isoformat(),
                "lines": len(output_text.splitlines()),
                "words": len(output_text.split())
            }
            
        return stats