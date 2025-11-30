"""
Memory and Session Management Module

Provides session tracking and context persistence for AI agents.
Implements conversation history management and session state storage.

Author: Ishan
Course: Google-Kaggle 5-Day AI Agents Intensive Course (Capstone Project)
Date: December 2025
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class MemoryManager:
    """
    Manages session state and conversation history for agent interactions.
    
    Tracks user interactions, agent responses, and analysis results across
    the lifecycle of an analysis session. Provides session persistence and
    context retrieval capabilities.
    
    Attributes:
        session_id (str): Unique session identifier (format: session_YYYYMMDD_HHMMSS)
        conversation_history (list): List of conversation messages with metadata
        session_data (dict): Session-level data and analysis results
        max_history_length (int): Maximum number of messages to retain
        
    Example:
        >>> memory = MemoryManager()
        >>> memory.add_message('user', 'Analyze Netflix')
        >>> memory.store_analysis_result('company_name', 'Netflix')
        >>> stats = memory.get_session_stats()
        >>> print(f"Session: {stats['session_id']}")
    """
    
    def __init__(self, session_id: Optional[str] = None, max_history_length: int = 50):
        """
        Initialize memory manager with new or existing session.
        
        Args:
            session_id (str, optional): Existing session ID to restore. If None, creates new.
            max_history_length (int): Maximum conversation messages to retain (default: 50)
        """
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history_length = max_history_length
        
        self.session_data: Dict[str, Any] = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'analysis_count': 0,
            'total_tokens_used': 0
        }
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to conversation history.
        
        Args:
            role (str): Message role ('user', 'agent', 'system')
            content (str): Message content
            metadata (dict, optional): Additional message metadata
            
        Example:
            >>> memory.add_message('user', 'Analyze Tesla')
            >>> memory.add_message('agent', 'Starting analysis...', 
            ...                    metadata={'step': 1, 'agent': 'ResearcherAgent'})
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(message)
        
        # Trim history if exceeds max length
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
        
        self.session_data['last_updated'] = datetime.now().isoformat()
    
    def get_recent_context(self, max_turns: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation messages.
        
        Args:
            max_turns (int): Maximum number of recent messages to return
            
        Returns:
            list: Recent conversation messages
            
        Example:
            >>> recent = memory.get_recent_context(max_turns=5)
            >>> print(f"Last {len(recent)} messages")
        """
        return self.conversation_history[-max_turns:]
    
    def get_context_summary(self) -> str:
        """
        Generate formatted summary of conversation context.
        
        Returns:
            str: Formatted conversation history
            
        Example:
            >>> summary = memory.get_context_summary()
            >>> print(summary)
        """
        summary = f"Session: {self.session_id}\n"
        summary += f"Messages: {len(self.conversation_history)}\n\n"
        
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            summary += f"[{msg['role']}] {msg['content'][:100]}...\n"
        
        return summary
    
    def store_analysis_result(self, key: str, value: Any):
        """
        Store analysis result in session data.
        
        Args:
            key (str): Result key/identifier
            value (Any): Result value (must be JSON-serializable)
            
        Example:
            >>> memory.store_analysis_result('company_name', 'Netflix')
            >>> memory.store_analysis_result('quality_score', 95.5)
        """
        self.session_data[key] = value
        self.session_data['last_updated'] = datetime.now().isoformat()
    
    def get_analysis_result(self, key: str, default: Any = None) -> Any:
        """
        Retrieve stored analysis result.
        
        Args:
            key (str): Result key to retrieve
            default (Any): Default value if key not found
            
        Returns:
            Any: Stored value or default
            
        Example:
            >>> company = memory.get_analysis_result('company_name')
            >>> score = memory.get_analysis_result('quality_score', 0)
        """
        return self.session_data.get(key, default)
    
    def increment_analysis_count(self):
        """
        Increment the count of analyses performed in this session.
        
        Example:
            >>> memory.increment_analysis_count()
        """
        self.session_data['analysis_count'] += 1
        self.session_data['last_updated'] = datetime.now().isoformat()
    
    def add_tokens_used(self, tokens: int):
        """
        Track API token usage.
        
        Args:
            tokens (int): Number of tokens used
            
        Example:
            >>> memory.add_tokens_used(1500)
        """
        self.session_data['total_tokens_used'] += tokens
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics and metadata.
        
        Returns:
            dict: Session statistics including ID, message count, analysis count
            
        Example:
            >>> stats = memory.get_session_stats()
            >>> print(f"Analyses: {stats['analysis_count']}")
        """
        return {
            'session_id': self.session_id,
            'created_at': self.session_data['created_at'],
            'last_updated': self.session_data['last_updated'],
            'message_count': len(self.conversation_history),
            'analysis_count': self.session_data['analysis_count'],
            'total_tokens_used': self.session_data['total_tokens_used']
        }
    
    def save_to_file(self, filepath: Optional[str] = None):
        """
        Persist session data to JSON file.
        
        Args:
            filepath (str, optional): Custom file path. Auto-generated if None.
            
        Example:
            >>> memory.save_to_file('sessions/my_session.json')
        """
        if filepath is None:
            session_dir = Path("sessions")
            session_dir.mkdir(exist_ok=True)
            filepath = session_dir / f"{self.session_id}.json"
        
        data = {
            'session_data': self.session_data,
            'conversation_history': self.conversation_history
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """
        Restore session from JSON file.
        
        Args:
            filepath (str): Path to session file
            
        Example:
            >>> memory.load_from_file('sessions/session_20251201_120000.json')
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.session_data = data['session_data']
        self.conversation_history = data['conversation_history']
        self.session_id = self.session_data['session_id']
    
    def clear_history(self):
        """
        Clear conversation history while preserving session data.
        
        Example:
            >>> memory.clear_history()
        """
        self.conversation_history = []
    
    def reset_session(self):
        """
        Reset session to initial state (new session ID, clear all data).
        
        Example:
            >>> memory.reset_session()
        """
        self.__init__()