"""
Persona and Job Analysis Module
"""

import re
from typing import Dict, List, Set, Any
import logging

logger = logging.getLogger(__name__)

class PersonaAnalyzer:
    """Analyzes persona characteristics and job requirements"""
    
    def __init__(self):
        self.persona_patterns = {
            'researcher': {
                'keywords': ['research', 'phd', 'academic', 'scholar', 'scientist', 'investigation'],
                'focus_areas': ['methodology', 'literature', 'analysis', 'findings', 'hypothesis', 'experiment', 'study', 'data', 'results', 'conclusion'],
                'expertise_weight': 0.9
            },
            'student': {
                'keywords': ['student', 'undergraduate', 'graduate', 'learner', 'pupil'],
                'focus_areas': ['concepts', 'basics', 'fundamentals', 'definition', 'example', 'tutorial', 'guide', 'introduction', 'overview'],
                'expertise_weight': 0.6
            },
            'analyst': {
                'keywords': ['analyst', 'analysis', 'business', 'financial', 'investment', 'strategic'],
                'focus_areas': ['trends', 'metrics', 'performance', 'roi', 'revenue', 'growth', 'market', 'competitive', 'risk', 'forecast'],
                'expertise_weight': 0.8
            },
            'engineer': {
                'keywords': ['engineer', 'technical', 'developer', 'architect', 'designer'],
                'focus_areas': ['implementation', 'design', 'architecture', 'technical', 'specification', 'requirements', 'solution', 'system'],
                'expertise_weight': 0.85
            },
            'manager': {
                'keywords': ['manager', 'director', 'executive', 'leader', 'supervisor'],
                'focus_areas': ['strategy', 'planning', 'execution', 'team', 'process', 'efficiency', 'goals', 'objectives', 'performance'],
                'expertise_weight': 0.7
            },
            'consultant': {
                'keywords': ['consultant', 'advisor', 'expert', 'specialist'],
                'focus_areas': ['recommendations', 'best practices', 'optimization', 'improvement', 'strategy', 'solution', 'assessment'],
                'expertise_weight': 0.8
            },
            'journalist': {
                'keywords': ['journalist', 'reporter', 'writer', 'editor'],
                'focus_areas': ['facts', 'events', 'timeline', 'background', 'context', 'impact', 'significance', 'quotes', 'sources'],
                'expertise_weight': 0.7
            },
            'entrepreneur': {
                'keywords': ['entrepreneur', 'founder', 'startup', 'business owner'],
                'focus_areas': ['opportunity', 'market', 'innovation', 'scaling', 'growth', 'investment', 'business model', 'competition'],
                'expertise_weight': 0.75
            }
        }
        
        self.job_action_patterns = {
            'analyze': ['analyze', 'analysis', 'examine', 'evaluate', 'assess', 'review'],
            'summarize': ['summarize', 'summary', 'overview', 'abstract', 'brief', 'condense'],
            'compare': ['compare', 'comparison', 'contrast', 'versus', 'vs', 'difference', 'similarity'],
            'extract': ['extract', 'identify', 'find', 'locate', 'discover', 'retrieve'],
            'prepare': ['prepare', 'create', 'develop', 'build', 'generate', 'produce'],
            'understand': ['understand', 'comprehend', 'learn', 'grasp', 'study'],
            'research': ['research', 'investigate', 'explore', 'survey', 'study'],
            'report': ['report', 'document', 'record', 'compile', 'present']
        }
        
        self.domain_indicators = {
            'academic': ['paper', 'journal', 'conference', 'citation', 'publication', 'peer review', 'abstract', 'methodology'],
            'business': ['revenue', 'profit', 'market', 'customer', 'sales', 'growth', 'strategy', 'roi', 'kpi'],
            'technical': ['algorithm', 'system', 'architecture', 'implementation', 'code', 'framework', 'api', 'database'],
            'medical': ['patient', 'treatment', 'diagnosis', 'clinical', 'therapy', 'medical', 'health', 'disease'],
            'legal': ['law', 'regulation', 'compliance', 'legal', 'contract', 'agreement', 'statute', 'policy'],
            'financial': ['investment', 'portfolio', 'asset', 'liability', 'financial', 'accounting', 'audit', 'tax'],
            'educational': ['curriculum', 'learning', 'education', 'teaching', 'course', 'syllabus', 'academic', 'assessment']
        }
    
    def analyze_persona(self, persona_text: str) -> Dict[str, Any]:
        """Analyze persona characteristics and determine expertise areas"""
        persona_lower = persona_text.lower()
        
        # Identify persona type
        persona_type = self._identify_persona_type(persona_lower)
        
        # Extract expertise areas
        expertise_areas = self._extract_expertise_areas(persona_lower, persona_type)
        
        # Determine domain focus
        domain_focus = self._identify_domain_focus(persona_lower)
        
        # Extract experience level indicators
        experience_level = self._assess_experience_level(persona_lower)
        
        profile = {
            'persona_type': persona_type,
            'expertise_areas': expertise_areas,
            'domain_focus': domain_focus,
            'experience_level': experience_level,
            'focus_keywords': self._generate_focus_keywords(persona_type, domain_focus),
            'expertise_weight': self.persona_patterns.get(persona_type, {}).get('expertise_weight', 0.7)
        }
        
        logger.info(f"Persona analysis: {persona_type} in {domain_focus} domain")
        return profile
    
    def analyze_job(self, job_text: str) -> Dict[str, Any]:
        """Analyze job requirements and extract key objectives"""
        job_lower = job_text.lower()
        
        # Identify primary actions
        primary_actions = self._identify_job_actions(job_lower)
        
        # Extract target keywords
        keywords = self._extract_job_keywords(job_text)
        
        # Identify content preferences
        content_preferences = self._identify_content_preferences(job_lower)
        
        # Determine urgency/importance indicators
        priority_indicators = self._extract_priority_indicators(job_lower)
        
        # Extract specific requirements
        specific_requirements = self._extract_specific_requirements(job_text)
        
        job_profile = {
            'primary_actions': primary_actions,
            'keywords': keywords,
            'content_preferences': content_preferences,
            'priority_indicators': priority_indicators,
            'specific_requirements': specific_requirements,
            'action_weights': self._calculate_action_weights(primary_actions)
        }
        
        logger.info(f"Job analysis: {primary_actions[:2]} with focus on {keywords[:3]}")
        return job_profile
    
    def _identify_persona_type(self, persona_text: str) -> str:
        """Identify the primary persona type"""
        scores = {}
        
        for persona_type, patterns in self.persona_patterns.items():
            score = 0
            for keyword in patterns['keywords']:
                if keyword in persona_text:
                    score += 1
            scores[persona_type] = score
        
        # Return the highest scoring persona type, or 'analyst' as default
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'analyst'
    
    def _extract_expertise_areas(self, persona_text: str, persona_type: str) -> List[str]:
        """Extract specific areas of expertise"""
        expertise_areas = []
        
        # Add persona-specific focus areas
        if persona_type in self.persona_patterns:
            expertise_areas.extend(self.persona_patterns[persona_type]['focus_areas'])
        
        # Extract domain-specific terms
        for domain, indicators in self.domain_indicators.items():
            if any(indicator in persona_text for indicator in indicators):
                expertise_areas.extend(indicators[:5])  # Top 5 indicators
        
        # Remove duplicates and return top areas
        return list(dict.fromkeys(expertise_areas))[:15]
    
    def _identify_domain_focus(self, persona_text: str) -> str:
        """Identify the primary domain of focus"""
        domain_scores = {}
        
        for domain, indicators in self.domain_indicators.items():
            score = sum(1 for indicator in indicators if indicator in persona_text)
            if score > 0:
                domain_scores[domain] = score
        
        return max(domain_scores, key=domain_scores.get) if domain_scores else 'general'
    
    def _assess_experience_level(self, persona_text: str) -> str:
        """Assess experience level from persona description"""
        if any(term in persona_text for term in ['phd', 'senior', 'lead', 'principal', 'expert', 'director']):
            return 'expert'
        elif any(term in persona_text for term in ['junior', 'entry', 'beginner', 'student', 'new']):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _generate_focus_keywords(self, persona_type: str, domain_focus: str) -> List[str]:
        """Generate focused keywords based on persona and domain"""
        keywords = []
        
        if persona_type in self.persona_patterns:
            keywords.extend(self.persona_patterns[persona_type]['focus_areas'][:10])
        
        if domain_focus in self.domain_indicators:
            keywords.extend(self.domain_indicators[domain_focus][:8])
        
        return list(dict.fromkeys(keywords))
    
    def _identify_job_actions(self, job_text: str) -> List[str]:
        """Identify primary actions required in the job"""
        actions_found = []
        
        for action_type, action_words in self.job_action_patterns.items():
            if any(word in job_text for word in action_words):
                actions_found.append(action_type)
        
        # If no specific actions found, default to analyze and extract
        return actions_found if actions_found else ['analyze', 'extract']
    
    def _extract_job_keywords(self, job_text: str) -> List[str]:
        """Extract important keywords from job description"""
        # Remove common stop words and extract meaningful terms
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'under', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}
        
        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', job_text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequency and return most common
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(20)]
    
    def _identify_content_preferences(self, job_text: str) -> Dict[str, float]:
        """Identify what type of content is preferred"""
        preferences = {
            'quantitative': 0.5,  # Numbers, data, statistics
            'qualitative': 0.5,   # Descriptions, explanations
            'methodological': 0.5, # Processes, procedures
            'theoretical': 0.5,    # Concepts, frameworks
            'practical': 0.5       # Examples, applications
        }
        
        # Adjust based on job text
        if any(term in job_text for term in ['data', 'statistics', 'numbers', 'metrics', 'quantitative']):
            preferences['quantitative'] += 0.3
        
        if any(term in job_text for term in ['methodology', 'method', 'process', 'procedure', 'approach']):
            preferences['methodological'] += 0.3
        
        if any(term in job_text for term in ['example', 'practical', 'application', 'case study', 'implementation']):
            preferences['practical'] += 0.3
        
        if any(term in job_text for term in ['theory', 'concept', 'framework', 'model', 'principle']):
            preferences['theoretical'] += 0.3
        
        return preferences
    
    def _extract_priority_indicators(self, job_text: str) -> List[str]:
        """Extract indicators of what's most important"""
        priority_terms = []
        
        # Look for explicit priority indicators
        priority_patterns = [
            r'focus(?:ing)? on ([^.]+)',
            r'primarily ([^.]+)',
            r'especially ([^.]+)',
            r'particularly ([^.]+)',
            r'emphasize ([^.]+)',
            r'key ([^.]+)',
            r'main ([^.]+)',
            r'important ([^.]+)'
        ]
        
        for pattern in priority_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            priority_terms.extend([match.strip() for match in matches])
        
        return priority_terms[:10]
    
    def _extract_specific_requirements(self, job_text: str) -> List[str]:
        """Extract specific requirements or constraints"""
        requirements = []
        
        # Look for specific requirement patterns
        requirement_patterns = [
            r'must include ([^.]+)',
            r'should contain ([^.]+)',
            r'need(?:s)? to ([^.]+)',
            r'require(?:s|d) ([^.]+)',
            r'looking for ([^.]+)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            requirements.extend([match.strip() for match in matches])
        
        return requirements[:10]
    
    def _calculate_action_weights(self, actions: List[str]) -> Dict[str, float]:
        """Calculate weights for different actions"""
        weights = {
            'analyze': 0.9,
            'summarize': 0.7,
            'compare': 0.8,
            'extract': 0.8,
            'prepare': 0.6,
            'understand': 0.6,
            'research': 0.9,
            'report': 0.7
        }
        
        action_weights = {}
        for action in actions:
            action_weights[action] = weights.get(action, 0.7)
        
        return action_weights