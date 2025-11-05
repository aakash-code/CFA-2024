# CFA PDFs - Organization Guide

## Current Structure

Your CFA PDFs are **already organized** in two locations:

### 1. ✅ CFA Prep Tool (Working Directory)
**Location**: `cfa-prep-tool/pdfs/`

```
cfa-prep-tool/pdfs/
├── level1/              ← Level 1 Study Materials
│   ├── CFA L1 (V1).pdf  (8.2 MB)
│   ├── CFA L1 (V2).pdf  (8.6 MB)
│   ├── CFA L1 (V3).pdf  (5.6 MB)
│   ├── CFA L1 (V4).pdf  (8.3 MB)
│   ├── CFA L1 (V5).pdf  (6.9 MB)
│   └── CFA L1 (V6).pdf  (3.4 MB)
│   Total: 41 MB
│
├── level2/              ← Level 2 Study Materials
│   ├── CFA L2 (V1).pdf  (8.3 MB)
│   ├── CFA L2 (V2).pdf  (3.5 MB)
│   ├── CFA L2 (V3).pdf  (3.0 MB)
│   ├── CFA L2 (V4).pdf  (8.2 MB)
│   ├── CFA L2 (V5).pdf  (6.8 MB)
│   └── CFA L2 (V6).pdf  (4.8 MB)
│   Total: 35 MB
│
└── level3/              ← Level 3 Study Materials
    ├── CFA L3 (V1).pdf  (3.9 MB)
    ├── CFA L3 (V2).pdf  (4.4 MB)
    ├── CFA L3 (V3).pdf  (5.2 MB)
    ├── CFA L3 (V4).pdf  (5.0 MB)
    ├── CFA L3 (V5).pdf  (4.8 MB)
    └── CFA L3 (V6).pdf  (2.3 MB)
    Total: 26 MB

TOTAL: 18 PDFs, 102 MB
```

**This is your WORKING directory for the CFA Prep Tool!**

### 2. 📁 Repository Root (Original Copies)
**Location**: `/home/user/CFA-2024/` (root directory)

The original 18 PDFs are still in the repository root (loose files).

## Cleanup Options

### Option A: Archive Root PDFs (Recommended)

Move root PDFs to a clean archive structure:

```bash
cd /home/user/CFA-2024
./organize_pdfs.sh
```

**Result:**
```
CFA-2024/
├── CFA-PDFs-Archive/         ← Clean archive
│   ├── Level-1/ (6 PDFs)
│   ├── Level-2/ (6 PDFs)
│   └── Level-3/ (6 PDFs)
├── cfa-prep-tool/            ← Working tool
│   └── pdfs/ (organized)
└── README.md
```

### Option B: Delete Root Duplicates

Since PDFs are already in `cfa-prep-tool/pdfs/`, you can delete root copies:

```bash
# Be careful with this command!
cd /home/user/CFA-2024
rm "CFA L"*.pdf
```

**Warning**: This permanently deletes the root PDFs. Only do this if you're sure!

### Option C: Keep As-Is

Keep both copies:
- Root PDFs = Backup
- Tool PDFs = Working copies

## How the CFA Prep Tool Uses PDFs

### The tool expects PDFs in:
```
cfa-prep-tool/pdfs/
├── level1/
├── level2/
└── level3/
```

### Extract content from all PDFs:
```bash
cd cfa-prep-tool/backend
python batch_process_pdfs.py
```

This processes all 18 PDFs and creates:
```
cfa-prep-tool/data/extracted/
├── L1_V1_extracted.json
├── L1_V2_extracted.json
├── ... (18 JSON files)
```

## Visual Directory Structure

### Before Organization:
```
CFA-2024/
├── CFA L1 (V1).pdf  ← Scattered
├── CFA L1 (V2).pdf  ← Scattered
├── CFA L2 (V1).pdf  ← Scattered
├── CFA L3 (V1).pdf  ← Scattered
├── ... (all 18 PDFs loose in root)
└── README.md
```

### After Organization:
```
CFA-2024/
├── cfa-prep-tool/
│   ├── pdfs/                    ← ORGANIZED!
│   │   ├── level1/ (6 PDFs)    ← Level 1
│   │   ├── level2/ (6 PDFs)    ← Level 2
│   │   └── level3/ (6 PDFs)    ← Level 3
│   ├── backend/                 ← Python server
│   ├── frontend/                ← Web interface
│   └── data/                    ← Study data
├── CFA L1 (V1).pdf             ← Original (optional: move/delete)
├── CFA L1 (V2).pdf             ← Original (optional: move/delete)
└── ... (other root PDFs)
```

## Verification

Check organization:
```bash
# View tool's organized PDFs
ls -lh cfa-prep-tool/pdfs/level1/
ls -lh cfa-prep-tool/pdfs/level2/
ls -lh cfa-prep-tool/pdfs/level3/

# View root PDFs
ls -lh *.pdf
```

Count PDFs:
```bash
# Tool PDFs (should be 18)
find cfa-prep-tool/pdfs -name "*.pdf" | wc -l

# Root PDFs (currently 18)
ls -1 *.pdf 2>/dev/null | wc -l
```

## Summary

| Location | Status | Purpose |
|----------|--------|---------|
| `cfa-prep-tool/pdfs/level1/` | ✅ Organized | Level 1 working files |
| `cfa-prep-tool/pdfs/level2/` | ✅ Organized | Level 2 working files |
| `cfa-prep-tool/pdfs/level3/` | ✅ Organized | Level 3 working files |
| Root directory `*.pdf` | 📁 Original | Backup/original files |

## Recommended Action

**Run the organization script to clean up root:**
```bash
cd /home/user/CFA-2024
./organize_pdfs.sh
```

This will:
1. Create `CFA-PDFs-Archive/` with clean structure
2. Move root PDFs to archive by level
3. Keep tool PDFs untouched
4. Clean up your repository root

## Next Steps After Organization

1. **Verify tool PDFs**: `ls cfa-prep-tool/pdfs/*/`
2. **Start the tool**: `cd cfa-prep-tool && ./start.sh`
3. **Extract PDFs**: `cd backend && python batch_process_pdfs.py`
4. **Start studying**: Open http://localhost:8000

---

**Your PDFs are organized and ready to use!** 📚✨
