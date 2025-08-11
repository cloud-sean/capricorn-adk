# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Enhanced state management utilities for multi-agent coordination."""

from typing import Any, Dict, Optional, List
from google.adk.agents import callback_context as callback_context_module
from google.genai import types
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class StateManager:
    """Manages shared state across agents with namespacing and validation."""
    
    @staticmethod
    def initialize_namespace(
        callback_context: callback_context_module.CallbackContext,
        namespace: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize a namespaced state section."""
        if namespace not in callback_context.state:
            callback_context.state[namespace] = initial_data or {}
            logger.debug(f"Initialized namespace: {namespace}")
    
    @staticmethod
    def get_namespaced(
        callback_context: callback_context_module.CallbackContext,
        namespace: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get value from namespaced state."""
        if namespace in callback_context.state:
            return callback_context.state[namespace].get(key, default)
        return default
    
    @staticmethod
    def set_namespaced(
        callback_context: callback_context_module.CallbackContext,
        namespace: str,
        key: str,
        value: Any
    ) -> None:
        """Set value in namespaced state."""
        if namespace not in callback_context.state:
            callback_context.state[namespace] = {}
        callback_context.state[namespace][key] = value
        logger.debug(f"Set {namespace}.{key} = {type(value).__name__}")
    
    @staticmethod
    def append_to_list(
        callback_context: callback_context_module.CallbackContext,
        namespace: str,
        key: str,
        value: Any
    ) -> None:
        """Append value to a list in namespaced state."""
        if namespace not in callback_context.state:
            callback_context.state[namespace] = {}
        if key not in callback_context.state[namespace]:
            callback_context.state[namespace][key] = []
        callback_context.state[namespace][key].append(value)
    
    @staticmethod
    def increment_counter(
        callback_context: callback_context_module.CallbackContext,
        namespace: str,
        key: str,
        amount: int = 1
    ) -> int:
        """Increment a counter in namespaced state."""
        if namespace not in callback_context.state:
            callback_context.state[namespace] = {}
        current = callback_context.state[namespace].get(key, 0)
        new_value = current + amount
        callback_context.state[namespace][key] = new_value
        return new_value


class PhaseManager:
    """Manages execution phases inspired by gemini-fullstack pattern."""
    
    PHASE_RESEARCH = "[RESEARCH]"
    PHASE_DELIVERABLE = "[DELIVERABLE]"
    PHASE_MODIFIED = "[MODIFIED]"
    PHASE_NEW = "[NEW]"
    
    @staticmethod
    def tag_task(task: str, phase: str, status: Optional[str] = None) -> str:
        """Tag a task with phase and optional status."""
        tags = [phase]
        if status:
            tags.append(status)
        return " ".join(tags) + " " + task
    
    @staticmethod
    def parse_task(tagged_task: str) -> Dict[str, Any]:
        """Parse a tagged task to extract phase, status, and content."""
        parts = tagged_task.split()
        phase = None
        status = None
        content_start = 0
        
        for i, part in enumerate(parts):
            if part in [PhaseManager.PHASE_RESEARCH, PhaseManager.PHASE_DELIVERABLE]:
                phase = part
                content_start = i + 1
            elif part in [PhaseManager.PHASE_MODIFIED, PhaseManager.PHASE_NEW]:
                status = part
                content_start = i + 1
        
        content = " ".join(parts[content_start:]) if content_start < len(parts) else ""
        
        return {
            "phase": phase,
            "status": status,
            "content": content,
            "full_task": tagged_task
        }
    
    @staticmethod
    def filter_by_phase(
        tasks: List[str],
        phase: str
    ) -> List[str]:
        """Filter tasks by phase."""
        filtered = []
        for task in tasks:
            parsed = PhaseManager.parse_task(task)
            if parsed["phase"] == phase:
                filtered.append(task)
        return filtered


class MetricsTracker:
    """Track metrics across agent executions."""
    
    @staticmethod
    def initialize_metrics(
        callback_context: callback_context_module.CallbackContext
    ) -> None:
        """Initialize metrics tracking."""
        if "metrics" not in callback_context.state:
            callback_context.state["metrics"] = {
                "start_time": datetime.now().isoformat(),
                "agents_executed": [],
                "total_papers_found": 0,
                "total_papers_analyzed": 0,
                "total_queries_generated": 0,
                "iteration_count": 0,
                "quality_scores": [],
                "execution_times": {}
            }
    
    @staticmethod
    def record_agent_execution(
        callback_context: callback_context_module.CallbackContext,
        agent_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> None:
        """Record agent execution metrics."""
        MetricsTracker.initialize_metrics(callback_context)
        metrics = callback_context.state["metrics"]
        
        metrics["agents_executed"].append(agent_name)
        execution_time = (end_time - start_time).total_seconds()
        metrics["execution_times"][agent_name] = execution_time
        
        logger.info(f"Agent {agent_name} executed in {execution_time:.2f} seconds")
    
    @staticmethod
    def update_paper_metrics(
        callback_context: callback_context_module.CallbackContext,
        papers_found: int = 0,
        papers_analyzed: int = 0
    ) -> None:
        """Update paper-related metrics."""
        MetricsTracker.initialize_metrics(callback_context)
        metrics = callback_context.state["metrics"]
        
        if papers_found > 0:
            metrics["total_papers_found"] += papers_found
        if papers_analyzed > 0:
            metrics["total_papers_analyzed"] += papers_analyzed
    
    @staticmethod
    def get_summary(
        callback_context: callback_context_module.CallbackContext
    ) -> Dict[str, Any]:
        """Get metrics summary."""
        if "metrics" not in callback_context.state:
            return {}
        
        metrics = callback_context.state["metrics"]
        end_time = datetime.now()
        start_time = datetime.fromisoformat(metrics["start_time"])
        total_time = (end_time - start_time).total_seconds()
        
        return {
            "total_execution_time": f"{total_time:.2f} seconds",
            "agents_executed": len(set(metrics["agents_executed"])),
            "papers_found": metrics["total_papers_found"],
            "papers_analyzed": metrics["total_papers_analyzed"],
            "queries_generated": metrics["total_queries_generated"],
            "iterations": metrics["iteration_count"],
            "average_quality_score": sum(metrics["quality_scores"]) / len(metrics["quality_scores"]) if metrics["quality_scores"] else 0
        }


class CheckpointManager:
    """Manage state checkpoints for recovery and debugging."""
    
    @staticmethod
    def create_checkpoint(
        callback_context: callback_context_module.CallbackContext,
        checkpoint_name: str
    ) -> None:
        """Create a checkpoint of current state."""
        if "checkpoints" not in callback_context.state:
            callback_context.state["checkpoints"] = {}
        
        # Create deep copy of state (excluding checkpoints themselves)
        state_copy = {
            k: v for k, v in callback_context.state.items() 
            if k != "checkpoints"
        }
        
        callback_context.state["checkpoints"][checkpoint_name] = {
            "timestamp": datetime.now().isoformat(),
            "state": json.loads(json.dumps(state_copy, default=str))  # Deep copy with serialization
        }
        
        logger.info(f"Created checkpoint: {checkpoint_name}")
    
    @staticmethod
    def restore_checkpoint(
        callback_context: callback_context_module.CallbackContext,
        checkpoint_name: str
    ) -> bool:
        """Restore state from checkpoint."""
        if "checkpoints" not in callback_context.state:
            logger.warning(f"No checkpoints found")
            return False
        
        if checkpoint_name not in callback_context.state["checkpoints"]:
            logger.warning(f"Checkpoint {checkpoint_name} not found")
            return False
        
        checkpoint = callback_context.state["checkpoints"][checkpoint_name]
        restored_state = checkpoint["state"]
        
        # Clear current state (except checkpoints)
        keys_to_clear = [k for k in callback_context.state.keys() if k != "checkpoints"]
        for key in keys_to_clear:
            del callback_context.state[key]
        
        # Restore state
        for key, value in restored_state.items():
            callback_context.state[key] = value
        
        logger.info(f"Restored checkpoint: {checkpoint_name} from {checkpoint['timestamp']}")
        return True
    
    @staticmethod
    def list_checkpoints(
        callback_context: callback_context_module.CallbackContext
    ) -> List[Dict[str, str]]:
        """List available checkpoints."""
        if "checkpoints" not in callback_context.state:
            return []
        
        checkpoints = []
        for name, data in callback_context.state["checkpoints"].items():
            checkpoints.append({
                "name": name,
                "timestamp": data["timestamp"]
            })
        
        return checkpoints