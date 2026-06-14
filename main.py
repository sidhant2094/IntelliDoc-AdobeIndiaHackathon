#!/usr/bin/env python3
"""
Adobe India Hackathon - Round 1B: Persona-Driven Document Intelligence
Author: Elite Implementation Team
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Any

# Import our custom modules
from document_processor import DocumentProcessor
from personna_analyzer import PersonaAnalyzer
from relevance_engine import RelevanceEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    """Main orchestrator for persona-driven document intelligence"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.persona_analyzer = PersonaAnalyzer()
        self.relevance_engine = RelevanceEngine()
        
    def load_input_config(self, input_dir: Path) -> Dict[str, Any]:
        """Load persona and job configuration from various possible sources"""
        
        # Try different config file names
        config_files = ['config.json', 'persona.json', 'input.json']
        
        for config_file in config_files:
            config_path = input_dir / config_file
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {config_file}")
                    return config
        
        # Try reading from text files
        txt_files = list(input_dir.glob("*.txt"))
        if txt_files:
            with open(txt_files[0], 'r', encoding='utf-8') as f:
                content = f.read().strip()
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Parse content - look for patterns
                persona = "Research Analyst"
                job = "Extract key insights from documents"
                
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['persona:', 'role:', 'user:']):
                        persona = line.split(':', 1)[-1].strip()
                    elif any(keyword in line.lower() for keyword in ['job:', 'task:', 'goal:']):
                        job = line.split(':', 1)[-1].strip()
                    elif i == 0 and len(line) < 100:  # First short line likely persona
                        persona = line
                    elif i == 1 or (i == 0 and len(line) > 100):  # Job description
                        job = line
                
                return {'persona': persona, 'job_to_be_done': job}
        
        # Fallback defaults
        logger.warning("No configuration found, using intelligent defaults")
        return {
            'persona': "Research Analyst with expertise in document analysis",
            'job_to_be_done': "Extract the most relevant sections and insights from the provided documents for comprehensive analysis"
        }
    
    def process_documents(self, pdf_paths: List[Path], persona: str, job: str, scoring_weights: Dict = None) -> Dict[str, Any]:
        """Main processing pipeline"""
        logger.info(f"Processing {len(pdf_paths)} documents for persona: {persona[:50]}...")
        
        # Step 1: Extract all sections from all documents
        all_sections = []
        doc_metadata = {}
        
        for pdf_path in pdf_paths:
            try:
                logger.info(f"Processing document: {pdf_path.name}")
                sections, metadata = self.doc_processor.extract_document_sections(pdf_path)
                all_sections.extend(sections)
                doc_metadata[pdf_path.name] = metadata
                logger.info(f"Extracted {len(sections)} sections from {pdf_path.name}")
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {e}")
                continue
        
        if not all_sections:
            logger.error("No sections extracted from any document!")
            return self._create_empty_output(pdf_paths, persona, job)
        
        logger.info(f"Total sections extracted: {len(all_sections)}")
        
        # Step 2: Analyze persona and job requirements
        persona_profile = self.persona_analyzer.analyze_persona(persona)
        job_requirements = self.persona_analyzer.analyze_job(job)
        
        logger.info(f"Persona analysis: {persona_profile['expertise_areas'][:3]}")
        logger.info(f"Job keywords: {job_requirements['keywords'][:5]}")
        
        # Step 3: Score and rank all sections
        logger.info("Computing relevance scores...")
        scored_sections = self.relevance_engine.score_sections(
            all_sections, persona_profile, job_requirements, scoring_weights
        )
        
        # Step 4: Select top sections (max 20)
        top_sections = scored_sections[:20]
        logger.info(f"Selected top {len(top_sections)} sections")
        
        # Step 5: Extract relevant subsections
        logger.info("Extracting relevant subsections...")
        subsections = self.relevance_engine.extract_subsections(
            top_sections, persona_profile, job_requirements
        )
        
        logger.info(f"Extracted {len(subsections)} subsections")
        
        # Step 6: Format output
        return self._format_output(
            pdf_paths, persona, job, top_sections, subsections, doc_metadata
        )
    
    def _create_empty_output(self, pdf_paths: List[Path], persona: str, job: str) -> Dict[str, Any]:
        """Create empty output structure when no sections are found"""
        return {
            "metadata": {
                "input_documents": [p.name for p in pdf_paths],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }
    
    def _format_output(self, pdf_paths: List[Path], persona: str, job: str, 
                      sections: List[Dict], subsections: List[Dict], 
                      doc_metadata: Dict) -> Dict[str, Any]:
        """Format final output according to specification"""
        
        # Format sections
        formatted_sections = []
        for i, section in enumerate(sections):
            formatted_sections.append({
                "document": section['document'],
                "page_number": section['page'],
                "section_title": section['title'],
                "importance_rank": i + 1
            })
        
        # Format subsections
        formatted_subsections = []
        for subsection in subsections:
            formatted_subsections.append({
                "document": subsection['document'], 
                "page_number": subsection['page'],
                "refined_text": subsection['text']
            })
        
        return {
            "metadata": {
                "input_documents": [p.name for p in pdf_paths],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.now().isoformat(),
                "total_sections_analyzed": sum(len(sections) for sections in doc_metadata.values() if isinstance(sections, list)),
                "documents_processed": len(pdf_paths)
            },
            "extracted_sections": formatted_sections,
            "subsection_analysis": formatted_subsections
        }


def main():
    """Main entry point"""
    try:
        # Setup paths
        input_dir = Path("inputs\Collection 1\PDFs")
        output_dir = Path("outputs\Collection 1")
        
        # Create output directory
        output_dir.mkdir(exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.error("No PDF files found in input directory!")
            sys.exit(1)
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        # Initialize system
        system = DocumentIntelligenceSystem()
        
        # Load configuration
        config = system.load_input_config(input_dir)
        persona = config.get('persona', 'Research Analyst')
        job_to_be_done = config.get('job_to_be_done', 'Extract key insights')
        scoring_weights = config.get('scoring_weights', None)
        
        logger.info(f"Persona: {persona}")
        logger.info(f"Job: {job_to_be_done[:100]}...")
        if scoring_weights:
            logger.info(f"Custom scoring weights: {scoring_weights}")
        
        # Process documents
        result = system.process_documents(pdf_files, persona, job_to_be_done, scoring_weights)
        
        # Save output
        output_file = output_dir / "challenge1b_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing complete! Output saved to {output_file}")
        logger.info(f"Extracted {len(result['extracted_sections'])} sections and {len(result['subsection_analysis'])} subsections")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()