#!/usr/bin/env python3
"""
Console Log Capture Script for Revenue Calculation Debugging
Captures JavaScript console output from the BigQuery application
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up Chrome driver with console logging enabled"""
    print("🔧 Setting up Chrome driver...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Enable logging
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver setup successful")
        return driver
    except Exception as e:
        print(f"❌ Failed to setup Chrome driver: {e}")
        return None

def capture_console_logs():
    """Capture console logs from the revenue calculation page"""
    print("🔍 Starting console log capture for revenue calculation debugging...")
    
    driver = setup_driver()
    if not driver:
        return None
    
    url = "http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt"
    console_logs = []
    
    try:
        print(f"📍 Navigating to {url}...")
        driver.get(url)
        
        print("✅ Page loaded successfully")
        print("⏱️  Waiting for JavaScript execution to complete...")
        
        # Wait for the page to load and JavaScript to execute
        time.sleep(5)
        
        # Try to wait for any revenue-related content
        try:
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            print("✅ Document ready state complete")
        except TimeoutException:
            print("⚠️  Timeout waiting for document ready, but continuing...")
        
        # Additional wait for async operations
        print("⏱️  Waiting for async operations to complete...")
        time.sleep(10)
        
        # Get console logs
        print("📋 Retrieving console logs...")
        logs = driver.get_log('browser')
        
        for log_entry in logs:
            timestamp = datetime.fromtimestamp(log_entry['timestamp'] / 1000.0).isoformat()
            console_logs.append({
                'timestamp': timestamp,
                'level': log_entry['level'],
                'message': log_entry['message'],
                'source': log_entry.get('source', 'unknown')
            })
        
        # Also try to execute JavaScript to get any additional console content
        try:
            # Try to get any stored console messages or state
            js_state = driver.execute_script("""
                return {
                    url: window.location.href,
                    title: document.title,
                    readyState: document.readyState,
                    hasJQuery: typeof jQuery !== 'undefined',
                    hasBootstrap: typeof bootstrap !== 'undefined'
                };
            """)
            print(f"📄 Page state: {js_state}")
        except Exception as e:
            print(f"⚠️  Could not get JS state: {e}")
        
    except Exception as e:
        print(f"❌ Error during page capture: {e}")
    
    finally:
        driver.quit()
        print("🔒 Browser closed")
    
    return console_logs

def analyze_logs(console_logs):
    """Analyze and categorize the console logs"""
    if not console_logs:
        print("❌ No console logs captured")
        return
    
    print(f"\n📊 CONSOLE LOG ANALYSIS ({len(console_logs)} total logs)")
    print("=" * 80)
    
    # Categorize logs
    revenue_logs = []
    error_logs = []
    warning_logs = []
    info_logs = []
    
    keywords_revenue = ['revenue', 'projection', 'comparable', 'loading', 'calculated', 'top 20', '🏆', '✅', '$']
    
    for log in console_logs:
        message = log['message'].lower()
        
        # Check for revenue-related content
        if any(keyword in message for keyword in keywords_revenue):
            revenue_logs.append(log)
        
        # Categorize by level
        level = log['level']
        if level == 'SEVERE':
            error_logs.append(log)
        elif level == 'WARNING':
            warning_logs.append(log)
        else:
            info_logs.append(log)
    
    # Print revenue-related logs
    print(f"\n🎯 REVENUE-RELATED LOGS ({len(revenue_logs)} found):")
    print("-" * 50)
    for log in revenue_logs:
        print(f"[{log['timestamp']}] [{log['level']}] {log['message']}")
    
    # Print errors
    print(f"\n❌ ERROR LOGS ({len(error_logs)} found):")
    print("-" * 50)
    for log in error_logs:
        print(f"[{log['timestamp']}] [{log['level']}] {log['message']}")
    
    # Print warnings
    print(f"\n⚠️  WARNING LOGS ({len(warning_logs)} found):")
    print("-" * 50)
    for log in warning_logs:
        print(f"[{log['timestamp']}] [{log['level']}] {log['message']}")
    
    # Print all logs
    print(f"\n📋 ALL CONSOLE LOGS ({len(console_logs)} total):")
    print("-" * 50)
    for log in console_logs:
        print(f"[{log['timestamp']}] [{log['level']}] {log['message']}")
    
    return {
        'total': len(console_logs),
        'revenue_related': len(revenue_logs),
        'errors': len(error_logs),
        'warnings': len(warning_logs),
        'info': len(info_logs)
    }

def main():
    """Main execution function"""
    print("🚀 Revenue Calculation Console Log Capture")
    print("=" * 50)
    
    # Capture logs
    console_logs = capture_console_logs()
    
    if not console_logs:
        print("❌ Failed to capture console logs")
        return
    
    # Analyze and display results
    stats = analyze_logs(console_logs)
    
    # Save logs to file for reference
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"console_logs_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(console_logs, f, indent=2)
        print(f"\n💾 Console logs saved to: {filename}")
    except Exception as e:
        print(f"⚠️  Could not save logs to file: {e}")
    
    print(f"\n🎉 Console log capture completed successfully!")
    if stats:
        print(f"📊 Total logs: {stats['total']}")
        print(f"🎯 Revenue-related: {stats['revenue_related']}")
        print(f"❌ Errors: {stats['errors']}")
        print(f"⚠️  Warnings: {stats['warnings']}")

if __name__ == "__main__":
    main()