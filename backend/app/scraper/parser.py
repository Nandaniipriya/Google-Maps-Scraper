from bs4 import BeautifulSoup
from scraper.base import Base
from scraper.common import Common
import requests
import re

class Parser(Base):
    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
            "location": "Copy address",
            "phone": "Copy phone number",
            "website": "Open website",
            "booking": "Open booking link",
        }

    def parse(self):
        try:
            infoSheet = self.driver.execute_script(
                """return document.querySelector("[role='main']")"""
            )
            
            if not infoSheet:
                print("Info sheet not found, skipping...")
                return
                
            html = infoSheet.get_attribute("outerHTML")
            if not html:
                print("No HTML content found, skipping...")
                return
                
            soup = BeautifulSoup(html, "html.parser")

            # Initialize data dictionary with default values
            data = {
                "Category": None,
                "Name": None,
                "Phone": None,
                "Google Maps URL": None,
                "Website": None,
                "email": None,
                "Business Status": None,
                "Address": None,
                "Total Reviews": None,
                "Booking Links": None,
                "Rating": None,
                "Hours": None
            }

            # Extract data points with better error handling
            try:
                name_elem = soup.select_one(".tAiQdd h1.DUwDvf")
                if name_elem:
                    data["Name"] = name_elem.text.strip()
            except Exception as e:
                print(f"Error extracting name: {e}")

            try:
                data["Rating"] = soup.find("span", class_="ceNzKf").get("aria-label").replace("stars", "").strip()
            except: pass

            try:
                reviews = list(soup.find("div", class_="F7nice").children)
                data["Total Reviews"] = reviews[1].get_text(strip=True)
            except: pass

            # Extract address, phone from info bars
            for infoBar in soup.find_all("button", class_="CsEnBe"):
                tooltip = infoBar.get("data-tooltip")
                text = infoBar.find("div", class_="rogA2c").text.strip()
                
                if tooltip == self.comparing_tool_tips["location"]:
                    data["Address"] = text
                elif tooltip == self.comparing_tool_tips["phone"]:
                    data["Phone"] = text

            # Extract website and email
            try:
                website_tag = soup.find("a", {"aria-label": lambda x: x and "Website:" in x})
                if website_tag:
                    data["Website"] = website_tag.get("href")
                    data["email"] = self.find_mail(data["Website"])
            except: pass

            # Extract remaining fields
            try:
                data["Hours"] = soup.find("div", class_="t39EBf").get_text(strip=True)
            except: pass

            try:
                data["Category"] = soup.find("button", class_="DkEaL").text.strip()
            except: pass

            try:
                data["Google Maps URL"] = self.driver.current_url
            except: pass

            try:
                data["Business Status"] = soup.find("span", class_="ZDu9vd").findChildren("span", recursive=False)[0].get_text(strip=True)
            except: pass

            self.finalData.append(data)

        except Exception as e:
            print(f"Error parsing location: {str(e)}")

    def find_mail(self, url):
        if not url:
            return None
            
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            text = response.text
            
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
            
            if not emails:
                # Try contact page
                contact_urls = [f"{url.rstrip('/')}/contact", f"{url.rstrip('/')}/contact-us"]
                for contact_url in contact_urls:
                    try:
                        response = requests.get(contact_url, headers=headers, timeout=10)
                        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", response.text)
                        if emails:
                            break
                    except:
                        continue

            # Validate and clean emails
            valid_emails = [
                email for email in set(emails)
                if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
            ]
            
            return ", ".join(valid_emails) if valid_emails else None

        except Exception as e:
            print(f"Error finding email: {str(e)}")
            return None

    def main(self, allResultsLinks):
        try:
            for resultLink in allResultsLinks:
                if Common.close_thread_is_set():
                    return
                self.openingurl(url=resultLink)
                self.parse()
        except Exception as e:
            print(f"Error processing results: {str(e)}")
