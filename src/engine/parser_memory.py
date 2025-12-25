"""
Parser Memory - Tracks player input history for context-aware branching.

Maintains a circular buffer of recent commands and provides keyword/pattern matching
for dynamic scene branching based on player exploration and dialogue.
"""

import re
from collections import deque
from typing import List, Set, Optional, Dict


class ParserMemory:
    """Tracks player input history for context-aware scene branching."""
    
    def __init__(self, buffer_size: int = 20):
        """
        Initialize parser memory.
        
        Args:
            buffer_size: Maximum number of commands to remember
        """
        self.buffer_size = buffer_size
        self.command_buffer = deque(maxlen=buffer_size)
        self.discovered_concepts = set()
        self.keyword_counts = {}
        self.pattern_cache = {}
        
    def add_command(self, command_text: str):
        """
        Add a command to the memory buffer.
        
        Args:
            command_text: Raw player input
        """
        if not command_text or not command_text.strip():
            return
            
        normalized = command_text.lower().strip()
        self.command_buffer.append(normalized)
        
        # Update keyword counts
        words = self._extract_keywords(normalized)
        for word in words:
            self.keyword_counts[word] = self.keyword_counts.get(word, 0) + 1
        
        # Clear pattern cache when new command added
        self.pattern_cache.clear()
    
    def has_mentioned(self, keyword: str, min_count: int = 1) -> bool:
        """
        Check if a keyword has been mentioned.
        
        Args:
            keyword: Keyword to search for (case-insensitive)
            min_count: Minimum number of mentions required
            
        Returns:
            True if keyword mentioned at least min_count times
        """
        normalized = keyword.lower()
        count = self.keyword_counts.get(normalized, 0)
        return count >= min_count
    
    def has_pattern(self, regex_pattern: str) -> bool:
        """
        Check if any command matches a regex pattern.
        
        Args:
            regex_pattern: Regular expression pattern
            
        Returns:
            True if any command matches the pattern
        """
        # Check cache
        if regex_pattern in self.pattern_cache:
            return self.pattern_cache[regex_pattern]
        
        try:
            compiled = re.compile(regex_pattern, re.IGNORECASE)
            for command in self.command_buffer:
                if compiled.search(command):
                    self.pattern_cache[regex_pattern] = True
                    return True
        except re.error:
            # Invalid regex
            pass
        
        self.pattern_cache[regex_pattern] = False
        return False
    
    def has_mentioned_all(self, keywords: List[str]) -> bool:
        """
        Check if all keywords have been mentioned.
        
        Args:
            keywords: List of keywords
            
        Returns:
            True if all keywords mentioned
        """
        return all(self.has_mentioned(kw) for kw in keywords)
    
    def has_mentioned_any(self, keywords: List[str]) -> bool:
        """
        Check if any keyword has been mentioned.
        
        Args:
            keywords: List of keywords
            
        Returns:
            True if any keyword mentioned
        """
        return any(self.has_mentioned(kw) for kw in keywords)
    
    def get_recent_commands(self, count: int = 5) -> List[str]:
        """
        Get the most recent commands.
        
        Args:
            count: Number of commands to retrieve
            
        Returns:
            List of recent commands (newest first)
        """
        return list(reversed(list(self.command_buffer)))[:count]
    
    def get_discovered_concepts(self) -> Set[str]:
        """
        Get all discovered concepts.
        
        Returns:
            Set of concept IDs
        """
        return self.discovered_concepts.copy()
    
    def mark_concept_discovered(self, concept_id: str):
        """
        Mark a concept as discovered.
        
        Args:
            concept_id: Concept identifier
        """
        self.discovered_concepts.add(concept_id)
    
    def has_concept(self, concept_id: str) -> bool:
        """
        Check if a concept has been discovered.
        
        Args:
            concept_id: Concept identifier
            
        Returns:
            True if concept discovered
        """
        return concept_id in self.discovered_concepts
    
    def check_trigger_phrases(self, triggers: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Check which trigger phrases have been activated.
        
        Args:
            triggers: List of trigger dictionaries with 'keywords' or 'pattern'
            
        Returns:
            List of activated triggers
        """
        activated = []
        
        for trigger in triggers:
            # Check keyword-based triggers
            if "keywords" in trigger:
                keywords = trigger["keywords"]
                if isinstance(keywords, str):
                    keywords = [keywords]
                
                mode = trigger.get("mode", "all")  # 'all' or 'any'
                
                if mode == "all":
                    if self.has_mentioned_all(keywords):
                        activated.append(trigger)
                else:  # any
                    if self.has_mentioned_any(keywords):
                        activated.append(trigger)
            
            # Check pattern-based triggers
            elif "pattern" in trigger:
                if self.has_pattern(trigger["pattern"]):
                    activated.append(trigger)
        
        return activated
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract meaningful keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'them', 'their', 'this', 'that',
            'these', 'those', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
        
        # Split and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def get_keyword_frequency(self, keyword: str) -> int:
        """
        Get the frequency of a keyword.
        
        Args:
            keyword: Keyword to check
            
        Returns:
            Number of times keyword was mentioned
        """
        return self.keyword_counts.get(keyword.lower(), 0)
    
    def get_top_keywords(self, count: int = 10) -> List[tuple]:
        """
        Get the most frequently mentioned keywords.
        
        Args:
            count: Number of keywords to return
            
        Returns:
            List of (keyword, frequency) tuples
        """
        sorted_keywords = sorted(
            self.keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_keywords[:count]
    
    def clear(self):
        """Clear all memory."""
        self.command_buffer.clear()
        self.discovered_concepts.clear()
        self.keyword_counts.clear()
        self.pattern_cache.clear()
    
    def save_state(self) -> dict:
        """
        Save parser memory state.
        
        Returns:
            Dictionary of state data
        """
        return {
            "commands": list(self.command_buffer),
            "discovered_concepts": list(self.discovered_concepts),
            "keyword_counts": self.keyword_counts.copy()
        }
    
    def load_state(self, state: dict):
        """
        Load parser memory state.
        
        Args:
            state: State dictionary from save_state()
        """
        self.command_buffer = deque(state.get("commands", []), maxlen=self.buffer_size)
        self.discovered_concepts = set(state.get("discovered_concepts", []))
        self.keyword_counts = state.get("keyword_counts", {}).copy()
        self.pattern_cache.clear()
    
    def __repr__(self) -> str:
        return f"<ParserMemory: {len(self.command_buffer)} commands, {len(self.discovered_concepts)} concepts>"
