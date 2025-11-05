#!/bin/bash

###############################################################################
#                                                                             #
#     CFA-I Repository Integration Script                                    #
#                                                                             #
#     Downloads Jupyter notebooks from EvelynLinn/CFA-I repository          #
#     and prepares them for use with the CFA Prep Tool                      #
#                                                                             #
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          CFA-I Repository Integration                          ║
║     Downloading CFA Level I Study Materials                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Create directory for CFA content
CFA_CONTENT_DIR="cfa-prep-tool/cfa-content"
mkdir -p "$CFA_CONTENT_DIR"

echo -e "${GREEN}[1/4] Downloading CFA-I repository...${NC}"

# Check if git is available
if command -v git &> /dev/null; then
    # Clone the repository
    if [ -d "$CFA_CONTENT_DIR/CFA-I" ]; then
        echo -e "${YELLOW}Repository already exists. Pulling latest changes...${NC}"
        cd "$CFA_CONTENT_DIR/CFA-I"
        git pull
        cd ../../..
    else
        git clone https://github.com/EvelynLinn/CFA-I.git "$CFA_CONTENT_DIR/CFA-I"
    fi
    echo -e "${GREEN}✓ Repository downloaded${NC}"
else
    echo -e "${YELLOW}Git not found. Downloading as ZIP...${NC}"
    curl -L https://github.com/EvelynLinn/CFA-I/archive/refs/heads/master.zip -o "$CFA_CONTENT_DIR/CFA-I.zip"
    cd "$CFA_CONTENT_DIR"
    unzip -q CFA-I.zip
    mv CFA-I-master CFA-I
    rm CFA-I.zip
    cd ../..
    echo -e "${GREEN}✓ Repository downloaded and extracted${NC}"
fi

echo ""
echo -e "${GREEN}[2/4] Analyzing content...${NC}"

# Count notebooks
NOTEBOOK_COUNT=$(find "$CFA_CONTENT_DIR/CFA-I" -name "*.ipynb" | wc -l | tr -d ' ')
echo "  Found $NOTEBOOK_COUNT Jupyter notebooks"

# List topics
echo ""
echo "Topics covered:"
find "$CFA_CONTENT_DIR/CFA-I" -name "*.ipynb" -exec basename {} \; | sort | head -10

echo ""
echo -e "${GREEN}[3/4] Installing required Python packages...${NC}"

# Activate virtual environment if it exists
if [ -d "cfa-venv" ]; then
    source cfa-venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
fi

# Install Jupyter and nbconvert for processing notebooks
pip install jupyter nbconvert nbformat -q
echo -e "${GREEN}✓ Jupyter packages installed${NC}"

echo ""
echo -e "${GREEN}[4/4] Creating integration script...${NC}"

# Create Python script for processing notebooks
cat > cfa-prep-tool/backend/process_cfa_notebooks.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Process CFA-I Jupyter notebooks to extract content for flashcard/quiz generation.
"""
import json
import os
import sys
from pathlib import Path
import nbformat
from typing import List, Dict

class NotebookProcessor:
    """Process Jupyter notebooks to extract CFA content."""

    def __init__(self, notebooks_dir: str):
        self.notebooks_dir = Path(notebooks_dir)

    def extract_content_from_notebook(self, notebook_path: Path) -> Dict:
        """Extract text and code from a Jupyter notebook."""
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        content = {
            'title': notebook_path.stem,
            'cells': [],
            'full_text': ''
        }

        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                content['cells'].append({
                    'type': 'markdown',
                    'content': cell.source
                })
                content['full_text'] += cell.source + '\n\n'
            elif cell.cell_type == 'code':
                content['cells'].append({
                    'type': 'code',
                    'content': cell.source
                })

        return content

    def process_all_notebooks(self) -> List[Dict]:
        """Process all notebooks in the directory."""
        notebooks = list(self.notebooks_dir.glob('**/*.ipynb'))
        results = []

        print(f"Found {len(notebooks)} notebooks to process\n")

        for nb_path in notebooks:
            # Skip checkpoint files
            if '.ipynb_checkpoints' in str(nb_path):
                continue

            print(f"Processing: {nb_path.name}")
            try:
                content = self.extract_content_from_notebook(nb_path)
                results.append(content)
                print(f"  ✓ Extracted {len(content['cells'])} cells")
            except Exception as e:
                print(f"  ✗ Error: {e}")

        return results

    def save_extracted_content(self, output_file: str):
        """Process notebooks and save extracted content to JSON."""
        results = self.process_all_notebooks()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved extracted content to: {output_file}")
        print(f"  Total notebooks processed: {len(results)}")

        # Calculate total content size
        total_text = sum(len(r['full_text']) for r in results)
        print(f"  Total content size: {total_text:,} characters")

def main():
    """Main function."""
    # Default paths
    notebooks_dir = '../cfa-content/CFA-I'
    output_file = '../cfa-content/extracted_content.json'

    if not os.path.exists(notebooks_dir):
        print(f"Error: Notebooks directory not found: {notebooks_dir}")
        print("Please run download_cfa_content.sh first")
        sys.exit(1)

    processor = NotebookProcessor(notebooks_dir)
    processor.save_extracted_content(output_file)

    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print("1. Review extracted content in: extracted_content.json")
    print("2. Use the content with your CFA Prep Tool:")
    print("   - Generate flashcards from notebook sections")
    print("   - Create quizzes from code examples")
    print("   - Extract key concepts and formulas")
    print("\n✓ Integration complete!")

if __name__ == '__main__':
    main()
PYTHON_SCRIPT

chmod +x cfa-prep-tool/backend/process_cfa_notebooks.py
echo -e "${GREEN}✓ Created notebook processing script${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}Integration Complete!${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "CFA-I repository downloaded to: $CFA_CONTENT_DIR/CFA-I"
echo "Contains: $NOTEBOOK_COUNT Jupyter notebooks"
echo ""
echo "Next steps:"
echo ""
echo "1. Extract content from notebooks:"
echo "   cd cfa-prep-tool/backend"
echo "   python process_cfa_notebooks.py"
echo ""
echo "2. This will create: cfa-content/extracted_content.json"
echo ""
echo "3. Use the extracted content to generate study materials:"
echo "   - Upload JSON content to your CFA Prep Tool"
echo "   - Generate flashcards from each topic"
echo "   - Create quizzes from notebook examples"
echo ""
echo "═══════════════════════════════════════════════════════════"
