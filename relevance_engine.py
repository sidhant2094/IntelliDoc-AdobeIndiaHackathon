"""
Advanced Relevance Engine with Multi-dimensional Scoring
"""

import re
import math
from typing import Dict, List, Any, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class RelevanceEngine:
    """Advanced relevance scoring engine with multiple dimensions"""
    
    def __init__(self):
        self.content_type_patterns = {
            'methodology': [
                'method', 'approach', 'technique', 'procedure', 'process', 'algorithm',
                'framework', 'model', 'strategy', 'protocol', 'workflow'
            ],
            'results': [
                'result', 'finding', 'outcome', 'conclusion', 'evidence', 'data',
                'statistics', 'measurement', 'observation', 'discovery'
            ],
            'background': [
                'introduction', 'background', 'overview', 'context', 'history',
                'literature', 'previous', 'existing', 'current', 'established'
            ],
            'analysis': [
                'analysis', 'evaluation', 'assessment', 'examination', 'comparison',
                'interpretation', 'discussion', 'review', 'critique', 'investigation'
            ],
            'examples': [
                'example', 'case', 'instance', 'illustration', 'demonstration',
                'sample', 'scenario', 'application', 'implementation', 'practice'
            ],
            'summary': [
                'summary', 'conclusion', 'abstract', 'overview', 'recap',
                'synthesis', 'key points', 'main findings', 'highlights'
            ]
        }
        
        # Weights for different scoring dimensions
        self.dimension_weights = {
            'semantic_similarity': 0.35,
            'keyword_overlap': 0.25,
            'content_type_match': 0.20,
            'expertise_alignment': 0.15,
            'structural_importance': 0.05
        }
    
    def score_sections(self, sections: List[Dict], persona_profile: Dict, 
                      job_requirements: Dict, custom_weights: Dict = None) -> List[Dict]:
        """Score all sections and return them ranked by relevance"""
        logger.info(f"Scoring {len(sections)} sections...")
        
        scored_sections = []
        
        for section in sections:
            try:
                score = self._calculate_comprehensive_score(
                    section, persona_profile, job_requirements, custom_weights
                )
                
                section_with_score = section.copy()
                section_with_score['relevance_score'] = score
                section_with_score['score_breakdown'] = self._get_score_breakdown(
                    section, persona_profile, job_requirements
                )
                
                scored_sections.append(section_with_score)
                
            except Exception as e:
                logger.warning(f"Error scoring section '{section.get('title', 'Unknown')}': {e}")
                section['relevance_score'] = 0.0
                scored_sections.append(section)
        
        # Sort by relevance score (highest first)
        scored_sections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Top section score: {scored_sections[0].get('relevance_score', 0):.3f}")
        logger.info(f"Median section score: {scored_sections[len(scored_sections)//2].get('relevance_score', 0):.3f}")
        
        return scored_sections
    
    def extract_subsections(self, top_sections: List[Dict], persona_profile: Dict, 
                          job_requirements: Dict, max_subsections: int = 30) -> List[Dict]:
        """Extract relevant subsections from top sections"""
        logger.info(f"Extracting subsections from {len(top_sections)} top sections...")
        
        subsections = []
        
        for section in top_sections:
            try:
                section_subsections = self._extract_section_subsections(
                    section, persona_profile, job_requirements
                )
                subsections.extend(section_subsections)
                
            except Exception as e:
                logger.warning(f"Error extracting subsections from '{section.get('title', 'Unknown')}': {e}")
                continue
        
        # Score and rank subsections
        for subsection in subsections:
            subsection['relevance_score'] = self._score_subsection(
                subsection, persona_profile, job_requirements
            )
        
        # Sort by relevance and limit
        subsections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Extracted {len(subsections[:max_subsections])} subsections")
        return subsections[:max_subsections]
    
    def _calculate_comprehensive_score(self, section: Dict, persona_profile: Dict, 
                                     job_requirements: Dict, custom_weights: Dict = None) -> float:
        """Calculate comprehensive relevance score"""
        
        # Merge and normalize weights
        weights = self.dimension_weights.copy()
        if custom_weights:
            weights.update(custom_weights)
            
            # Normalize weights defensively
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v / total_weight for k, v in weights.items()}
            else:
                # Fallback to defaults if sum is 0
                weights = self.dimension_weights.copy()
        
        # 1. Semantic similarity (simplified TF-IDF approach)
        semantic_score = self._calculate_semantic_similarity(
            section, persona_profile, job_requirements
        )
        
        # 2. Keyword overlap
        keyword_score = self._calculate_keyword_overlap(
            section, persona_profile, job_requirements
        )
        
        # 3. Content type matching
        content_type_score = self._calculate_content_type_match(
            section, job_requirements
        )
        
        # 4. Expertise alignment
        expertise_score = self._calculate_expertise_alignment(
            section, persona_profile
        )
        
        # 5. Structural importance
        structural_score = self._calculate_structural_importance(section)
        
        # Weighted combination
        total_score = (
            weights['semantic_similarity'] * semantic_score +
            weights['keyword_overlap'] * keyword_score +
            weights['content_type_match'] * content_type_score +
            weights['expertise_alignment'] * expertise_score +
            weights['structural_importance'] * structural_score
        )
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    def _calculate_semantic_similarity(self, section: Dict, persona_profile: Dict, 
                                     job_requirements: Dict) -> float:
        """Calculate semantic similarity using keyword overlap and TF-IDF concepts"""
        section_text = (section.get('title', '') + ' ' + section.get('content', '')).lower()
        
        # Combine persona and job keywords
        target_keywords = (
            persona_profile.get('focus_keywords', []) + 
            job_requirements.get('keywords', [])
        )
        
        if not target_keywords:
            return 0.0
        
        # Count keyword occurrences
        keyword_matches = 0
        total_keywords = len(target_keywords)
        
        for keyword in target_keywords:
            if keyword.lower() in section_text:
                keyword_matches += 1
        
        # Basic similarity score
        similarity = keyword_matches / total_keywords
        
        # Boost for multiple occurrences of important keywords
        boost = 0
        for keyword in persona_profile.get('expertise_areas', [])[:5]:
            occurrences = section_text.count(keyword.lower())
            if occurrences > 1:
                boost += min(occurrences * 0.1, 0.3)
        
        return min(similarity + boost, 1.0)
    
    def _calculate_keyword_overlap(self, section: Dict, persona_profile: Dict, 
                                 job_requirements: Dict) -> float:
        """Calculate direct keyword overlap score"""
        section_text = (section.get('title', '') + ' ' + section.get('content', '')).lower()
        
        # Extract words from section
        section_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', section_text))
        
        # Combine all target keywords
        target_keywords = set()
        target_keywords.update(word.lower() for word in persona_profile.get('expertise_areas', []))
        target_keywords.update(word.lower() for word in job_requirements.get('keywords', []))
        target_keywords.update(word.lower() for word in persona_profile.get('focus_keywords', []))
        
        if not target_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(section_words.intersection(target_keywords))
        union = len(section_words.union(target_keywords))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_content_type_match(self, section: Dict, job_requirements: Dict) -> float:
        """Calculate how well section content type matches job requirements"""
        section_text = (section.get('title', '') + ' ' + section.get('content', '')).lower()
        
        # Identify section content type
        section_content_types = []
        for content_type, patterns in self.content_type_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in section_text)
            if matches > 0:
                section_content_types.append((content_type, matches))
        
        if not section_content_types:
            return 0.5  # Neutral score if can't identify content type
        
        # Sort by match count
        section_content_types.sort(key=lambda x: x[1], reverse=True)
        primary_content_type = section_content_types[0][0]
        
        # Check if this content type aligns with job requirements
        job_actions = job_requirements.get('primary_actions', [])
        content_preferences = job_requirements.get('content_preferences', {})
        
        # Map actions to preferred content types
        action_content_mapping = {
            'analyze': ['analysis', 'methodology', 'results'],
            'summarize': ['summary', 'background'],
            'compare': ['analysis', 'results'],
            'extract': ['results', 'examples', 'methodology'],
            'research': ['background', 'methodology', 'analysis'],
            'understand': ['background', 'examples', 'summary']
        }
        
        score = 0.5  # Base score
        
        for action in job_actions:
            if action in action_content_mapping:
                if primary_content_type in action_content_mapping[action]:
                    score += 0.3
        
        # Add preference-based scoring
        if primary_content_type == 'methodology' and content_preferences.get('methodological', 0) > 0.6:
            score += 0.2
        elif primary_content_type == 'examples' and content_preferences.get('practical', 0) > 0.6:
            score += 0.2
        elif primary_content_type == 'results' and content_preferences.get('quantitative', 0) > 0.6:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_expertise_alignment(self, section: Dict, persona_profile: Dict) -> float:
        """Calculate alignment with persona expertise"""
        section_text = (section.get('title', '') + ' ' + section.get('content', '')).lower()
        
        expertise_areas = persona_profile.get('expertise_areas', [])
        if not expertise_areas:
            return 0.5
        
        # Count mentions of expertise areas
        expertise_matches = 0
        for area in expertise_areas:
            if area.lower() in section_text:
                expertise_matches += 1
        
        # Calculate alignment score
        alignment = expertise_matches / len(expertise_areas)
        
        # Apply expertise weight from persona
        expertise_weight = persona_profile.get('expertise_weight', 0.7)
        
        return alignment * expertise_weight
    
    def _calculate_structural_importance(self, section: Dict) -> float:
        """Calculate importance based on document structure"""
        level = section.get('level', 'H3')
        section_type = section.get('type', 'section')
        
        # Level-based scoring
        level_scores = {'title': 0.9, 'H1': 0.8, 'H2': 0.7, 'H3': 0.6}
        level_score = level_scores.get(level, 0.5)
        
        # Type-based scoring
        type_scores = {'title': 0.9, 'section': 0.7, 'page_section': 0.5}
        type_score = type_scores.get(section_type, 0.5)
        
        # Length-based scoring (longer sections might be more comprehensive)
        content_length = len(section.get('content', ''))
        length_score = min(content_length / 1000, 0.8)  # Cap at 0.8
        
        return (level_score + type_score + length_score) / 3
    
    def _get_score_breakdown(self, section: Dict, persona_profile: Dict, 
                           job_requirements: Dict) -> Dict[str, float]:
        """Get detailed score breakdown for debugging"""
        return {
            'semantic_similarity': self._calculate_semantic_similarity(section, persona_profile, job_requirements),
            'keyword_overlap': self._calculate_keyword_overlap(section, persona_profile, job_requirements),
            'content_type_match': self._calculate_content_type_match(section, job_requirements),
            'expertise_alignment': self._calculate_expertise_alignment(section, persona_profile),
            'structural_importance': self._calculate_structural_importance(section)
        }
    
    def _extract_section_subsections(self, section: Dict, persona_profile: Dict, 
                                   job_requirements: Dict) -> List[Dict]:
        """Extract meaningful subsections from a section"""
        content = section.get('content', '')
        if len(content) < 200:  # Too short to split meaningfully
            return []
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 2:
            # Try splitting by sentences if no paragraph breaks
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            if len(sentences) < 3:
                return []
            # Group sentences into chunks
            paragraphs = []
            for i in range(0, len(sentences), 3):
                chunk = '. '.join(sentences[i:i+3]) + '.'
                if len(chunk) > 100:  # Only include substantial chunks
                    paragraphs.append(chunk)
        
        subsections = []
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 100:  # Only consider substantial paragraphs
                # Create a title from first few words or use position
                words = paragraph.split()[:8]
                title = ' '.join(words) + '...' if len(words) == 8 else ' '.join(words)
                
                subsections.append({
                    'document': section['document'],
                    'page': section['page'],
                    'title': title,
                    'text': paragraph,
                    'parent_section': section.get('title', 'Unknown'),
                    'subsection_index': i
                })
        
        return subsections
    
    def _score_subsection(self, subsection: Dict, persona_profile: Dict, 
                         job_requirements: Dict) -> float:
        """Score individual subsection relevance"""
        text = subsection.get('text', '').lower()
        
        # Keyword matching
        target_keywords = (
            persona_profile.get('focus_keywords', []) + 
            job_requirements.get('keywords', [])
        )
        
        keyword_matches = 0
        for keyword in target_keywords[:10]:  # Top 10 keywords
            if keyword.lower() in text:
                keyword_matches += 1
        
        keyword_score = keyword_matches / min(len(target_keywords), 10) if target_keywords else 0
        
        # Length consideration (prefer substantial but not overly long content)
        length = len(text)
        if length < 50:
            length_score = 0.2
        elif length > 1000:
            length_score = 0.6
        else:
            length_score = min(length / 500, 1.0)
        
        # Combine scores
        return (keyword_score * 0.7 + length_score * 0.3)