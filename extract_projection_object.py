#!/usr/bin/env python3
"""
Extract the actual projection object values by modifying the console.log calls
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up Chrome driver"""
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
        return driver
    except Exception as e:
        print(f"❌ Failed to setup Chrome driver: {e}")
        return None

def inject_detailed_console_override(driver):
    """Inject a more comprehensive console override"""
    print("💉 Injecting comprehensive console override...")
    
    try:
        driver.execute_script("""
            // Store all console output with full object serialization
            window.fullConsoleLog = [];
            
            // Enhanced JSON serialization that handles circular references
            function safeStringify(obj, indent = 2) {
                const cache = new Set();
                return JSON.stringify(obj, (key, value) => {
                    if (typeof value === "object" && value !== null) {
                        if (cache.has(value)) {
                            return "[Circular Reference]";
                        }
                        cache.add(value);
                    }
                    return value;
                }, indent);
            }
            
            // Override console methods
            const originalConsole = {
                log: console.log,
                info: console.info,
                warn: console.warn,
                error: console.error
            };
            
            ['log', 'info', 'warn', 'error'].forEach(function(method) {
                console[method] = function() {
                    const timestamp = new Date().toISOString();
                    const args = Array.prototype.slice.call(arguments);
                    
                    // Process each argument
                    const processedArgs = args.map(arg => {
                        if (typeof arg === 'object' && arg !== null) {
                            try {
                                return {
                                    type: 'object',
                                    value: safeStringify(arg),
                                    keys: Object.keys(arg),
                                    constructor: arg.constructor.name
                                };
                            } catch (e) {
                                return {
                                    type: 'object',
                                    value: '[Object - Could not serialize]',
                                    error: e.message
                                };
                            }
                        } else {
                            return {
                                type: typeof arg,
                                value: String(arg)
                            };
                        }
                    });
                    
                    window.fullConsoleLog.push({
                        method: method,
                        timestamp: timestamp,
                        originalArgs: args,
                        processedArgs: processedArgs
                    });
                    
                    // Also call the original console method
                    originalConsole[method].apply(console, arguments);
                };
            });
            
            console.log('🔍 Comprehensive console override activated');
        """)
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not inject console override: {e}")
        return False

def extract_console_and_projections():
    """Extract both console logs and projection data"""
    print("🚀 Starting Comprehensive Projection Data Extraction")
    print("=" * 60)
    
    driver = setup_driver()
    if not driver:
        return None
    
    url = "http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt"
    
    try:
        # Start with a blank page and inject our console override
        driver.get("about:blank")
        if not inject_detailed_console_override(driver):
            return None
        
        print(f"📍 Loading page: {url}")
        driver.get(url)
        
        print("⏱️  Waiting for all JavaScript execution (20 seconds)...")
        time.sleep(20)
        
        # Get our captured console logs
        print("📋 Retrieving comprehensive console logs...")
        full_console_log = driver.execute_script("return window.fullConsoleLog || [];")
        
        # Try to get any projection data from the page
        projection_values = driver.execute_script("""
            // Try to find any global variables or data related to projections
            var data = {};
            
            // Check common variable names
            if (typeof window.projectionData !== 'undefined') data.projectionData = window.projectionData;
            if (typeof window.calculatedProjections !== 'undefined') data.calculatedProjections = window.calculatedProjections;
            if (typeof window.revenueProjections !== 'undefined') data.revenueProjections = window.revenueProjections;
            
            // Try to extract values from the DOM
            var monthlyElement = document.querySelector('.hero-metric-value.revenue');
            if (monthlyElement) {
                data.monthlyRevenue = monthlyElement.textContent.trim();
            }
            
            var annualElements = document.querySelectorAll('.hero-metric-value.revenue');
            if (annualElements.length > 1) {
                data.annualRevenue = annualElements[1].textContent.trim();
            }
            
            // Look for table data
            var tables = document.querySelectorAll('table');
            data.tableCount = tables.length;
            
            return data;
        """)
        
        return {
            'full_console_log': full_console_log,
            'projection_values': projection_values,
            'page_title': driver.title,
            'page_url': driver.current_url
        }
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return None
        
    finally:
        driver.quit()

def analyze_comprehensive_results(results):
    """Analyze the comprehensive results"""
    if not results:
        print("❌ No results to analyze")
        return
    
    print(f"\n📊 COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    # Analyze console logs
    console_logs = results.get('full_console_log', [])
    print(f"\n🎯 COMPREHENSIVE CONSOLE ANALYSIS ({len(console_logs)} total logs):")
    print("-" * 50)
    
    # Find projection-related logs
    projection_logs = []
    for log in console_logs:
        # Check if any argument contains projection-related content
        for arg in log.get('processedArgs', []):
            arg_value = str(arg.get('value', '')).lower()
            if any(keyword in arg_value for keyword in ['projection', 'revenue', 'calculated', 'comparable']):
                projection_logs.append(log)
                break
    
    print(f"\n💰 PROJECTION-RELATED LOGS ({len(projection_logs)} found):")
    for log in projection_logs:
        print(f"\n[{log.get('timestamp')}] {log.get('method', 'unknown').upper()}:")
        for i, arg in enumerate(log.get('processedArgs', [])):
            print(f"  Argument {i} ({arg.get('type')}):")
            if arg.get('type') == 'object':
                print(f"    Keys: {arg.get('keys', [])}")
                print(f"    Value: {arg.get('value', 'N/A')}")
            else:
                print(f"    Value: {arg.get('value', 'N/A')}")
    
    # Show projection values
    projection_values = results.get('projection_values', {})
    print(f"\n💵 EXTRACTED PROJECTION VALUES:")
    print("-" * 50)
    print(json.dumps(projection_values, indent=2))
    
    return results

def main():
    """Main execution"""
    results = extract_console_and_projections()
    
    if results:
        analyze_comprehensive_results(results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_projection_data_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
    
    print("\n🎉 Comprehensive extraction completed!")

if __name__ == "__main__":
    main()