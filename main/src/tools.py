from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from data_fetcher import poi_list

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

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Useful for searching the web with DuckDuckGo.",
)