from time import sleep
from scraper.base import Base
from scraper.scroller import Scroller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile


class Backend(Base):
    def __init__(self, searchquery: str, outputformat: str, healdessmode: int):
        """Initialize the scraper backend
        Args:
            searchquery (str): Search query for Google Maps
            outputformat (str): Format of output (json)
            healdessmode (int): Whether to run in headless mode (1=headless, 0=visible)
        """
        self.searchquery = searchquery
        self.headlessMode = healdessmode
        self.init_driver()
        self.scroller = Scroller(driver=self.driver)

    def init_driver(self) -> None:
        """Initialize the Chrome WebDriver with appropriate options"""
        options = webdriver.ChromeOptions()
        
        # Headless mode with proper hardware acceleration disabled
        if self.headlessMode == 1:
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
        
        # Essential options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Disable problematic features
        options.add_argument('--disable-webgl')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        
        # Error handling and logging
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        # Performance settings
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # *** THIS LINE IS REQUIRED FOR RENDER ***
        options.binary_location = "/usr/bin/chromium"

        # Set driver service
        service = Service(ChromeDriverManager().install())

        # Initialize the driver
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def scrape(self) -> None:
        """Perform the scraping operation"""
        # Your scraping logic here
        pass