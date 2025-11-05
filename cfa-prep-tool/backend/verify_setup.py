"""Simple script to verify and test the CFA Prep Tool setup."""
import os
import sys

def check_setup():
    """Check if everything is set up correctly."""

    print("=" * 70)
    print("CFA Prep Tool - Setup Verification")
    print("=" * 70)
    print()

    checks_passed = 0
    checks_total = 0

    # Check 1: Python packages
    checks_total += 1
    print("1. Checking Python packages...")
    try:
        import fastapi
        import sqlalchemy
        import uvicorn
        try:
            import fitz  # PyMuPDF
            print("   ✓ All required packages installed")
            checks_passed += 1
        except ImportError:
            print("   ⚠️  PyMuPDF not installed. Run: pip install PyMuPDF")
    except ImportError as e:
        print(f"   ✗ Missing package: {e}")
        print("   Run: pip install -r requirements.txt")

    # Check 2: PDF files
    checks_total += 1
    print("\n2. Checking PDF organization...")
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdfs")

    if os.path.exists(pdf_dir):
        l1_pdfs = len([f for f in os.listdir(os.path.join(pdf_dir, "level1")) if f.endswith('.pdf')]) if os.path.exists(os.path.join(pdf_dir, "level1")) else 0
        l2_pdfs = len([f for f in os.listdir(os.path.join(pdf_dir, "level2")) if f.endswith('.pdf')]) if os.path.exists(os.path.join(pdf_dir, "level2")) else 0
        l3_pdfs = len([f for f in os.listdir(os.path.join(pdf_dir, "level3")) if f.endswith('.pdf')]) if os.path.exists(os.path.join(pdf_dir, "level3")) else 0

        total_pdfs = l1_pdfs + l2_pdfs + l3_pdfs

        if total_pdfs == 18:
            print(f"   ✓ All 18 PDFs organized (L1: {l1_pdfs}, L2: {l2_pdfs}, L3: {l3_pdfs})")
            checks_passed += 1
        else:
            print(f"   ⚠️  Found {total_pdfs} PDFs (expected 18)")
    else:
        print("   ✗ PDF directory not found")

    # Check 3: Environment file
    checks_total += 1
    print("\n3. Checking environment configuration...")
    env_file = os.path.join(os.path.dirname(__file__), ".env")

    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if "ANTHROPIC_API_KEY" in content and "your_api_key_here" not in content:
                print("   ✓ API key configured")
                checks_passed += 1
            else:
                print("   ⚠️  API key not set in .env file")
                print("      Get your key from: https://console.anthropic.com/")
    else:
        print("   ⚠️  .env file not found")
        print("      Copy .env.example to .env and add your API key")

    # Check 4: Database
    checks_total += 1
    print("\n4. Checking database...")
    try:
        from database import init_db, SessionLocal
        init_db()
        db = SessionLocal()
        db.close()
        print("   ✓ Database initialized successfully")
        checks_passed += 1
    except Exception as e:
        print(f"   ✗ Database error: {e}")

    # Check 5: Directory structure
    checks_total += 1
    print("\n5. Checking directory structure...")
    required_dirs = ["data", "data/extracted", "pdfs"]
    base_dir = os.path.dirname(os.path.dirname(__file__))

    all_exist = all(os.path.exists(os.path.join(base_dir, d)) for d in required_dirs)

    if all_exist:
        print("   ✓ All required directories exist")
        checks_passed += 1
    else:
        print("   ⚠️  Some directories missing")

    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)

    if checks_passed == checks_total:
        print("\n✅ Setup complete! You're ready to use the CFA Prep Tool.")
        print("\nTo start the server:")
        print("  python app.py")
        print("\nThen open: http://localhost:8000")
        return True
    else:
        print("\n⚠️  Some setup steps are incomplete. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
