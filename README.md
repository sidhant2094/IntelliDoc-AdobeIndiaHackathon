# IntelliDoc

## Persona-Aware Document Intelligence System

IntelliDoc is a persona-driven document intelligence system that automatically reconstructs document structure from PDF files and retrieves the most relevant sections based on a user's role, expertise, and objective.

The system combines PDF layout analysis, OCR-based text extraction, persona profiling, job requirement analysis, content-type classification, and multi-factor relevance scoring to help users efficiently navigate large documents and identify task-specific information.

---

## Problem Statement

Large technical documents, reports, research papers, and manuals often contain hundreds of pages of information. Locating relevant content manually is time-consuming and inefficient.

IntelliDoc addresses this challenge by:

- Extracting document structure from PDFs
- Identifying headings and section hierarchies
- Understanding user personas and objectives
- Ranking sections based on contextual relevance
- Returning focused content aligned with user intent

---

## Key Features

### Document Structure Extraction

- Automatic heading detection
- Hierarchical section reconstruction
- PDF outline generation
- Page-aware section mapping

### OCR-Based Processing

- Support for scanned PDFs
- Multilingual OCR support
- Automatic fallback when text extraction is unavailable

### Persona Intelligence

- Persona classification
- Domain identification
- Experience-level assessment
- Expertise area extraction

### Job Requirement Analysis

- Objective detection
- Keyword extraction
- Content preference modeling
- Priority identification

### Multi-Factor Relevance Ranking

- Semantic similarity scoring
- Keyword overlap analysis
- Content-type matching
- Expertise alignment scoring
- Structural importance weighting

### Intelligent Subsection Extraction

- Paragraph-level segmentation
- Relevance-based filtering
- Context-preserving content retrieval

---

## Core Pipeline

```text
User Persona + Job Objective
            │
            ▼
 Persona Classification
            │
            ▼
 Job Requirement Analysis
            │
            ▼
 PDF Structure Extraction
            │
            ▼
 Section Reconstruction
            │
            ▼
 Content-Type Detection
            │
            ▼
 Multi-Factor Relevance Scoring
            │
            ▼
 Ranked Section Retrieval
            │
            ▼
 Subsection Extraction
```

---

## System Architecture

```text
PDF Documents
      │
      ▼
Text Extraction / OCR
      │
      ▼
Document Processing Engine
      │
      ▼
Heading Detection
      │
      ▼
Section Generation
      │
      ▼
Persona Analyzer
      │
      ▼
Relevance Engine
      │
      ▼
Ranked Document Insights
```

---

## Methodology

The relevance engine evaluates each document section using a weighted scoring framework:

| Component | Weight |
|------------|---------|
| Semantic Similarity | 35% |
| Keyword Overlap | 25% |
| Content-Type Match | 20% |
| Expertise Alignment | 15% |
| Structural Importance | 5% |

The final relevance score determines which sections are surfaced to the user.

---

## Machine Learning & NLP Components

The system incorporates multiple NLP and information retrieval techniques:

- Persona classification using linguistic pattern analysis
- Domain and expertise detection
- Content-type classification
- Keyword extraction
- Jaccard similarity matching
- TF-IDF-inspired relevance scoring
- Multi-factor ranking aggregation
- Structured document hierarchy analysis

---

## Technologies Used

### Core Technologies

- Python
- PyMuPDF
- Tesseract OCR
- Pillow
- NumPy

### Supporting Tools

- Docker
- Git
- GitHub

---

## Dataset

Evaluation was performed on a collection of:

- Research papers
- Technical documentation
- Academic reports
- Business reports
- Long-form PDF documents

The system is designed to operate across multiple document domains without task-specific training.

---

## Project Structure

```text
IntelliDoc/
├── document_processor.py
├── persona_analyzer.py
├── relevance_engine.py
├── main.py
├── inputs/
├── outputs/
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/sidhant2094/IntelliDoc.git

cd IntelliDoc

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### System Dependencies

macOS:

```bash
brew install tesseract poppler
```

---

## Running the Project

```bash
python main.py
```

Place input PDF documents inside the `inputs/` directory.

Generated results will be saved in the `outputs/` directory.

---

## Applications

- Research paper exploration
- Technical document search
- Literature review assistance
- Business report analysis
- Knowledge management systems
- Academic document retrieval

---

## Future Improvements

- Transformer-based retrieval models
- Dense vector search
- Retrieval-Augmented Generation (RAG)
- Interactive web interface
- Multi-document question answering
- Benchmark-based evaluation metrics

---

## Maintainer

**Sidhant Malik**

---

## License

This project is licensed under the MIT License.
