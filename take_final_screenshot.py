#!/usr/bin/env python3

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def take_final_screenshot():
    """Take a final screenshot showing the comparables table"""
    
    print("Taking final screenshot of comparables table...")
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Remove headless to see the page
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the page
        target_url = 'http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt'
        print(f"Navigating to: {target_url}")
        
        driver.get(target_url)
        
        # Wait for page to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Page loaded, waiting for comparables to load...")
        
        # Wait for comparables to load
        time.sleep(10)
        
        # Try to scroll to comparables section
        try:
            # Look for comparables section
            comparables_section = driver.find_element(By.CSS_SELECTOR, 
                "[id*='comparable'], [class*='comparable'], .property-table, table")
            driver.execute_script("arguments[0].scrollIntoView(true);", comparables_section)
            time.sleep(2)
            print("Scrolled to comparables section")
        except:
            print("Could not find comparables section to scroll to")
        
        # Take screenshots
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Full page screenshot
        full_screenshot = f"/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery/final-screenshot-full-{timestamp}.png"
        driver.save_screenshot(full_screenshot)
        print(f"Full page screenshot: {full_screenshot}")
        
        # Try to get a focused screenshot of the table area
        try:
            table_elements = driver.find_elements(By.CSS_SELECTOR, "table, .property-table, .comparables-container")
            if table_elements:
                table = table_elements[0]
                location = table.location
                size = table.size
                
                # Take screenshot of specific element
                focused_screenshot = f"/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery/final-screenshot-table-{timestamp}.png"
                
                # Scroll element into view and take screenshot
                driver.execute_script("arguments[0].scrollIntoView(true);", table)
                time.sleep(1)
                table.screenshot(focused_screenshot)
                print(f"Table screenshot: {focused_screenshot}")
        except Exception as e:
            print(f"Could not take table-specific screenshot: {e}")
        
        # Extract table data for verification
        try:
            # Get all table rows
            rows = driver.find_elements(By.CSS_SELECTOR, "tr, .property-row")
            print(f"\nFound {len(rows)} table rows")
            
            table_data = []
            for i, row in enumerate(rows[:10]):  # First 10 rows
                cells = row.find_elements(By.CSS_SELECTOR, "td, th, .property-cell")
                row_text = [cell.text.strip() for cell in cells if cell.text.strip()]
                if row_text:
                    table_data.append({
                        'row_index': i,
                        'cells': row_text,
                        'full_text': row.text.strip()
                    })
            
            print("\nTable data extracted:")
            for row in table_data[:5]:  # First 5 rows
                print(f"Row {row['row_index']}: {row['full_text'][:100]}...")
            
        except Exception as e:
            print(f"Could not extract table data: {e}")
        
        # Wait a moment before closing
        time.sleep(3)
        
        return {
            'full_screenshot': full_screenshot,
            'table_data_rows': len(table_data) if 'table_data' in locals() else 0,
            'success': True
        }
        
    except Exception as e:
        print(f"Screenshot error: {e}")
        return {'error': str(e), 'success': False}
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    result = take_final_screenshot()
    print(f"\nScreenshot result: {result}")