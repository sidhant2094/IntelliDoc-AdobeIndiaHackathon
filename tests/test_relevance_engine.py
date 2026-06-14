import unittest
import sys
import os
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from relevance_engine import RelevanceEngine

class TestRelevanceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RelevanceEngine()
        self.persona_profile = {
            'expertise_areas': ['AI', 'Machine Learning'],
            'focus_keywords': ['neural networks', 'deep learning'],
            'expertise_weight': 0.8
        }
        self.job_requirements = {
            'keywords': ['model', 'accuracy'],
            'primary_actions': ['analyze'],
            'content_preferences': {'quantitative': 0.8}
        }
        self.section = {
            'title': 'Model Accuracy Analysis',
            'content': 'We analyzed the model accuracy using deep learning and neural networks.',
            'level': 'H2',
            'type': 'section',
            'document': 'doc1.pdf',
            'page': 1
        }

    def test_default_weights(self):
        score = self.engine._calculate_comprehensive_score(self.section, self.persona_profile, self.job_requirements)
        self.assertTrue(0.0 <= score <= 1.0)
        
    def test_custom_weights_normalization(self):
        # Weights that sum to 2.0 -> should be normalized to sum to 1.0 (each weight 0.5)
        custom_weights = {
            'semantic_similarity': 1.0,
            'keyword_overlap': 1.0,
            'content_type_match': 0.0,
            'expertise_alignment': 0.0,
            'structural_importance': 0.0
        }
        score = self.engine._calculate_comprehensive_score(
            self.section, self.persona_profile, self.job_requirements, custom_weights
        )
        self.assertTrue(0.0 <= score <= 1.0)
        
    def test_custom_weights_zero_sum(self):
        # Weights that sum to 0 -> should fallback to defaults
        custom_weights = {
            'semantic_similarity': 0.0,
            'keyword_overlap': 0.0,
            'content_type_match': 0.0,
            'expertise_alignment': 0.0,
            'structural_importance': 0.0
        }
        score_custom = self.engine._calculate_comprehensive_score(
            self.section, self.persona_profile, self.job_requirements, custom_weights
        )
        score_default = self.engine._calculate_comprehensive_score(
            self.section, self.persona_profile, self.job_requirements
        )
        self.assertAlmostEqual(score_custom, score_default)

if __name__ == '__main__':
    unittest.main()
