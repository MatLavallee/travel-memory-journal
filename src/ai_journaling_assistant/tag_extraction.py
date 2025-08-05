"""Travel Memory Journal tag extraction service."""

import re
from typing import List, Dict, Optional

from ai_journaling_assistant.config import get_tag_categories


class TagExtractor:
    """Rule-based tag extraction for travel memory descriptions.
    
    Implements ADR-0002 rule-based approach for extracting meaningful
    tags from natural language travel descriptions.
    """
    
    def __init__(self):
        """Initialize with travel-specific keyword dictionaries."""
        self.categories = get_tag_categories()
        
        # Create reverse lookup for efficient category identification
        self._keyword_to_categories = {}
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword not in self._keyword_to_categories:
                    self._keyword_to_categories[keyword] = []
                self._keyword_to_categories[keyword].append(category)
    
    def extract_tags(self, description: str, categories: Optional[List[str]] = None) -> List[str]:
        """Extract tags from memory description using rule-based approach.
        
        Args:
            description: Natural language description of travel memory.
            categories: Optional list of categories to filter by.
            
        Returns:
            List of extracted tags, deduplicated and relevant to travel.
        """
        if not description or not description.strip():
            return []
        
        # Preprocess text for better matching
        processed_text = self._preprocess_text(description)
        
        # Find matching keywords
        found_tags = self._find_keywords(processed_text, categories)
        
        # Remove duplicates while preserving order
        unique_tags = []
        seen = set()
        for tag in found_tags:
            if tag not in seen:
                unique_tags.append(tag)
                seen.add(tag)
        
        return unique_tags
    
    def extract_tags_by_category(self, description: str) -> Dict[str, List[str]]:
        """Extract tags organized by category.
        
        Args:
            description: Natural language description of travel memory.
            
        Returns:
            Dictionary mapping category names to lists of extracted tags.
        """
        all_tags = self.extract_tags(description)
        
        categorized = {}
        for category in self.categories.keys():
            categorized[category] = []
        
        for tag in all_tags:
            if tag in self._keyword_to_categories:
                for category in self._keyword_to_categories[tag]:
                    if tag not in categorized[category]:
                        categorized[category].append(tag)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text for tag extraction.
        
        Args:
            text: Raw text to preprocess.
            
        Returns:
            Cleaned and normalized text ready for keyword matching.
        """
        # Convert to lowercase for case-insensitive matching
        text = text.lower()
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _find_keywords(self, text: str, filter_categories: Optional[List[str]] = None) -> List[str]:
        """Find matching keywords in preprocessed text.
        
        Args:
            text: Preprocessed text to search.
            filter_categories: Optional categories to limit search to.
            
        Returns:
            List of found keywords/tags.
        """
        found_tags = []
        
        # Determine which categories to search
        categories_to_search = filter_categories or self.categories.keys()
        
        for category in categories_to_search:
            if category not in self.categories:
                continue
                
            for keyword in self.categories[category]:
                keyword_lower = keyword.lower()
                
                # Try exact match first
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text):
                    found_tags.append(keyword)
                    continue
                
                # Try variations for single words
                if ' ' not in keyword_lower:
                    # Handle common variations
                    variations = []
                    
                    # Plural patterns
                    variations.extend([
                        keyword_lower + 's',      # mountain -> mountains
                        keyword_lower + 'es',     # beach -> beaches
                    ])
                    
                    # Handle -y to -ies
                    if keyword_lower.endswith('y'):
                        variations.append(keyword_lower[:-1] + 'ies')  # city -> cities
                    
                    # Handle verb forms for -ing words
                    if keyword_lower.endswith('ing'):
                        base = keyword_lower[:-3]  # walking -> walk
                        variations.extend([
                            base,                  # walking -> walk
                            base + 'ed',          # walking -> walked
                            base + 's',           # walking -> walks
                        ])
                    
                    # Handle base verbs to -ing forms
                    else:
                        variations.extend([
                            keyword_lower + 'ing',  # walk -> walking
                            keyword_lower + 'ed',   # walk -> walked
                        ])
                        # Handle doubled consonants
                        if len(keyword_lower) > 2 and keyword_lower[-1] == keyword_lower[-2]:
                            variations.append(keyword_lower + 'ing')  # run -> running
                    
                    for variation in variations:
                        if variation:
                            variation_pattern = r'\b' + re.escape(variation) + r'\b'
                            if re.search(variation_pattern, text):
                                found_tags.append(keyword)
                                break
        
        return found_tags