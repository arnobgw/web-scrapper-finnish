# Finnish Medical Dictionary Scraper

A Python web scraper for checking if Finnish medical terms exist in the Terveysportti medical dictionary.

> [!IMPORTANT]
> This scraper requires valid login credentials to access the Terveysportti dictionary.

## Features

- 🔐 **Automatic Authentication** - Logs in automatically with provided credentials
- 🔍 **Automated Search** - Searches Finnish medical terms on [Terveysportti Sanakirjat](https://www.terveysportti.fi/apps/sanakirjat/)
- ✅ **Result Detection** - Returns whether each term is "found" or "not found"
- 📦 **Batch Processing** - Supports searching multiple terms at once
- 🌐 **Smart Driver Management** - Automatically downloads the correct ChromeDriver version
- 🎯 **Configurable** - Run in headless mode or with visible browser

## Installation

1. Install Python dependencies:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

2. Make sure you have Chrome browser installed (Selenium uses ChromeDriver)

## Usage

### Quick Start

1. Edit the credentials in `medical_dictionary_scraper.py`:
```python
EMAIL = "your.email@example.com"
PASSWORD = "your_password"
```

2. Run the script:
```bash
python medical_dictionary_scraper.py
```

### Custom Usage in Your Code

```python
from medical_dictionary_scraper import MedicalDictionaryScraper

# Your credentials
EMAIL = "your.email@example.com"
PASSWORD = "your_password"

# Define your search terms
search_terms = ["Kirjasto", "lääkäri", "sydän", "keuhko"]

# Use the scraper (automatically logs in)
with MedicalDictionaryScraper(email=EMAIL, password=PASSWORD, headless=True) as scraper:
    results = scraper.search_multiple_terms(search_terms)

# Print results
for term, status in results.items():
    print(f'"{term}" = "{status}"')
```

### Parameters

- `email` (str): Your Terveysportti login email - **Required**
- `password` (str): Your Terveysportti password - **Required**
- `headless` (bool): Set to `True` to run browser in background (no GUI), `False` to see the browser window
  - Default: `True`
  - Use `False` for debugging

### Example Output

```
Starting Medical Dictionary Scraper...
Searching for 2 terms

Searching 1/2: Kirjasto
Searching 2/2: lääkäri

==================================================
RESULTS:
==================================================
"Kirjasto" = "not found"
"lääkäri" = "found"
==================================================
```

## How It Works

1. **Authenticates** - Clicks login button, enters credentials, and logs in
2. **Searches** - For each term:
   - Enters the term in the search box
   - Waits for results to load
   - Checks for "Ei tuloksia" (No results) message
   - Returns "found" or "not found" accordingly
3. **Returns Results** - Dictionary mapping each term to its status

## Requirements

- Python 3.7+
- Chrome browser
- selenium
- webdriver-manager

## Notes

- The scraper includes a 1-second delay between searches to be respectful to the server
- If you encounter issues, try running with `headless=False` to see what's happening in the browser
