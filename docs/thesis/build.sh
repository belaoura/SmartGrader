#!/bin/bash
# SmartGrader Thesis Build Script
# Generates PDF and DOCX from Markdown sources

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
THESIS_DIR="$SCRIPT_DIR"
FIGURES_DIR="$(dirname "$SCRIPT_DIR")/figures"

echo "=== SmartGrader Thesis Builder ==="

# Step 1: Generate UML diagrams (if plantuml is available)
if command -v plantuml &> /dev/null; then
    echo "Generating UML diagrams..."
    mkdir -p "$FIGURES_DIR/generated"
    plantuml -tpng "$FIGURES_DIR/uml/"*.puml -o "$FIGURES_DIR/generated/"
    echo "UML diagrams generated."
else
    echo "WARNING: plantuml not found. Skipping diagram generation."
    echo "Install: apt install plantuml (Linux) or brew install plantuml (macOS)"
fi

# Step 2: Build PDF via XeLaTeX
if command -v pandoc &> /dev/null; then
    echo "Building PDF..."
    pandoc "$THESIS_DIR/metadata.yaml" \
        "$THESIS_DIR"/0*.md \
        --from markdown \
        --to pdf \
        --pdf-engine=xelatex \
        --bibliography="$THESIS_DIR/bibliography.bib" \
        --citeproc \
        --number-sections \
        --toc \
        --resource-path="$FIGURES_DIR" \
        -o "$THESIS_DIR/thesis.pdf"
    echo "PDF built: $THESIS_DIR/thesis.pdf"

    # Step 3: Build DOCX
    echo "Building DOCX..."
    pandoc "$THESIS_DIR/metadata.yaml" \
        "$THESIS_DIR"/0*.md \
        --from markdown \
        --to docx \
        --bibliography="$THESIS_DIR/bibliography.bib" \
        --citeproc \
        --number-sections \
        --toc \
        --resource-path="$FIGURES_DIR" \
        -o "$THESIS_DIR/thesis.docx"
    echo "DOCX built: $THESIS_DIR/thesis.docx"
else
    echo "ERROR: pandoc not found. Install from https://pandoc.org/installing.html"
    exit 1
fi

echo "=== Build complete ==="
