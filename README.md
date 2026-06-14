# IntelliDoc

## Overview

IntelliDoc is an advanced persona-driven document intelligence system that extracts and ranks the most relevant sections from PDF documents based on a specific persona and their job-to-be-done. It's designed to help users quickly find the most pertinent information in documents based on their specific needs and expertise level.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Docker Support](#docker-support)
- [Development](#development)
- [License](#license)

## Features

### Heading Extractor
- **Multi-format Support**: Extracts headings from both text-based and image-based PDFs
- **Multilingual OCR**: Supports multiple languages including English, Japanese, Chinese, Arabic, Hindi, and Korean
- **Smart Heading Detection**:
  - Identifies headings based on font size, weight, and style
  - Handles nested heading hierarchies
  - Distinguishes between main headings and subheadings
- **Document Structure Analysis**:
  - Automatically detects document structure
  - Identifies body text vs. headings
  - Handles complex layouts and columns
- **Output Formats**:
  - JSON output with hierarchical heading structure
  - Preserves page numbers and positions
  - Extracts text content under each heading

### Advanced PDF Processing
- Enhanced PDF text extraction with outline parsing
- OCR fallback for image-based PDFs
- Multilingual support (English, Japanese, Chinese, Arabic, Hindi, Korean)
- Intelligent section boundary detection
- Content type classification
- Table and figure extraction

### Persona Analysis
- Automatic persona type identification (researcher, analyst, student, etc.)
- Domain focus detection (academic, business, technical, etc.)
- Experience level assessment
- Expertise area extraction
- Job requirement parsing

### Relevance Scoring
- Multi-dimensional scoring system:
  - Semantic Similarity (35%)
  - Keyword Overlap (25%)
  - Content Type Match (20%)
  - Expertise Alignment (15%)
  - Structural Importance (5%)

### Subsection Intelligence
- Granular content extraction from top sections
- Paragraph-level relevance scoring
- Intelligent text chunking for optimal readability
- Context-aware text refinement

## Installation

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for image-based PDFs)
- Poppler (for PDF processing)
- Git (for cloning the repository)

### Setup Instructions

#### 1. Clone the Repository
```bash
git clone https://github.com/Codealpha07/IntelliDoc.git
cd IntelliDoc
```

#### 2. Set Up Python Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

**macOS (using Homebrew):**
```bash
brew install tesseract poppler
```

**Windows:**
1. Download and install Tesseract OCR from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. During installation, check "Add Tesseract to your system PATH"
3. Download and install Poppler from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/)
4. Add Poppler to your system PATH

#### 5. Verify Installation
```bash
python -c "import fitz; print('PyMuPDF version:', fitz.__version__)"
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
```

## Usage

### Basic Usage

