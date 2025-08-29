const { chromium } = require('playwright-core');

async function captureConsoleLogs() {
    console.log('🔍 Starting console log capture for revenue calculation debugging...');
    
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    const page = await browser.newPage();
    
    // Array to store all console messages
    const consoleLogs = [];
    
    // Capture all console messages
    page.on('console', async (message) => {
        const timestamp = new Date().toISOString();
        const type = message.type();
        const text = message.text();
        
        const logEntry = {
            timestamp,
            type,
            text
        };
        
        consoleLogs.push(logEntry);
        
        // Print to our console with type indicator
        console.log(`[${timestamp}] [${type.toUpperCase()}] ${text}`);
    });
    
    // Capture page errors
    page.on('pageerror', (error) => {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [PAGE ERROR] ${error.message}`);
        consoleLogs.push({
            timestamp,
            type: 'pageerror',
            text: error.message
        });
    });
    
    // Set viewport for proper rendering
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    console.log('📍 Navigating to http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt...');
    
    try {
        // Navigate to the page with extended timeout
        await page.goto('http://127.0.0.1:5004/copyJIC?taskId=868fd6tdt', {
            waitUntil: 'networkidle',
            timeout: 60000
        });
        
        console.log('✅ Page loaded successfully');
        
        // Wait a bit more to ensure all JavaScript execution completes
        console.log('⏱️  Waiting for JavaScript execution to complete...');
        await page.waitForTimeout(10000);
        
        // Try to detect if the revenue calculations have completed by looking for specific elements
        console.log('🔍 Checking if revenue calculations are visible on page...');
        
        // Wait for any revenue-related content to appear
        try {
            await page.waitForSelector('[data-test="revenue"], .revenue, #revenue', { timeout: 5000 });
            console.log('✅ Revenue elements detected on page');
        } catch (e) {
            console.log('⚠️  No specific revenue elements found, but continuing...');
        }
        
        // Additional wait to catch any delayed console output
        await page.waitForTimeout(5000);
        
    } catch (error) {
        console.error('❌ Error loading page:', error.message);
    }
    
    await browser.close();
    
    console.log('\n📊 CONSOLE LOG SUMMARY:');
    console.log('='.repeat(80));
    
    // Filter and organize the logs
    const revenueRelatedLogs = consoleLogs.filter(log => 
        log.text.toLowerCase().includes('revenue') ||
        log.text.toLowerCase().includes('projection') ||
        log.text.toLowerCase().includes('comparable') ||
        log.text.toLowerCase().includes('loading') ||
        log.text.toLowerCase().includes('calculated') ||
        log.text.toLowerCase().includes('top 20') ||
        log.text.includes('🏆') ||
        log.text.includes('✅') ||
        log.text.includes('$')
    );
    
    const errors = consoleLogs.filter(log => 
        log.type === 'error' || log.type === 'pageerror'
    );
    
    console.log(`\n🎯 REVENUE-RELATED LOGS (${revenueRelatedLogs.length} found):`);
    console.log('-'.repeat(50));
    revenueRelatedLogs.forEach(log => {
        console.log(`[${log.timestamp}] [${log.type.toUpperCase()}] ${log.text}`);
    });
    
    console.log(`\n❌ ERRORS (${errors.length} found):`);
    console.log('-'.repeat(50));
    errors.forEach(log => {
        console.log(`[${log.timestamp}] [${log.type.toUpperCase()}] ${log.text}`);
    });
    
    console.log(`\n📋 ALL CONSOLE LOGS (${consoleLogs.length} total):`);
    console.log('-'.repeat(50));
    consoleLogs.forEach(log => {
        console.log(`[${log.timestamp}] [${log.type.toUpperCase()}] ${log.text}`);
    });
    
    return { consoleLogs, revenueRelatedLogs, errors };
}

// Run the capture
captureConsoleLogs()
    .then((results) => {
        console.log('\n🎉 Console log capture completed successfully!');
        console.log(`📊 Total logs: ${results.consoleLogs.length}`);
        console.log(`🎯 Revenue-related: ${results.revenueRelatedLogs.length}`);
        console.log(`❌ Errors: ${results.errors.length}`);
        process.exit(0);
    })
    .catch((error) => {
        console.error('💥 Failed to capture console logs:', error);
        process.exit(1);
    });