"""
Finnish Medical Dictionary Scraper
Scrapes Terveysportti medical dictionary to check if terms are found or not.
Requires authentication to access the dictionary.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time


class MedicalDictionaryScraper:
    def __init__(self, email, password, headless=True):
        """
        Initialize the scraper with Chrome WebDriver.
        
        Args:
            email (str): Login email address
            password (str): Login password
            headless (bool): Run browser in headless mode (no GUI)
        """
        self.url = "https://www.terveysportti.fi/apps/sanakirjat/"
        self.email = email
        self.password = password
        self.is_logged_in = False
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver_manager to automatically get the correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def login(self):
        """
        Log in to the Terveysportti website.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            print("Navigating to website...")
            self.driver.get(self.url)
            
            # Wait for and click the login button (Kirjaudu)
            print("Clicking login button...")
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/apps/duoauth/auth')]"))
            )
            login_button.click()
            
            # Wait for login form to appear
            print("Waiting for login form...")
            time.sleep(2)
            
            # Enter username/email
            print("Entering credentials...")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_input.clear()
            username_input.send_keys(self.email)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "password")
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Click login button
            print("Submitting login form...")
            login_submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_submit.click()
            
            # Wait for redirect back to dictionary page
            print("Waiting for login to complete...")
            time.sleep(5)
            
            # Check if we're back at the dictionary page
            if "sanakirjat" in self.driver.current_url:
                print("✓ Login successful!")
                self.is_logged_in = True
                return True
            else:
                print("✗ Login may have failed - unexpected URL")
                return False
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False
    
    def search_term(self, term):
        """
        Search for a single term in the medical dictionary.
        
        Args:
            term (str): The Finnish medical term to search
            
        Returns:
            str: "found" or "not found"
        """
        try:
            # Navigate to the website
            self.driver.get(self.url)
            
            # Wait for the search input to be present
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search'], input.form-control"))
            )
            
            # Clear and enter the search term
            search_input.clear()
            search_input.send_keys(term)
            search_input.send_keys(Keys.RETURN)
            
            # Wait a bit for results to load
            time.sleep(3)
            
            # Get page source for checking
            page_source = self.driver.page_source
            
            # Primary check: "Ei tuloksia" (No results) indicates not found
            if "Ei tuloksia" in page_source:
                return "not found"
            
            # Secondary check: "Yhteensä" (Total) indicates results were found
            # Example: "Yhteensä 305 osumaa haulla lääkäri"
            if "Yhteensä" in page_source and "osumaa" in page_source:
                return "found"
            
            # Tertiary check: Look for dictionary section headers which appear with results
            if "Lääketieteen termit" in page_source or "termit" in page_source.lower():
                return "found"
            
            # If we can't determine, check for "not found" indicators more broadly
            page_source_lower = page_source.lower()
            if "ei tuloksia" in page_source_lower or "ei löytynyt" in page_source_lower:
                return "not found"
            
            # Default to "found" if no clear "not found" indicator
            # This is safer than defaulting to "not found"
            return "found"
            
        except TimeoutException:
            print(f"Timeout while searching for term: {term}")
            return "error"
        except Exception as e:
            print(f"Error searching for term '{term}': {str(e)}")
            return "error"
    
    def search_multiple_terms(self, terms):
        """
        Search for multiple terms and return results as a dictionary.
        Automatically logs in if not already logged in.
        
        Args:
            terms (list): List of Finnish medical terms to search
            
        Returns:
            dict: Dictionary mapping terms to their status ("found" or "not found")
        """
        # Login first if not already logged in
        if not self.is_logged_in:
            if not self.login():
                print("Failed to login. Cannot proceed with searches.")
                return {term: "error" for term in terms}
        
        results = {}
        
        for i, term in enumerate(terms, 1):
            print(f"Searching {i}/{len(terms)}: {term}")
            status = self.search_term(term)
            results[term] = status
            
            # Small delay between searches to be respectful to the server
            time.sleep(1)
        
        return results
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Example usage of the scraper."""
    # Login credentials
    EMAIL = ""
    PASSWORD = ""
    
    # Example search terms
    search_terms = ["Kirjasto", "lääkäri", "Sydän", "lentokone"]

    print("Starting Medical Dictionary Scraper...")
    print(f"Searching for {len(search_terms)} terms\n")
    
    # Use context manager to ensure browser closes properly
    with MedicalDictionaryScraper(email=EMAIL, password=PASSWORD, headless=False) as scraper:
        results = scraper.search_multiple_terms(search_terms)
    
    # Display results
    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    for term, status in results.items():
        print(f'"{term}" = "{status}"')
    print("="*50)
    
    return results


if __name__ == "__main__":
    main()
