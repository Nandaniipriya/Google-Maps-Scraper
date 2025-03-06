from fastapi import FastAPI, HTTPException
from selenium import webdriver
from scraper.scraper import Backend
from scraper.common import Common
from config.setting import ScraperResponse, SearchQuery, Location

app = FastAPI(title="Google Maps Scraper API")

@app.get("/")
async def root():
    return {"message": "Welcome to Google Maps Scraper API"}

@app.post("/scrape", response_model=ScraperResponse)
async def scrape_google_maps(search: SearchQuery):
    scraper = None
    try:
        # Initialize scraper in headless mode
        scraper = Backend(
            searchquery=search.query,
            outputformat="json",
            healdessmode=1
        )
        
        # Run the scraping (remove await since mainscraping is not async)
        scraper.mainscraping()
        
        # Get results from parser with error handling
        if not scraper.scroller or not scraper.scroller.parser:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize parser"
            )
            
        results = scraper.scroller.parser.finalData
        if not results:
            return ScraperResponse(total_results=0, locations=[])
        
        # Format response
        locations = [
            Location(
                category=item.get("Category"),
                name=item.get("Name"),
                phone=item.get("Phone"),
                google_maps_url=item.get("Google Maps URL"),
                website=item.get("Website"),
                email=item.get("email"),
                business_status=item.get("Business Status"),
                address=item.get("Address"),
                total_reviews=item.get("Total Reviews"),
                booking_links=item.get("Booking Links"),
                rating=item.get("Rating"),
                hours=item.get("Hours")
            )
            for item in results
        ]
        
        return ScraperResponse(
            total_results=len(locations),
            locations=locations
        )
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )
        
    finally:
        # Ensure cleanup happens
        if scraper:
            try:
                Common.set_close_thread()
                if hasattr(scraper, 'driver'):
                    scraper.driver.quit()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="error",
        workers=1  # Single worker to avoid resource conflicts
    )


