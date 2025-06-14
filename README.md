# Travel AI Agent
## Overview
This AI Agent is given information about the user's preferences and nessecities, uses various tools to plan a vacation, and then adds the itenerary to a google calendar. This agent speeds up travel planning by providing the user with a full itenerary, while minimizing the chances of hallucinations or misinformation through the use of many information gathering tools. 

## AI Agent
This AI Agent is built using Langchain and the OpenAI gpt-4o Model. 

## Tools
### POI List Tool
This tool uses OpenTripMap's API to find the coordinates of the travel destination and then returns a list of all points of interest within a radius. This information is used by the agent to know what potential locations to add to the itenerary.
### Travel Time Tool
This tool uses OpenRouteService's API to find the projected travel time between a start coordinate and a destination coordinate. This tool is used by the agent to make the times in the itenerary realistically account for commuting between locations.
### Search Tool
This tool uses DuckDuckGo's API to allow the AI Agent to search the web. This tool can be used by the agent in a variety of ways to create the perfect travel plan. This tool has a delay if it fails due to rate limits, as that was a problem which was constantly being run into.
### Calenedar Tool
This tool uses Google API to add all events from the itenerary to the user's Google Calendar. In order for this to be used, the user must give the AI Agent permission through an OAuth Client.
