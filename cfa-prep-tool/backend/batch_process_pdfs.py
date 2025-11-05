"""Batch PDF processor for organized CFA materials."""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from pdf_extractor import CFAPDFExtractor

def process_all_levels():
    """Process all PDFs organized by level."""

    base_dir = os.path.dirname(os.path.dirname(__file__))
    pdf_base = os.path.join(base_dir, "pdfs")
    output_dir = os.path.join(base_dir, "data", "extracted")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    levels = {
        "level1": "L1",
        "level2": "L2",
        "level3": "L3"
    }

    all_results = []

    print("=" * 70)
    print("CFA PDF Batch Processor")
    print("=" * 70)
    print()

    for folder, level_code in levels.items():
        level_dir = os.path.join(pdf_base, folder)

        if not os.path.exists(level_dir):
            print(f"⚠️  Skipping {folder} - directory not found")
            continue

        print(f"\n📚 Processing {level_code} PDFs from {folder}/")
        print("-" * 70)

        # Get all PDFs in this level
        pdf_files = sorted([f for f in os.listdir(level_dir) if f.endswith('.pdf')])

        if not pdf_files:
            print(f"  No PDFs found in {folder}/")
            continue

        print(f"  Found {len(pdf_files)} PDFs")

        # Process each PDF
        for pdf_file in pdf_files:
            pdf_path = os.path.join(level_dir, pdf_file)

            print(f"\n  Processing: {pdf_file}")

            extractor = CFAPDFExtractor(level_dir, output_dir)
            result = extractor.process_pdf(pdf_file)

            if result:
                all_results.append(result)
                print(f"    ✓ {result['total_pages']} pages")
                print(f"    ✓ {len(result['sections'])} sections")
                print(f"    ✓ {len(result['formulas'])} formulas")
            else:
                print(f"    ✗ Failed to process")

    # Summary
    print("\n" + "=" * 70)
    print("Processing Complete!")
    print("=" * 70)

    if all_results:
        total_pages = sum(r['total_pages'] for r in all_results)
        total_sections = sum(len(r['sections']) for r in all_results)
        total_formulas = sum(len(r['formulas']) for r in all_results)

        print(f"\n📊 Summary:")
        print(f"  • PDFs processed: {len(all_results)}")
        print(f"  • Total pages: {total_pages:,}")
        print(f"  • Sections extracted: {total_sections:,}")
        print(f"  • Formulas found: {total_formulas:,}")

        # Breakdown by level
        print(f"\n📈 By Level:")
        for level_code in ["L1", "L2", "L3"]:
            level_pdfs = [r for r in all_results if r['level'] == level_code]
            if level_pdfs:
                pages = sum(r['total_pages'] for r in level_pdfs)
                print(f"  • {level_code}: {len(level_pdfs)} PDFs, {pages:,} pages")

        print(f"\n💾 Extracted data saved to: {output_dir}")

    else:
        print("\n⚠️  No PDFs were successfully processed")

    print()
    return all_results

if __name__ == "__main__":
    results = process_all_levels()

    if results:
        print("✅ All PDFs processed successfully!")
        print("\nNext steps:")
        print("  1. Review extracted JSON files in data/extracted/")
        print("  2. Use the web app to generate flashcards and quizzes")
        print("  3. Start studying!")
    else:
        print("❌ Processing failed. Check the errors above.")
        sys.exit(1)
