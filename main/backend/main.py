from tools import search_tool, poi_tool, travel_time_tool, add_events_to_google_calendar_tool, tavily_search_tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from fastapi import FastAPI, Request
from dotenv import load_dotenv

app = FastAPI()

@app.post("/generate_itinerary")
def generate_itinerary():
    request_data = Request.json()
    location = request_data.get("location")
    interests = request_data.get("interests")
    specific_places = request_data.get("specific_places", "None")
    places = request_data.get("places", "None")
    restaurants = request_data.get("restaurants", "None")
    hotels = request_data.get("hotels", "None")
    budget = request_data.get("budget")
    time = request_data.get("time")
    date = request_data.get("date")

    load_dotenv()

    class Response(BaseModel):
        itenerary: str
        time_estimates: list[dict]
        budget_breakdown: dict
        hotels: list[str]
        restaurants: list[str]
        tools_used: list[str]

    llm = ChatOpenAI(model='gpt-4o')
    parser = PydanticOutputParser(pydantic_object=Response)

    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a travel assistant that will help generate an itenerary.
            Answer the user query and use neccessary tools.
            Make sure to minimize the amount of times search_tool is used, preferably less than 4 per query.
            Wait between uses of the search_tool to avoid rate limits.
            Whenever using the search_tool, make sure to also ask for the coordinates of the locations.
            Dont put the coordinates in the final output, rather use them to calculate the travel time between locations.
            Make sure the intenerary follows the interests and budger of the user.
            Please break down the budget and time estimates (Start and End) for each activity (make sure to include in final output).
            After generating the itinerary, you MUST call the add_events_to_google_calendar_tool with the final list of events. Do not output the final answer until you have called this tool.
            Then, provide the itenerary with the estimated time and cost.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    
    tools = [tavily_search_tool, poi_tool, add_events_to_google_calendar_tool]
    agent = create_tool_calling_agent(
        llm = llm,
        prompt = prompt,
        tools = tools
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, return_intermediate_steps=False) 

    query = f"Generate an itinerary for a trip to {location} with interests in {interests} and a budget of {budget} and {time} days, starting on {date}."

    raw_response = agent_executor.invoke({"query": query})
    structured_response = parser.parse(raw_response.get("output"))
    return structured_response