"""
Document Processing Module - Leverages Round 1A outline extraction
"""

import fitz
import json
import os
import pytesseract
from PIL import Image
from collections import defaultdict, Counter
import io
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging
import platform

logger = logging.getLogger(__name__)

# Configure tesseract executable path cross-platform
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
else:
    # Default location inside Debian/Ubuntu-based containers
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def clean_text(text):
    """Clean text from various unicode issues"""
    return re.sub(r'[\u200b\u200c\u200d\u2060]+', '', text).strip()

def is_bold(flags):
    """Check if text span is bold"""
    return bool(flags & (1 << 4))

class PDFOutlineExtractor:
    """Enhanced version of your Round 1A extractor"""
    
    def __init__(self, doc):
        self.doc = doc
        self.page_lines = defaultdict(list)
        self.font_stats = Counter()
        self.size_rank = []
        self.body_size = None
        self.level_map = {}

    def is_text_pdf(self, page):
        return bool(page.get_text("text").strip())

    def ocr_page(self, page):
        """OCR fallback for image-based PDFs"""
        try:
            pix = page.get_pixmap(dpi=200, alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            data = pytesseract.image_to_data(
                img,
                lang='eng+jpn+chi_sim+ara+hin+kor',
                output_type=pytesseract.Output.DICT
            )

            spans = []
            for i, txt in enumerate(data['text']):
                text = clean_text(txt)
                if len(text.strip()) < 2:
                    continue
                if not any(c.isalpha() for c in text):
                    continue
                spans.append({
                    'text': text,
                    'size': self.body_size or 12.0,
                    'weight': 0,
                    'y': data['top'][i],
                    'x': data['left'][i]
                })
            return spans
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return []

    def merge_spans_to_lines(self, spans, y_thresh=5):
        """Merge text spans into logical lines"""
        if not spans:
            return []
            
        lines = []
        spans_sorted = sorted(spans, key=lambda s: (round(s['y'] / y_thresh), s['x']))
        curr_key, curr_line = None, []

        for s in spans_sorted:
            key = round(s['y'] / y_thresh)
            if curr_key is None or key == curr_key:
                curr_line.append(s)
                curr_key = key
            else:
                lines.append(curr_line)
                curr_line = [s]
                curr_key = key

        if curr_line:
            lines.append(curr_line)

        result = []
        for line_spans in lines:
            text = ' '.join(s['text'] for s in line_spans)
            avg_size = sum(s['size'] for s in line_spans) / len(line_spans)
            max_weight = max(s.get('weight', 0) for s in line_spans)
            y = sum(s['y'] for s in line_spans) / len(line_spans)

            result.append({
                'text': clean_text(text),
                'size': avg_size,
                'weight': max_weight,
                'y': y,
                'spans': line_spans
            })
        return result

    def analyze_pages(self):
        """Extract text structure from all pages"""
        for p_idx, page in enumerate(self.doc):
            raw_spans = []
            if self.is_text_pdf(page):
                try:
                    for block in page.get_text('dict')['blocks']:
                        for line in block.get('lines', []):
                            for span in line.get('spans', []):
                                txt = clean_text(span['text'])
                                if len(txt.strip()) < 2 or not any(c.isalpha() for c in txt):
                                    continue
                                raw_spans.append({
                                    'text': txt,
                                    'size': round(span['size'], 2),
                                    'weight': span['flags'],
                                    'y': span['origin'][1],
                                    'x': span['origin'][0]
                                })
                                self.font_stats[round(span['size'], 2)] += 1
                except Exception as e:
                    logger.warning(f"Error processing page {p_idx}: {e}")
                    raw_spans = self.ocr_page(page)
            else:
                raw_spans = self.ocr_page(page)

            lines = self.merge_spans_to_lines(raw_spans)
            self.page_lines[p_idx] = [{**line, 'page': p_idx + 1} for line in lines]

    def calibrate_font_levels(self):
        """Determine font size hierarchy"""
        if not self.font_stats:
            self.body_size = 12.0
        else:
            self.body_size = self.font_stats.most_common(1)[0][0]
            unique_sizes = sorted(self.font_stats.keys(), reverse=True)
            self.size_rank = unique_sizes[:4]

    def extract_title(self):
        """Extract document title"""
        first_lines = self.page_lines.get(0, [])
        if not first_lines:
            return 'Untitled'

        def is_date_like(text):
            return bool(re.search(r'\b(?:\d{1,2}[/-])?\d{1,2}[/-]\d{2,4}\b', text, re.IGNORECASE))

        candidates = [
            l for l in first_lines
            if len(l['text']) > 5 and not is_date_like(l['text'])
        ]

        if not candidates:
            return 'Untitled'

        candidates.sort(key=lambda x: (-x['size'], x['y']))
        return clean_text(candidates[0]['text'])

    def detect_headings(self):
        """Detect document headings with enhanced logic"""
        outline = []
        seen = set()
        threshold = self.body_size * 1.1 if self.body_size else 12.0
        normalized_title = clean_text(self.extract_title()).lower()

        for p_idx, lines in self.page_lines.items():
            if not lines:
                continue
                
            ys = [l['y'] for l in lines]
            gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)] if len(ys) > 1 else []
            med_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0

            for i, line in enumerate(lines):
                if not line.get('spans'):
                    continue
                    
                # Analyze spans for heading characteristics
                hdr_chunks, hdr_sizes, hdr_weights = [], [], []
                for span in line['spans']:
                    is_hdr = span['size'] >= threshold or is_bold(span.get('weight', 0))
                    if is_hdr:
                        hdr_chunks.append(span['text'])
                        hdr_sizes.append(span['size'])
                        hdr_weights.append(span.get('weight', 0))

                if not hdr_chunks:
                    continue

                text = clean_text(' '.join(hdr_chunks))
                if len(text) > 100 or not any(c.isalnum() for c in text):
                    continue
                if text.lower() == normalized_title:
                    continue

                # Skip dates
                if re.match(r'(?:\d{1,2}[-/])?\d{1,2}[-/]\d{2,4}', text):
                    continue

                size_val = max(hdr_sizes) if hdr_sizes else threshold
                wt_val = max(hdr_weights) if hdr_weights else 0
                
                # Determine heading level
                level = None
                for idx, sz in enumerate(self.size_rank[:3]):
                    if abs(size_val - sz) < 0.1:
                        level = f'H{idx + 1}'
                        break

                prev_gap = line['y'] - (ys[i - 1] if i > 0 else 0)
                
                if not level and size_val >= threshold and is_bold(wt_val):
                    level = 'H3'
                elif not level and med_gap and prev_gap > 1.8 * med_gap:
                    level = 'H3'

                key = (level, text.lower())
                if level and key not in seen:
                    seen.add(key)
                    outline.append({'level': level, 'text': text, 'page': p_idx + 1})

        return outline

    def extract(self):
        """Main extraction method"""
        self.analyze_pages()
        self.calibrate_font_levels()
        title = self.extract_title()
        outline = self.detect_headings()
        return {'title': title, 'outline': outline}


