from tools import search_tool, poi_tool, travel_time_tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv


if __name__ == "__main__":

    load_dotenv()

    class Response(BaseModel):
        itenerary: str
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
            Please break down the budget and time estimates (Start and End) for each activity.
            Once you have an itenerary, use the travel_time_tool to estimate the time between each activity.
            Then, provide the final itenerary with the estimated time and cost.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    
    tools = [search_tool, poi_tool, travel_time_tool]
    agent = create_tool_calling_agent(
        llm = llm,
        prompt = prompt,
        tools = tools
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools)
    location = input("Where are you traveling? ")
    interests = input("What are some interests you want to find here? ")
    budget = input("What is your budget for this trip? ")
    time = input("How many days do you have for this trip? ")
    query = f"Generate an itenerary for a trip to {location} with interests in {interests} and a budget of {budget} and {time} days."
    raw_response = agent_executor.invoke({"query": query})
    structured_response = parser.parse(raw_response.get("output"))
    print(structured_response)