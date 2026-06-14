import fitz
import json
import os
import pytesseract
from PIL import Image
from collections import defaultdict, Counter
import io
import re

config = '--oem 3 --psm 6 -l eng+chi_sim+jpn+kor+hin+ara'


def is_bold(flags):
    return bool(flags & (1 << 4))


def clean_text(text):
    return re.sub(r'[\u200b\u200c\u200d\u2060]+', '', text).strip()


class PDFOutlineExtractor:
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

    def merge_spans_to_lines(self, spans, y_thresh=5):
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

    def detect_headings(self):
        outline = []
        seen = set()
        threshold = self.body_size * 1.1
        normalized_title = clean_text(self.extract_title()).lower()

        for p_idx, lines in self.page_lines.items():
            ys = [l['y'] for l in lines]
            gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)] if len(ys) > 1 else []
            med_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0

            for i, line in enumerate(lines):
                segments, curr = [], []
                for span in line['spans']:
                    is_hdr = span['size'] >= threshold or is_bold(span['weight'])
                    if not curr or curr[-1]['is_hdr'] == is_hdr:
                        curr.append({'span': span, 'is_hdr': is_hdr})
                    else:
                        segments.append(curr)
                        curr = [{'span': span, 'is_hdr': is_hdr}]
                if curr:
                    segments.append(curr)

                hdr_chunks, hdr_sizes, hdr_weights = [], [], []
                for seg in segments:
                    if seg[0]['is_hdr']:
                        hdr_chunks.append(' '.join(s['span']['text'] for s in seg))
                        hdr_sizes += [s['span']['size'] for s in seg]
                        hdr_weights += [s['span']['weight'] for s in seg]

                if not hdr_chunks:
                    continue

                text = clean_text(' '.join(hdr_chunks))
                if len(text) > 100 or not any(c.isalnum() for c in text):
                    continue
                if text.lower() == normalized_title:
                    continue

                # Date filtering
                if re.match(r'(?:\d{1,2}[-/])?\d{1,2}[-/]\d{2,4}', text) or \
                   re.match(r'(January|February|March|...)\s+\d{1,2},?\s+\d{4}', text, re.IGNORECASE):
                    continue

                size_val, wt_val = max(hdr_sizes), max(hdr_weights)
                level = None
                for idx, sz in enumerate(self.size_rank):
                    if abs(size_val - sz) < 0.1 and (idx >= 2 or is_bold(wt_val)):
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

            # Recovery for headings like "Summary", "Background" etc.
            if p_idx > 0 and lines:
                first_line = lines[0]
                txt = first_line['text']
                if 3 <= len(txt) <= 50 and (txt.istitle() or txt.isupper()):
                    if any(txt.lower() == o['text'].lower() for o in outline):
                        continue
                    next_gap = (lines[1]['y'] - first_line['y']) if len(lines) > 1 else 0
                    if next_gap > 1.2 * med_gap:
                        key = ('H2', txt.lower())
                        if key not in seen:
                            seen.add(key)
                            outline.append({'level': 'H2', 'text': txt, 'page': p_idx + 1})

        return outline

    def analyze_pages(self):
        for p_idx, page in enumerate(self.doc):
            raw_spans = []
            if self.is_text_pdf(page):
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
            else:
                raw_spans = self.ocr_page(page)

            lines = self.merge_spans_to_lines(raw_spans)
            self.page_lines[p_idx] = [{**line, 'page': p_idx + 1} for line in lines]

    def calibrate_font_levels(self):
        if not self.font_stats:
            self.body_size = 12.0
        else:
            self.body_size = self.font_stats.most_common(1)[0][0]
            unique_sizes = sorted(self.font_stats.keys(), reverse=True)
            self.size_rank = unique_sizes[:4]

    def extract_title(self):
        first_lines = self.page_lines.get(0, [])
        if not first_lines:
            return 'Untitled'

        def is_date_like(text):
            return bool(re.search(r'\b(?:\d{1,2}[/-])?\d{1,2}[/-]\d{2,4}\b|(?:January|February)...', text, re.IGNORECASE))

        def is_gibberish(text):
            return len(set(text)) < len(text) * 0.3

        candidates = [
            l for l in first_lines
            if len(l['text']) > 5 and not is_date_like(l['text']) and not is_gibberish(l['text'])
        ]

        candidates.sort(key=lambda x: (-x['size'], x['y']))
        block = []
        if not candidates:
            return 'Untitled'

        base = candidates[0]
        block.append(base)
        base_y, base_size = base['y'], base['size']

        for l in candidates[1:]:
            if abs(l['size'] - base_size) < 0.6 and abs(l['y'] - base_y) < 60:
                block.append(l)

        block.sort(key=lambda x: x['y'])
        return clean_text(' '.join(l['text'] for l in block))

    def extract(self):
        self.analyze_pages()
        self.calibrate_font_levels()
        title = self.extract_title()
        outline = self.detect_headings()
        return {'title': title, 'outline': outline}


# ---------- Execution Driver ----------
def process_pdf(in_path, out_path):
    doc = fitz.open(in_path)
    extractor = PDFOutlineExtractor(doc)
    result = extractor.extract()
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    inp = r"Heading Extractor\inputs"
    outp = r"Heading Extractor\outputs"
    os.makedirs(outp, exist_ok=True)
    for f in os.listdir(inp):
        if f.lower().endswith('.pdf'):
            process_pdf(os.path.join(inp, f), os.path.join(outp, f.replace('.pdf', '.json')))