1. **Prepare Input Files**
   - Place 3-10 PDF files in the `inputs/` directory
   - Create a configuration file (see [Input Format](#input-format))
   - Example directory structure:
     ```
     IntelliDoc/
     ├── inputs/
     │   ├── document1.pdf
     │   ├── document2.pdf
     │   └── config.json
     └── ...
     ```

2. **Run the Application**
   ```bash
   # Basic usage with default settings
   python main.py
   
   # With custom input/output directories
   python main.py --input-dir ./my_inputs --output-dir ./my_outputs
   
   # With verbose logging
   python main.py --verbose
   ```

3. **View Results**
   - Output will be saved in the `outputs/` directory by default
   - Main output file: `challenge1b_output.json`
   - Logs are available in `app.log` (when verbose mode is enabled)

### Command Line Options

```bash
python main.py [options]

Options:
  --input-dir PATH    Directory containing input PDFs (default: inputs/)
  --output-dir PATH   Directory to save output (default: outputs/)
  --config FILE       Path to configuration file (default: auto-detected)
  --verbose           Enable verbose logging (default: False)
  --debug             Enable debug mode (more detailed logging) (default: False)
  --max-docs N        Maximum number of documents to process (default: 10)
  --no-ocr            Disable OCR processing (faster but may miss text in images)
  --language LANG     Set OCR language (default: eng)
```

### Configuration File Format

Create a `config.json` file in your input directory with the following format:

```json
{
  "persona": "[Persona description]",
  "job_to_be_done": "[Detailed description of the task]",
  "scoring_weights": {
    "semantic_similarity": 0.35,
    "keyword_overlap": 0.25,
    "content_type_match": 0.20,
    "expertise_alignment": 0.15,
    "structural_importance": 0.05
  }
}
```

*Note: The `scoring_weights` block is optional. If provided but the weights do not sum to 1.0, they will be normalized proportionally. If omitted or if the sum is 0, defaults will be used.*

Example:
```json
{
  "persona": "Senior Machine Learning Engineer with 5 years of experience in NLP",
  "job_to_be_done": "Research state-of-the-art transformer architectures for document understanding",
  "scoring_weights": {
    "semantic_similarity": 0.50,
    "keyword_overlap": 0.30,
    "content_type_match": 0.10,
    "expertise_alignment": 0.05,
    "structural_importance": 0.05
  }
}
```

### Environment Variables

You can also configure the application using environment variables:

```bash
# Set input/output directories
export INTELLIDOC_INPUT_DIR=./my_inputs
export INTELLIDOC_OUTPUT_DIR=./my_outputs

# Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export INTELLIDOC_LOG_LEVEL=INFO

# Enable/disable features
export INTELLIDOC_ENABLE_OCR=true
export INTELLIDOC_MAX_DOCS=5
```

## Input Format

The system expects:
- 3-10 PDF files in `/app/input/` directory
- Configuration file (one of):
  - `config.json`: JSON format with `persona` and `job_to_be_done` fields
  - `persona.json`: Alternative JSON configuration
  - `input.json`: Another alternative format
  - `*.txt`: Plain text with persona on first line, job description following

### Example Configuration (`config.json`):
```json
{
  "persona": "PhD Researcher in Computational Biology with expertise in machine learning applications",
  "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for graph neural networks in drug discovery"
}
```

## Output Format

The system generates `challenge1b_output.json` with:

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processing_timestamp": "2025-01-XX...",
    "total_sections_analyzed": 45,
    "documents_processed": 3
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "section_title": "Graph Neural Network Architectures",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "refined_text": "Graph neural networks have emerged as..."
    }
  ]
}
```

## Technical Implementation

### Persona Classification
The system recognizes 8 persona types:
- **Researcher**: Focus on methodology, literature, benchmarks
- **Student**: Emphasis on concepts, examples, fundamentals  
- **Analyst**: Business metrics, trends, performance analysis
- **Engineer**: Technical implementation, architecture, systems
- **Manager**: Strategy, planning, execution, processes
- **Consultant**: Recommendations, best practices, optimization
- **Journalist**: Facts, events, context, impact analysis
- **Entrepreneur**: Market opportunities, innovation, scaling

### Content Type Detection
Automatically identifies 6 content types:
- **Methodology**: Approaches, techniques, frameworks
- **Results**: Findings, data, measurements, outcomes
- **Background**: Context, literature, historical information
- **Analysis**: Evaluation, interpretation, discussion
- **Examples**: Cases, illustrations, applications
- **Summary**: Conclusions, abstracts, key points

### Advanced Scoring Algorithm

```python
def calculate_score(section, persona, job):
    score = (
        0.35 * semantic_similarity(section, persona, job) +
        0.25 * keyword_overlap(section, persona, job) +
        0.20 * content_type_match(section, job) +
        0.15 * expertise_alignment(section, persona) +
        0.05 * structural_importance(section)
    )
    return min(score, 1.0)
```

## Performance Optimizations

- **Efficient Text Processing**: Optimized regular expressions and string operations
- **Smart Caching**: Avoid redundant computations
- **Memory Management**: Process documents sequentially to minimize RAM usage
- **Early Filtering**: Skip irrelevant content early in the pipeline

## Docker Support

### Building the Docker Image

1. Build the Docker image:
   ```bash
   docker build --platform linux/amd64 -t intellidoc:latest .
   ```

2. Verify the image was built successfully:
   ```bash
   docker images | grep intellidoc
   ```

### Running the Container

1. Create input and output directories:
   ```bash
   mkdir -p ./input ./output
   ```

2. Place your PDF files and config in the input directory:
   ```bash
   cp your-document.pdf ./input/
   cp config.json ./input/
   ```

3. Run the container:
   ```bash
   docker run --rm \
     -v $(pwd)/input:/app/input \
     -v $(pwd)/output:/app/output \
     --network none \
     intellidoc:latest
   ```

### Docker Compose

For easier management, you can use Docker Compose:

1. Create a `docker-compose.yml` file:
   ```yaml
   version: '3.8'
   services:
     intellidoc:
       build: .
       volumes:
         - ./input:/app/input
         - ./output:/app/output
       environment:
         - INTELLIDOC_LOG_LEVEL=INFO
         - INTELLIDOC_MAX_DOCS=5
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

2. Start the service:
   ```bash
   docker-compose up --build
   ```

### Docker Best Practices

- **Resource Limits**: The example above sets reasonable CPU and memory limits
- **Volume Mounting**: Use named volumes for production deployments
- **Security**: Runs with non-root user inside container
- **Caching**: Leverages Docker layer caching for faster builds

## Dependencies

