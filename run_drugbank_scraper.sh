#!/bin/bash
# Quick start script for DrugBank DDI Scraper

echo "=================================================="
echo "   DrugBank DDI Scraper - Quick Start"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please create one with: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if playwright is installed
if ! python -c "import playwright" 2>/dev/null; then
    echo ""
    echo "Installing Playwright..."
    pip install playwright

    echo ""
    echo "Installing Playwright browsers..."
    playwright install chromium
fi

# Check if pandas is installed
if ! python -c "import pandas" 2>/dev/null; then
    echo ""
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

echo ""
echo "=================================================="
echo "   Setup Complete!"
echo "=================================================="
echo ""
echo "Options:"
echo ""
echo "1. Run scraper on FYP_Drug_Interaction_Template.csv"
echo "2. Test scraper with first 5 rows only"
echo "3. Debug: Inspect DrugBank page structure"
echo "4. Debug: Test adding two drugs"
echo "5. Debug: Analyze saved HTML files"
echo "6. Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Starting DrugBank scraper on full CSV file..."
        echo "This will run in non-headless mode so you can watch it work."
        echo ""
        python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv
        ;;
    2)
        echo ""
        echo "Testing scraper with first 5 rows only..."
        python drugbank_ddi_scraper.py FYP_Drug_Interaction_Template.csv --start 0 --end 5 --output test_drugbank_results.csv
        ;;
    3)
        echo ""
        echo "Running page structure debug..."
        python debug_drugbank_page_load.py
        ;;
    4)
        echo ""
        echo "Running drug addition debug (Lisinopril + Amlodipine)..."
        python debug_drugbank_add_drugs.py
        ;;
    5)
        echo ""
        echo "Analyzing saved HTML files..."
        python debug_drugbank_html_analysis.py
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "   Done!"
echo "=================================================="
echo ""
echo "Check the log file for details: drugbank_scraper.log"
echo ""
