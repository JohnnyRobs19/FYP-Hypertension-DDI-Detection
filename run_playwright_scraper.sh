#!/bin/bash
# Quick start script for Playwright DDI Scraper

echo "=================================================="
echo "   Playwright DDI Scraper - Quick Start"
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
echo "1. Create a sample drug pairs file"
echo "2. Run scraper with existing file"
echo "3. Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Creating sample drug pairs file..."
        python create_sample_drug_pairs.py \
            --mode template \
            --output drug_pairs_sample.xlsx

        echo ""
        echo "Sample file created: drug_pairs_sample.xlsx"
        echo ""
        read -p "Do you want to run the scraper on this file now? (y/n): " run_now

        if [[ $run_now == "y" || $run_now == "Y" ]]; then
            echo ""
            echo "Starting scraper..."
            python playwright_ddi_scraper.py drug_pairs_sample.xlsx
        fi
        ;;
    2)
        echo ""
        read -p "Enter the path to your Excel file: " excel_file

        if [ ! -f "$excel_file" ]; then
            echo "Error: File not found: $excel_file"
            exit 1
        fi

        echo ""
        echo "Starting scraper..."
        python playwright_ddi_scraper.py "$excel_file"
        ;;
    3)
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
echo "Check the log file for details: playwright_ddi_scraper.log"
echo ""
