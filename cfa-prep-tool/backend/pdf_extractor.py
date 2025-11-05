"""PDF extraction service for CFA materials."""
import os
import json
import re
from typing import Dict, List, Tuple
import fitz  # PyMuPDF

class CFAPDFExtractor:
    """Extract content from CFA PDF files."""

    def __init__(self, pdf_dir: str, output_dir: str):
        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF page by page."""
        pages = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    pages.append({
                        "page_number": page_num + 1,
                        "text": text,
                        "char_count": len(text)
                    })
            doc.close()
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
        return pages

    def parse_level_and_volume(self, filename: str) -> Tuple[str, int]:
        """Parse level and volume from filename."""
        # Example: "CFA L1 (V1).pdf" -> ("L1", 1)
        match = re.search(r'CFA L(\d) \(V(\d)\)', filename)
        if match:
            level = f"L{match.group(1)}"
            volume = int(match.group(2))
            return level, volume
        return None, None

    def extract_sections(self, text: str) -> List[Dict]:
        """Extract sections/chapters from text."""
        # This is a simplified version - you may need to adjust based on PDF structure
        sections = []

        # Look for common section headers
        section_patterns = [
            r'READING \d+',
            r'CHAPTER \d+',
            r'LEARNING OUTCOME STATEMENTS',
            r'SUMMARY',
            r'PRACTICE PROBLEMS'
        ]

        current_section = None
        current_text = []

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check if this is a section header
            is_header = any(re.search(pattern, line, re.IGNORECASE) for pattern in section_patterns)

            if is_header:
                # Save previous section
                if current_section and current_text:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_text)
                    })
                # Start new section
                current_section = line
                current_text = []
            elif current_section:
                current_text.append(line)

        # Save last section
        if current_section and current_text:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_text)
            })

        return sections

    def extract_formulas(self, text: str) -> List[str]:
        """Extract mathematical formulas from text."""
        formulas = []

        # Look for common formula patterns
        # This is simplified - may need enhancement
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Look for lines with common math symbols and equals signs
            if '=' in line and any(char in line for char in ['/', '*', '+', '-', '^', '(', ')']):
                # Check if it's likely a formula (not just regular text with =)
                if len(line) < 200 and re.search(r'[A-Z][a-z]?\s*=', line):
                    formulas.append(line)

        return formulas

    def process_pdf(self, pdf_filename: str) -> Dict:
        """Process a single PDF file."""
        pdf_path = os.path.join(self.pdf_dir, pdf_filename)
        level, volume = self.parse_level_and_volume(pdf_filename)

        if not level or not volume:
            print(f"Could not parse level/volume from {pdf_filename}")
            return None

        print(f"Processing {pdf_filename} - {level} Volume {volume}...")

        # Extract pages
        pages = self.extract_text_from_pdf(pdf_path)

        if not pages:
            print(f"No content extracted from {pdf_filename}")
            return None

        # Combine all text
        full_text = '\n\n'.join([p['text'] for p in pages])

        # Extract sections
        sections = self.extract_sections(full_text)

        # Extract formulas
        formulas = self.extract_formulas(full_text)

        # Prepare extracted data
        extracted_data = {
            "filename": pdf_filename,
            "level": level,
            "volume": volume,
            "total_pages": len(pages),
            "total_chars": len(full_text),
            "sections": sections,
            "formulas": formulas,
            "pages": pages[:5]  # Store first 5 pages as sample
        }

        # Save to JSON
        output_filename = f"{level}_V{volume}_extracted.json"
        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)

        print(f"Saved extracted data to {output_filename}")
        return extracted_data

    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDF files in the directory."""
        results = []
        pdf_files = sorted([f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')])

        print(f"Found {len(pdf_files)} PDF files to process\n")

        for pdf_file in pdf_files:
            result = self.process_pdf(pdf_file)
            if result:
                results.append(result)

        print(f"\nProcessed {len(results)} PDFs successfully")
        return results

def main():
    """Main function for testing PDF extraction."""
    pdf_dir = "/home/user/CFA-2024"
    output_dir = "/home/user/CFA-2024/cfa-prep-tool/data/extracted"

    extractor = CFAPDFExtractor(pdf_dir, output_dir)
    results = extractor.process_all_pdfs()

    print("\nExtraction Summary:")
    for result in results:
        print(f"- {result['level']} V{result['volume']}: {result['total_pages']} pages, {len(result['sections'])} sections, {len(result['formulas'])} formulas")

if __name__ == "__main__":
    main()
