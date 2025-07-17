import time
from mcp.server.fastmcp import FastMCP
from langchain_community.tools import DuckDuckGoSearchRun
from data_fetcher import poi_list, travel_time
from google_calendar_helper import add_events_to_google_calendar

mcp = FastMCP("TravelAgentServer", stateless_http=True, host="0.0.0.0", port=8000)

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
def rate_limited_search(*args, **kwargs):
    '''
    Perform a rate-limited search using DuckDuckGo.
    Retries up to 3 times with exponential backoff in case of rate limiting or network issues.
    
    Args:
        *args: Positional arguments for the search function.
        **kwargs: Keyword arguments for the search function.
    Returns:
        str: Search results or error message.
    '''
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

@mcp.tool()
def add_events_to_google_calendar_tool(events: list):
    """
    Add a list of events to the user's Google Calendar.

    Args:
        events (list): A list of dictionaries, each containing event details such as:
            - summary (str): Title of the event
            - description (str): Description of the event
            - location (str): Location of the event
            - start (str): ISO format start datetime (e.g., '2024-06-01T09:00:00')
            - end (str): ISO format end datetime (e.g., '2024-06-01T10:00:00')
    Returns:
        str: Success message or error.
    """
    return add_events_to_google_calendar(events)

if __name__ == "__main__":
        # mcp.run(transport="stdio")
        mcp.run(transport="streamable-http")