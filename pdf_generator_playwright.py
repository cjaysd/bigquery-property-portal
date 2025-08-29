"""
Playwright-based PDF Generation System with Browser Pooling
Provides pixel-perfect PDF rendering for OODA branded reports
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, Page, Playwright
import logging

logger = logging.getLogger(__name__)

class BrowserPool:
    """
    Manages a pool of browser instances for efficient PDF generation.
    Eliminates the 3.2 second startup overhead per PDF.
    """
    
    def __init__(self, pool_size: int = 3):
        self.pool_size = pool_size
        self.browsers: list[Browser] = []
        self.playwright: Optional[Playwright] = None
        self.lock = asyncio.Lock()
        self.initialized = False
        
    async def initialize(self):
        """Initialize the browser pool"""
        if not self.initialized:
            self.playwright = await async_playwright().start()
            self.initialized = True
            logger.info(f"Browser pool initialized with size {self.pool_size}")
    
    @asynccontextmanager
    async def get_browser(self):
        """Get a browser from the pool or create a new one"""
        await self.initialize()
        
        browser = None
        async with self.lock:
            if self.browsers:
                browser = self.browsers.pop()
                logger.debug("Reusing browser from pool")
            else:
                logger.debug("Creating new browser instance")
                browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--memory-pressure-off',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-gpu',
                        '--disable-software-rasterizer'
                    ]
                )
        
        try:
            yield browser
        finally:
            # Return browser to pool or close if pool is full
            async with self.lock:
                if len(self.browsers) < self.pool_size:
                    # Clean up pages to prevent memory leaks
                    for context in browser.contexts:
                        for page in context.pages:
                            await page.close()
                    self.browsers.append(browser)
                    logger.debug("Returned browser to pool")
                else:
                    await browser.close()
                    logger.debug("Closed excess browser")
    
    async def cleanup(self):
        """Clean up all browser instances"""
        async with self.lock:
            for browser in self.browsers:
                await browser.close()
            self.browsers.clear()
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                self.initialized = False
        logger.info("Browser pool cleaned up")

# Global browser pool instance
browser_pool = BrowserPool(pool_size=3)

class PlaywrightPDFGenerator:
    """
    Generates pixel-perfect PDFs using Playwright and Chromium
    Preserves OODA branding, dark themes, and Chart.js visualizations
    """
    
    # OODA Dark theme preservation CSS
    DARK_THEME_CSS = """
        @media print {
            * { 
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
            }
            body {
                background-color: #1a1a19 !important;
                color: #e2e2e0 !important;
            }
            .glassmorphism {
                /* Fallback for glassmorphism in PDF */
                backdrop-filter: none !important;
                background: rgba(255, 255, 255, 0.15) !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
            }
            .card {
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }
            .section {
                page-break-after: auto !important;
                break-after: auto !important;
            }
        }
    """
    
    @staticmethod
    async def wait_for_charts(page: Page, timeout: int = 30000):
        """
        Wait for Chart.js charts to fully render
        Disables animations for clean capture
        """
        try:
            # Wait for canvas elements to exist
            await page.wait_for_selector('canvas', timeout=timeout)
            
            # Wait for Chart.js to be loaded and charts to be ready
            await page.wait_for_function("""
                () => {
                    if (typeof Chart === 'undefined') return true; // No charts
                    
                    const charts = document.querySelectorAll('canvas');
                    if (charts.length === 0) return true;
                    
                    // Check if all canvases have been initialized
                    return Array.from(charts).every(canvas => {
                        const ctx = canvas.getContext('2d');
                        return ctx && canvas.width > 0 && canvas.height > 0;
                    });
                }
            """, timeout=timeout)
            
            # Disable animations for clean PDF capture
            await page.evaluate("""
                () => {
                    if (typeof Chart !== 'undefined') {
                        // Set global defaults
                        Chart.defaults.animation.duration = 0;
                        Chart.defaults.animations.active = false;
                        
                        // Update all existing chart instances
                        Object.values(Chart.instances || {}).forEach(chart => {
                            if (chart.options.animation) {
                                chart.options.animation = false;
                            }
                            if (chart.options.animations) {
                                chart.options.animations = false;
                            }
                            chart.update('none'); // Update without animation
                        });
                    }
                }
            """)
            
            # Give charts a moment to settle after disabling animations
            await asyncio.sleep(0.5)
            
            logger.debug("Charts ready for PDF capture")
            
        except Exception as e:
            logger.warning(f"Chart wait timeout or error: {e}")
            # Continue anyway - page might not have charts
    
    @staticmethod
    async def inject_dark_theme(page: Page):
        """Inject OODA dark theme preservation CSS"""
        await page.add_style_tag(content=PlaywrightPDFGenerator.DARK_THEME_CSS)
        logger.debug("Dark theme CSS injected")
    
    @staticmethod
    async def generate_pdf(
        html_content: str,
        options: Optional[Dict[str, Any]] = None,
        wait_for_charts: bool = True,
        inject_dark_theme: bool = True
    ) -> bytes:
        """
        Generate a PDF from HTML content with OODA branding preserved
        
        Args:
            html_content: HTML string to render
            options: PDF generation options
            wait_for_charts: Whether to wait for Chart.js completion
            inject_dark_theme: Whether to inject dark theme CSS
            
        Returns:
            PDF bytes
        """
        start_time = time.time()
        
        # Default PDF options for OODA branding
        default_options = {
            'format': 'A4',
            'print_background': True,
            'margin': {
                'top': '20mm',
                'bottom': '20mm',
                'left': '15mm',
                'right': '15mm'
            },
            'prefer_css_page_size': True,
            'display_header_footer': False
        }
        
        if options:
            default_options.update(options)
        
        async with browser_pool.get_browser() as browser:
            # Create a new page with proper viewport
            page = await browser.new_page()
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            
            try:
                # Set content
                await page.set_content(html_content, wait_until='networkidle')
                
                # Inject dark theme CSS if requested
                if inject_dark_theme:
                    await PlaywrightPDFGenerator.inject_dark_theme(page)
                
                # Wait for charts if requested
                if wait_for_charts:
                    await PlaywrightPDFGenerator.wait_for_charts(page)
                
                # Wait a moment for any final rendering
                await asyncio.sleep(0.5)
                
                # Generate PDF
                pdf_bytes = await page.pdf(**default_options)
                
                generation_time = time.time() - start_time
                logger.info(f"PDF generated in {generation_time:.2f} seconds")
                
                return pdf_bytes
                
            finally:
                await page.close()
    
    @staticmethod
    async def generate_pdf_from_url(
        url: str,
        options: Optional[Dict[str, Any]] = None,
        wait_for_charts: bool = True,
        inject_dark_theme: bool = True
    ) -> bytes:
        """
        Generate a PDF from a URL
        
        Args:
            url: URL to render
            options: PDF generation options
            wait_for_charts: Whether to wait for Chart.js completion
            inject_dark_theme: Whether to inject dark theme CSS
            
        Returns:
            PDF bytes
        """
        start_time = time.time()
        
        # Default PDF options
        default_options = {
            'format': 'A4',
            'print_background': True,
            'margin': {
                'top': '20mm',
                'bottom': '20mm',
                'left': '15mm',
                'right': '15mm'
            },
            'prefer_css_page_size': True,
            'display_header_footer': False
        }
        
        if options:
            default_options.update(options)
        
        async with browser_pool.get_browser() as browser:
            page = await browser.new_page()
            await page.set_viewport_size({'width': 1920, 'height': 1080})
            
            try:
                # Navigate to URL
                await page.goto(url, wait_until='networkidle')
                
                # Inject dark theme CSS if requested
                if inject_dark_theme:
                    await PlaywrightPDFGenerator.inject_dark_theme(page)
                
                # Wait for charts if requested
                if wait_for_charts:
                    await PlaywrightPDFGenerator.wait_for_charts(page)
                
                # Wait a moment for any final rendering
                await asyncio.sleep(0.5)
                
                # Generate PDF
                pdf_bytes = await page.pdf(**default_options)
                
                generation_time = time.time() - start_time
                logger.info(f"PDF generated from URL in {generation_time:.2f} seconds")
                
                return pdf_bytes
                
            finally:
                await page.close()

# Performance configuration for optimal PDF generation
PERFORMANCE_CONFIG = {
    'browser_pool_size': 3,
    'max_concurrent_pdfs': os.cpu_count() - 1 if os.cpu_count() else 1,
    'page_timeout': 30000,
    'network_idle_time': 500,
}

async def cleanup():
    """Cleanup function to be called on application shutdown"""
    await browser_pool.cleanup()

# Example usage for testing
async def test_pdf_generation():
    """Test PDF generation with sample HTML"""
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background: #1a1a19;
                color: #e2e2e0;
                font-family: 'Inter', -apple-system, sans-serif;
                padding: 40px;
            }
            .card {
                background: linear-gradient(135deg, #0e0e0d 0%, #1a1a19 100%);
                border: 1px solid rgba(38, 208, 134, 0.3);
                border-radius: 12px;
                padding: 24px;
                margin: 20px 0;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }
            h1 {
                color: #26D086;
                font-size: 32px;
                margin: 0 0 20px 0;
            }
            .metric {
                font-size: 48px;
                font-weight: 600;
                color: #26D086;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>OODA Premium Analysis Report</h1>
            <div class="metric">$127,500</div>
            <p>Annual Revenue Projection</p>
        </div>
    </body>
    </html>
    """
    
    pdf_bytes = await PlaywrightPDFGenerator.generate_pdf(sample_html)
    
    # Save test PDF
    with open('test_ooda_report.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"Test PDF generated: {len(pdf_bytes)} bytes")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_pdf_generation())
    asyncio.run(cleanup())