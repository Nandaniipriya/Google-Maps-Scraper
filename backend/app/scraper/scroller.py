import time
from scraper.common import Common
from bs4 import BeautifulSoup
from selenium.common.exceptions import JavascriptException
from scraper.parser import Parser

class Scroller:
    def __init__(self, driver) -> None:
        self.driver = driver
        self.parser = None
        self.__allResultsLinks = []

    def start_parsing(self):
        self.parser = Parser(self.driver)
        if self.__allResultsLinks:
            self.parser.main(self.__allResultsLinks)
        else:
            print("No results links found to parse")
    
    def scroll(self):
        scrollable_element = self.driver.execute_script(
            """return document.querySelector("[role='feed']")"""
        )
        
        if not scrollable_element:
            print("No results found")
            self.__allResultsLinks = []  # Ensure empty list
            return
            
        print("Starting scroll")
        last_height = 0

        while True:
            if Common.close_thread_is_set():
                return
                
            # Scroll to bottom
            scrollable_element = self.driver.execute_script(
                """return document.querySelector("[role='feed']")"""
            )
            self.driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                scrollable_element
            )
            time.sleep(2)

            # Calculate new scroll height
            new_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", 
                scrollable_element
            )

            # Check if we've reached the end
            if new_height == last_height:
                end_element = self.driver.execute_script(
                    "return document.querySelector('.PbZDve')"
                )
                
                if end_element:
                    break
                    
                try:
                    # Try loading more results
                    self.driver.execute_script(
                        "array=document.getElementsByClassName('hfpxzc');"
                        "array[array.length-1].click();"
                    )
                except JavascriptException:
                    pass
            else:
                last_height = new_height
                
                # Extract links
                soup = BeautifulSoup(scrollable_element.get_attribute('outerHTML'), 'html.parser')
                result_links = [
                    a.get('href') for a in soup.find_all('a', class_='hfpxzc')
                ]
                self.__allResultsLinks = result_links
                print(f"Total locations found: {len(self.__allResultsLinks)}")

        self.start_parsing()


