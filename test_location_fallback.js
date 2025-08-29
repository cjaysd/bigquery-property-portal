const { chromium } = require('playwright');
const fs = require('fs');

async function testLocationFallback() {
    let browser;
    let consoleMessages = [];
    
    try {
        // Launch browser
        browser = await chromium.launch({ 
            headless: false,  // Set to false to see what's happening
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Set up console logging
        page.on('console', (message) => {
            const timestamp = new Date().toISOString();
            const logEntry = {
                timestamp,
                type: message.type(),
                text: message.text(),
                location: message.location()
            };
            consoleMessages.push(logEntry);
            console.log(`[${timestamp}] ${message.type().toUpperCase()}: ${message.text()}`);
        });

        // Set up network request monitoring
        const networkRequests = [];
        page.on('request', (request) => {
            if (request.url().includes('/api/properties/')) {
                const timestamp = new Date().toISOString();
                console.log(`[${timestamp}] REQUEST: ${request.method()} ${request.url()}`);
                
                // Log POST data if present
                if (request.method() === 'POST') {
                    const postData = request.postData();
                    if (postData) {
                        console.log(`[${timestamp}] POST DATA:`, postData);
                        networkRequests.push({
                            timestamp,
                            method: request.method(),
                            url: request.url(),
                            postData: postData
                        });
                    }
                }
            }
        });

        // Set up response monitoring
        page.on('response', async (response) => {
            if (response.url().includes('/api/properties/')) {
                const timestamp = new Date().toISOString();
                console.log(`[${timestamp}] RESPONSE: ${response.status()} ${response.url()}`);
                
                try {
                    const responseData = await response.json();
                    console.log(`[${timestamp}] RESPONSE DATA:`, JSON.stringify(responseData, null, 2));
                } catch (e) {
                    console.log(`[${timestamp}] Could not parse response as JSON`);
                }
            }
        });

        await page.setViewportSize({ width: 1920, height: 1080 });
        
        console.log('Navigating to: http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt');
        
        // Navigate to the target URL
        await page.goto('http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt', {
            waitUntil: 'networkidle',
            timeout: 30000
        });

        console.log('Page loaded, waiting for initial API calls...');
        
        // Wait for the page to fully load and make initial API calls
        await page.waitForTimeout(5000);

        // Take initial screenshot
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        await page.screenshot({
            path: `/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery/screenshot-initial-${timestamp}.png`,
            fullPage: true
        });

        // Wait for comparables table to load
        try {
            await page.waitForSelector('.comparable-property', { timeout: 15000 });
            console.log('Comparables table loaded');
        } catch (e) {
            console.log('Comparables table not found or took too long to load');
        }

        // Capture detailed information about the comparables
        const comparablesInfo = await page.evaluate(() => {
            const comparables = [];
            const rows = document.querySelectorAll('.comparable-property, tr');
            
            rows.forEach((row, index) => {
                const cells = row.querySelectorAll('td, .property-info');
                if (cells.length > 0) {
                    const rowData = {
                        index,
                        text: row.innerText?.trim() || '',
                        html: row.innerHTML
                    };
                    comparables.push(rowData);
                }
            });

            // Also look for any elements containing location/distance information
            const locationElements = document.querySelectorAll('*');
            const locationInfo = [];
            
            locationElements.forEach(el => {
                const text = el.innerText || '';
                if (text.match(/mile|distance|location|city|zip|address/i) && text.length < 200) {
                    locationInfo.push({
                        tagName: el.tagName,
                        className: el.className,
                        text: text.trim()
                    });
                }
            });

            return {
                comparables,
                locationInfo,
                pageTitle: document.title,
                url: window.location.href
            };
        });

        // Take screenshot of comparables table
        await page.screenshot({
            path: `/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery/screenshot-comparables-${timestamp}.png`,
            fullPage: true
        });

        // Scroll to specific sections if they exist
        try {
            const comparablesSection = await page.$('.comparables, [id*="comparable"], [class*="comparable"]');
            if (comparablesSection) {
                await comparablesSection.scrollIntoView();
                await page.waitForTimeout(1000);
                
                await page.screenshot({
                    path: `/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery/screenshot-comparables-focused-${timestamp}.png`
                });
            }
        } catch (e) {
            console.log('Could not find specific comparables section');
        }

        // Wait for any additional API calls that might happen
        await page.waitForTimeout(5000);

        // Save all collected data
        const reportData = {
            timestamp: new Date().toISOString(),
            url: 'http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt',
            consoleMessages,
            networkRequests,
            comparablesInfo,
            testSummary: {
                totalConsoleMessages: consoleMessages.length,
                networkRequestCount: networkRequests.length,
                comparablesFound: comparablesInfo.comparables.length,
                locationElementsFound: comparablesInfo.locationInfo.length
            }
        };

        // Write detailed report
        fs.writeFileSync(
            `/Users/AIRBNB/Cursor_Projects/NewGoogleBigQuery/location-fallback-test-${timestamp}.json`,
            JSON.stringify(reportData, null, 2)
        );

        console.log('\n=== TEST SUMMARY ===');
        console.log(`Console messages captured: ${consoleMessages.length}`);
        console.log(`Network requests captured: ${networkRequests.length}`);
        console.log(`Comparable properties found: ${comparablesInfo.comparables.length}`);
        console.log(`Location elements found: ${comparablesInfo.locationInfo.length}`);
        
        // Analyze the data for location-based fallback verification
        const apiCalls = networkRequests.filter(req => req.url.includes('/api/properties/nearby'));
        console.log(`\nAPI calls to /api/properties/nearby: ${apiCalls.length}`);
        
        apiCalls.forEach((call, index) => {
            console.log(`\nAPI Call ${index + 1}:`);
            console.log(`URL: ${call.url}`);
            if (call.postData) {
                try {
                    const postData = JSON.parse(call.postData);
                    console.log(`POST Data:`, JSON.stringify(postData, null, 2));
                    
                    // Check for location-based parameters
                    if (postData.distance_from || postData.max_distance) {
                        console.log('✅ Location-based fallback parameters detected!');
                        console.log(`Distance from: ${postData.distance_from}`);
                        console.log(`Max distance: ${postData.max_distance}`);
                    } else {
                        console.log('❌ No location-based parameters found in this request');
                    }
                } catch (e) {
                    console.log('Could not parse POST data as JSON');
                }
            }
        });

        return reportData;

    } catch (error) {
        console.error('Error during test:', error);
        throw error;
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the test
testLocationFallback()
    .then((data) => {
        console.log('\n=== TEST COMPLETED SUCCESSFULLY ===');
        console.log('Check the generated screenshots and JSON report for detailed results');
    })
    .catch((error) => {
        console.error('Test failed:', error);
        process.exit(1);
    });