class DocumentProcessor:
    """Main document processor that builds on Round 1A"""
    
    def __init__(self):
        self.min_section_length = 50
        
    def extract_document_sections(self, pdf_path: Path) -> Tuple[List[Dict], Dict]:
        """Extract structured sections from a PDF document"""
        try:
            doc = fitz.open(pdf_path)
            extractor = PDFOutlineExtractor(doc)
            
            # Get outline structure
            outline_data = extractor.extract()
            title = outline_data['title']
            outline = outline_data['outline']
            
            # Extract full text content with page mapping
            full_text_pages = {}
            for page_num in range(len(doc)):
                page = doc[page_num]
                full_text_pages[page_num + 1] = page.get_text()
            
            doc.close()
            
            # Create sections based on outline structure
            sections = self._create_sections_from_outline(
                outline, full_text_pages, pdf_path.name, title
            )
            
            metadata = {
                'title': title,
                'total_pages': len(full_text_pages),
                'outline_items': len(outline),
                'sections_created': len(sections)
            }
            
            logger.info(f"Extracted {len(sections)} sections from {pdf_path.name}")
            return sections, metadata
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return [], {'error': str(e)}
    
    def _create_sections_from_outline(self, outline: List[Dict], full_text_pages: Dict, 
                                    doc_name: str, title: str) -> List[Dict]:
        """Create structured sections from outline and full text"""
        sections = []
        
        # Add title as first section if substantial
        if title and title != 'Untitled' and len(title) > 10:
            sections.append({
                'document': doc_name,
                'title': title,
                'content': title,
                'page': 1,
                'level': 'title',
                'type': 'title'
            })
        
        # Process each outline item
        for i, item in enumerate(outline):
            try:
                # Get section content
                start_page = item['page']
                end_page = outline[i + 1]['page'] if i + 1 < len(outline) else max(full_text_pages.keys())
                
                # Extract text for this section
                section_text = self._extract_section_text(
                    full_text_pages, start_page, end_page, item['text']
                )
                
                if len(section_text) >= self.min_section_length:
                    sections.append({
                        'document': doc_name,
                        'title': item['text'],
                        'content': section_text,
                        'page': start_page,
                        'level': item['level'],
                        'type': 'section'
                    })
                    
            except Exception as e:
                logger.warning(f"Error processing outline item {item}: {e}")
                continue
        
        # If no sections from outline, create page-based sections
        if len(sections) <= 1:  # Only title
            sections.extend(self._create_page_based_sections(full_text_pages, doc_name))
        
        return sections
    
    def _extract_section_text(self, full_text_pages: Dict, start_page: int, 
                            end_page: int, section_title: str) -> str:
        """Extract text content for a specific section"""
        content_parts = []
        
        for page_num in range(start_page, min(end_page + 1, max(full_text_pages.keys()) + 1)):
            if page_num in full_text_pages:
                page_text = full_text_pages[page_num]
                
                # Clean and filter page text
                lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                filtered_lines = []
                
                found_start = False
                for line in lines:
                    # Skip until we find the section start
                    if not found_start and section_title.lower() in line.lower():
                        found_start = True
                        continue
                    
                    if found_start:
                        # Skip headers, footers, page numbers
                        if self._is_content_line(line):
                            filtered_lines.append(line)
                
                if filtered_lines:
                    content_parts.append(' '.join(filtered_lines))
        
        return ' '.join(content_parts)
    
    def _is_content_line(self, line: str) -> bool:
        """Filter out headers, footers, and page numbers"""
        line = line.strip()
        
        # Skip empty or very short lines
        if len(line) < 3:
            return False
        
        # Skip page numbers
        if re.match(r'^\d+$', line):
            return False
        
        # Skip common header/footer patterns
        if re.match(r'^(page \d+|chapter \d+|\d+\s*$)', line.lower()):
            return False
        
        return True
    
    def _create_page_based_sections(self, full_text_pages: Dict, doc_name: str) -> List[Dict]:
        """Fallback: create sections based on pages when outline is insufficient"""
        sections = []
        
        for page_num, page_text in full_text_pages.items():
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            content_lines = [line for line in lines if self._is_content_line(line)]
            
            if content_lines and len(' '.join(content_lines)) >= self.min_section_length:
                # Try to find a good title from the first few lines
                title = self._extract_page_title(content_lines) or f"Page {page_num} Content"
                
                sections.append({
                    'document': doc_name,
                    'title': title,
                    'content': ' '.join(content_lines),
                    'page': page_num,
                    'level': 'H2',
                    'type': 'page_section'
                })
        
        return sections
    
    def _extract_page_title(self, content_lines: List[str]) -> str:
        """Extract a meaningful title from page content"""
        for line in content_lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Look for title-like characteristics
            if 10 <= len(line) <= 80 and not line.endswith('.'):
                # Check if it looks like a title (proper case, no lowercase articles at start)
                words = line.split()
                if len(words) >= 2 and any(word[0].isupper() for word in words[:3]):
                    return line
        
        # Fallback to first substantial line
        return content_lines[0] if content_lines else "Content"