### Core Dependencies
- **Python 3.8+**: Core programming language
- **PyMuPDF (fitz)**: Advanced PDF processing and text extraction
- **pytesseract**: OCR capabilities for image-based PDFs
- **Pillow**: Image processing for OCR preprocessing
- **numpy**: Numerical computations and array operations
- **pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning utilities for text processing
- **nltk**: Natural language processing toolkit
- **tqdm**: Progress bars for long-running operations

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Static type checking
- **pylint**: Code quality checking

### System Dependencies
- **Tesseract OCR**: For optical character recognition
- **Poppler**: For PDF rendering and processing
- **Git**: For version control

## Error Handling and Logging

### Error Handling Strategies
- **Graceful Fallbacks**: Automatically falls back to OCR for image-based PDFs
- **Robust Parsing**: Handles malformed PDF structures and recovers gracefully
- **Input Validation**: Validates all inputs before processing
- **Configuration Defaults**: Provides sensible defaults for missing configuration
- **Resource Management**: Properly manages file handles and system resources

### Logging System

Logs are written to `app.log` and can be configured via environment variables:

```python
import logging

# Basic configuration
logging.basicConfig(
    level=os.getenv('INTELLIDOC_LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Get logger for a module
logger = logging.getLogger(__name__)
```

### Common Issues and Solutions

1. **OCR Failures**:
   - Ensure Tesseract is installed and in PATH
   - Check that the language packs are installed
   - Verify image quality if using scanned documents

2. **PDF Processing Errors**:
   - Corrupt PDFs may cause issues
   - Try opening the PDF in a viewer to verify integrity
   - Consider converting to a different format if problems persist

3. **Performance Issues**:
   - Large PDFs may require more memory
   - Consider splitting large documents
   - Enable logging to identify bottlenecks

## Performance and Scaling

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Processing Time | ~30-45s | For 5 average-sized PDFs |
| Memory Usage | 400-600MB | Peak usage during processing |
| CPU Usage | 2 cores | Can be scaled based on workload |
| Model Size | <100MB | No large external models |
| Document Size | Up to 50MB | Per document |
| Batch Size | Up to 10 | Documents per run |

### Scaling Considerations

1. **Vertical Scaling**:
   - Increase CPU cores for faster processing
   - Add more RAM for larger documents or batches

2. **Horizontal Scaling**:
   - Process documents in parallel across multiple instances
   - Use a message queue for job distribution

3. **Optimization Tips**:
   - Enable caching for repeated documents
   - Disable OCR if not needed with `--no-ocr`
   - Process documents in smaller batches

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU Cores | 1 | 2+ |
| RAM | 1GB | 2GB |
| Disk Space | 100MB | 1GB |
| OS | Linux/Windows/macOS | Linux |

## Testing and Quality Assurance

### Test Coverage

The codebase includes comprehensive test coverage for:
- Document processing and text extraction
- Persona analysis and classification
- Relevance scoring algorithms
- Input/output handling
- Error conditions and edge cases

### Test Execution

Run the full test suite:
```bash
pytest tests/ -v --cov=.
```

### Test Scenarios

1. **Unit Tests**:
   - Individual component testing
   - Mocked dependencies
   - Edge case validation

2. **Integration Tests**:
   - End-to-end document processing
   - Configuration handling
   - File system operations

3. **Performance Tests**:
   - Processing time benchmarks
   - Memory usage profiling
   - Scaling characteristics

### Test Data

Test data is stored in `tests/test_data/` and includes:
- Sample PDF documents
- Configuration files
- Expected output files

### Continuous Integration

The project includes a `.github/workflows/ci.yml` file that runs:
- Unit tests
- Type checking
- Linting
- Code coverage

## Advanced Features

### Multi-dimensional Analysis

1. **Semantic Understanding**:
   - Context-aware text analysis
   - Topic modeling
   - Entity recognition

2. **Persona Adaptation**:
   - Dynamic adjustment based on expertise level
   - Domain-specific processing
   - Customizable scoring weights

3. **Content Intelligence**:
   - Automatic section detection
   - Table and figure extraction
   - Citation analysis

### Customization Options

1. **Scoring Weights**:
   You can customize the relevance engine scoring weights dynamically by adding a `scoring_weights` block to your `config.json` file. If omitted, the default weights are:
   ```json
   {
       "semantic_similarity": 0.35,
       "keyword_overlap": 0.25,
       "content_type_match": 0.20,
       "expertise_alignment": 0.15,
       "structural_importance": 0.05
   }
   ```

2. **Plugins and Extensions**:
   - Custom document processors
   - Specialized analyzers
   - Output formatters

3. **API Access**:
   - RESTful interface
   - Python package
   - Command-line interface

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository.

## Acknowledgments

- Adobe for the original challenge
- Open source contributors
- The Python community

---

This implementation combines the robust PDF extraction capabilities from Round 1A with sophisticated intelligence layers to deliver highly relevant, persona-specific document insights.