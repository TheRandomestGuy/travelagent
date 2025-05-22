import time
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from data_fetcher import poi_list, travel_time

@tool
def poi_tool(location_name: str, radius: int):
    """
    Get a list of points of interest in a city around a certain radius. This list contains points of interest of all types.
    
    Args:
        location_name (str): The name of the city.
        radius (int): The radius in meters.
        
    Returns:
        list: A list of dictionaries with the name and coordinates of each POI.
    """
    return poi_list(location_name, radius)

@tool
def travel_time_tool(location_cords1: tuple, location_cords2: tuple):
    """
    Get the travel time between two locations.
    
    Make sure all arguements are in the format of (lat, lon). This requires switching the first and second arguement.
    Double check the validity of the coordinates before passing them to this function.

    Args:
        location_cords1 (tuple): The coordinates of the first location.
        location_cords2 (tuple): The coordinates of the second location.
        
    Returns:
        float: The travel time in seconds.
    """
    return travel_time(location_cords1, location_cords2)

def rate_limited_search(*args, **kwargs):
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            result = DuckDuckGoSearchRun().run(*args, **kwargs)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"DuckDuckGo rate limit or error detected: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"DuckDuckGo search failed after {max_retries} attempts: {e}")
                return "DuckDuckGo search failed due to rate limiting or network error."

search_tool = Tool(
    name="search",
    func=rate_limited_search,
    description="Useful for searching the web with DuckDuckGo.",
)