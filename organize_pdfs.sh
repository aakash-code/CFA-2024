#!/bin/bash
# Script to organize root CFA PDFs into an archive folder

echo "======================================================"
echo "CFA PDF Organization Script"
echo "======================================================"
echo ""

# Create archive directory in root
ARCHIVE_DIR="CFA-PDFs-Archive"
mkdir -p "$ARCHIVE_DIR"

echo "📁 Creating organized archive structure..."
mkdir -p "$ARCHIVE_DIR/Level-1"
mkdir -p "$ARCHIVE_DIR/Level-2"
mkdir -p "$ARCHIVE_DIR/Level-3"

echo ""
echo "📦 Moving PDFs from root to archive..."

# Move Level 1 PDFs
for i in 1 2 3 4 5 6; do
    if [ -f "CFA L1 (V$i).pdf" ]; then
        mv "CFA L1 (V$i).pdf" "$ARCHIVE_DIR/Level-1/"
        echo "  ✓ Moved CFA L1 (V$i).pdf → Archive/Level-1/"
    fi
done

# Move Level 2 PDFs
for i in 1 2 3 4 5 6; do
    if [ -f "CFA L2 (V$i).pdf" ]; then
        mv "CFA L2 (V$i).pdf" "$ARCHIVE_DIR/Level-2/"
        echo "  ✓ Moved CFA L2 (V$i).pdf → Archive/Level-2/"
    fi
done

# Move Level 3 PDFs
for i in 1 2 3 4 5 6; do
    if [ -f "CFA L3 (V$i).pdf" ]; then
        mv "CFA L3 (V$i).pdf" "$ARCHIVE_DIR/Level-3/"
        echo "  ✓ Moved CFA L3 (V$i).pdf → Archive/Level-3/"
    fi
done

echo ""
echo "======================================================"
echo "✅ Organization Complete!"
echo "======================================================"
echo ""
echo "Structure:"
echo "  CFA-PDFs-Archive/"
echo "  ├── Level-1/  (6 PDFs)"
echo "  ├── Level-2/  (6 PDFs)"
echo "  └── Level-3/  (6 PDFs)"
echo ""
echo "Note: Your CFA Prep Tool also has organized copies at:"
echo "  cfa-prep-tool/pdfs/level1/"
echo "  cfa-prep-tool/pdfs/level2/"
echo "  cfa-prep-tool/pdfs/level3/"
echo ""
