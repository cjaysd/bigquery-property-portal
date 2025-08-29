#!/usr/bin/env python3
"""
Detailed Console Log Capture with Value Extraction
Captures JavaScript console output and extracts the actual projection values
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
    print("🔧 Setting up Chrome driver for detailed capture...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
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

def extract_projection_values(driver):
    """Extract the actual projection values from the page"""
    print("🔍 Extracting projection values from JavaScript...")
    
    try:
        # Execute JavaScript to get the projection data
        projection_data = driver.execute_script("""
            // Try to get projection data from various possible sources
            var results = {};
            
            // Check if there are any global variables with projection data
            if (typeof window.projectionData !== 'undefined') {
                results.projectionData = window.projectionData;
            }
            
            // Check if there are any elements containing revenue data
            var revenueElements = document.querySelectorAll('[data-revenue], .revenue, .projection');
            results.revenueElements = [];
            for (var i = 0; i < revenueElements.length; i++) {
                results.revenueElements.push({
                    tag: revenueElements[i].tagName,
                    class: revenueElements[i].className,
                    text: revenueElements[i].textContent,
                    innerHTML: revenueElements[i].innerHTML
                });
            }
            
            // Try to get data from any input fields or display elements
            var inputs = document.querySelectorAll('input[type="number"], .amount, .currency');
            results.inputValues = [];
            for (var i = 0; i < inputs.length; i++) {
                results.inputValues.push({
                    tag: inputs[i].tagName,
                    class: inputs[i].className,
                    value: inputs[i].value || inputs[i].textContent,
                    placeholder: inputs[i].placeholder
                });
            }
            
            // Check for any tables or structured data
            var tables = document.querySelectorAll('table, .table');
            results.tableData = [];
            for (var i = 0; i < tables.length; i++) {
                results.tableData.push({
                    rows: tables[i].rows.length,
                    innerHTML: tables[i].innerHTML.substring(0, 500) + '...'
                });
            }
            
            return results;
        """)
        
        return projection_data
        
    except Exception as e:
        print(f"⚠️  Could not extract projection values: {e}")
        return None

def inject_console_interceptor(driver):
    """Inject JavaScript to intercept and store console messages"""
    print("💉 Injecting console interceptor...")
    
    try:
        driver.execute_script("""
            // Store original console methods
            window.originalConsole = {
                log: console.log,
                info: console.info,
                warn: console.warn,
                error: console.error
            };
            
            // Array to store intercepted messages
            window.interceptedConsole = [];
            
            // Override console methods
            ['log', 'info', 'warn', 'error'].forEach(function(method) {
                console[method] = function() {
                    // Store the message
                    var message = {
                        method: method,
                        timestamp: new Date().toISOString(),
                        args: Array.prototype.slice.call(arguments).map(function(arg) {
                            if (typeof arg === 'object') {
                                try {
                                    return JSON.parse(JSON.stringify(arg));
                                } catch (e) {
                                    return '[Object: ' + Object.prototype.toString.call(arg) + ']';
                                }
                            }
                            return arg;
                        })
                    };
                    window.interceptedConsole.push(message);
                    
                    // Call original console method
                    window.originalConsole[method].apply(console, arguments);
                };
            });
            
            console.log('🔍 Console interceptor activated');
        """)
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not inject console interceptor: {e}")
        return False

def get_intercepted_console_logs(driver):
    """Retrieve the intercepted console logs"""
    try:
        logs = driver.execute_script("return window.interceptedConsole || [];")
        return logs
    except Exception as e:
        print(f"⚠️  Could not retrieve intercepted logs: {e}")
        return []

def detailed_console_capture():
    """Main function to capture detailed console information"""
    print("🚀 Starting DETAILED Revenue Calculation Console Capture")
    print("=" * 60)
    
    driver = setup_driver()
    if not driver:
        return None
    
    url = "http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt"
    
    try:
        print(f"📍 Navigating to {url}...")
        
        # Inject console interceptor before loading the page
        driver.get("about:blank")
        inject_console_interceptor(driver)
        
        # Now load the actual page
        driver.get(url)
        print("✅ Page loaded with console interceptor active")
        
        # Wait for JavaScript execution
        print("⏱️  Waiting for JavaScript execution (15 seconds)...")
        time.sleep(15)
        
        # Get intercepted console logs
        print("📋 Retrieving intercepted console logs...")
        intercepted_logs = get_intercepted_console_logs(driver)
        
        # Extract projection values
        print("💰 Extracting projection values...")
        projection_data = extract_projection_values(driver)
        
        # Get standard browser logs as backup
        browser_logs = driver.get_log('browser')
        
        return {
            'intercepted_logs': intercepted_logs,
            'projection_data': projection_data,
            'browser_logs': browser_logs,
            'page_url': driver.current_url,
            'page_title': driver.title
        }
        
    except Exception as e:
        print(f"❌ Error during detailed capture: {e}")
        return None
        
    finally:
        driver.quit()
        print("🔒 Browser closed")

def analyze_detailed_results(results):
    """Analyze the detailed capture results"""
    if not results:
        print("❌ No results to analyze")
        return
    
    print(f"\n📊 DETAILED ANALYSIS RESULTS")
    print("=" * 80)
    
    # Analyze intercepted logs
    intercepted = results.get('intercepted_logs', [])
    print(f"\n🎯 INTERCEPTED CONSOLE LOGS ({len(intercepted)} found):")
    print("-" * 50)
    
    revenue_logs = []
    for log in intercepted:
        message_str = ' '.join(str(arg) for arg in log.get('args', []))
        if any(keyword in message_str.lower() for keyword in ['revenue', 'projection', 'calculated', '🏆', '✅', '$']):
            revenue_logs.append(log)
            print(f"[{log.get('timestamp', 'unknown')}] [{log.get('method', 'unknown').upper()}]")
            for i, arg in enumerate(log.get('args', [])):
                if isinstance(arg, dict):
                    print(f"  Arg {i}: {json.dumps(arg, indent=4)}")
                else:
                    print(f"  Arg {i}: {arg}")
            print()
    
    # Analyze projection data
    projection_data = results.get('projection_data', {})
    print(f"\n💰 EXTRACTED PROJECTION DATA:")
    print("-" * 50)
    if projection_data:
        print(json.dumps(projection_data, indent=2))
    else:
        print("No projection data extracted")
    
    # Show summary
    print(f"\n📈 SUMMARY:")
    print(f"  • Total intercepted logs: {len(intercepted)}")
    print(f"  • Revenue-related logs: {len(revenue_logs)}")
    print(f"  • Page title: {results.get('page_title', 'Unknown')}")
    print(f"  • Final URL: {results.get('page_url', 'Unknown')}")
    
    return results

def main():
    """Main execution function"""
    results = detailed_console_capture()
    
    if results:
        analyzed = analyze_detailed_results(results)
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detailed_console_capture_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save detailed results: {e}")
    
    print(f"\n🎉 Detailed console capture completed!")

if __name__ == "__main__":
    main()