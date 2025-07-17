import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp import ClientSession
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import AsyncOpenAI

from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Load environment variables
load_dotenv("../.env")

# Global variables to store session state
session = None
exit_stack = AsyncExitStack()
openai_client = AsyncOpenAI()
model = "gpt-4o"
write = None


async def connect_to_server(server_script_path: str = "server.py"):
    """Connect to an MCP server.

    Args:
        server_script_path: Path to the server script.
    """
    global session, write, exit_stack

    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        get_session_id,
    ):

        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

    # List available tools
    tools_result = await session.list_tools()
    print("\nConnected to server with tools:")
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")


async def get_mcp_tools() -> List[Dict[str, Any]]:
    """Get available tools from the MCP server in OpenAI format.

    Returns:
        A list of tools in OpenAI format.
    """
    global session

    tools_result = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools_result.tools
    ]


async def process_query(query: str) -> str:
    """Process a query using OpenAI and available MCP tools.

    Args:
        query: The user query.

    Returns:
        The response from OpenAI.
    """
    global session, openai_client, model

    # Get available tools
    tools = await get_mcp_tools()

    # Initial OpenAI API call
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="auto",
    )

    # Get assistant's response
    assistant_message = response.choices[0].message

    # Initialize conversation with user query and assistant response
    messages = [
        {"role": "user", "content": query},
        assistant_message,
    ]

    # Handle tool calls if present
    if assistant_message.tool_calls:
        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            # Execute tool call
            result = await session.call_tool(
                tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )

            # Add tool response to conversation
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content[0].text,
                }
            )

        # Get final response from OpenAI with tool results
        final_response = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="none",  # Don't allow more tool calls
        )

        return final_response.choices[0].message.content

    # No tool calls, just return the direct response
    return assistant_message.content


async def cleanup():
    """Clean up resources."""
    global exit_stack
    await exit_stack.aclose()


async def main():
    """Main entry point for the client."""
    await connect_to_server("server.py")

    # Example: Ask about company vacation policy
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
            Once you have an itenerary, use the travel_time_tool to estimate the time between each activity.
            Then, provide the final itenerary with the estimated time and cost.
            Add the itenerary to the user's Google Calendar using the add_events_to_google_calendar_tool.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    
    tools = await get_mcp_tools()
    
    agent = create_tool_calling_agent(
        llm = llm,
        prompt = prompt,
        tools = tools
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, return_intermediate_steps=False)
    location = input("Where are you traveling? ")
    interests = input("What are some interests you want to find here? ")

    specific_places = input("Do you have any specific places in mind? (yes/no) ")
    places = "None"
    if specific_places.lower() == 'yes':
        places = input("Please list the places you have in mind, separated by commas: ")
    else:
        print("No specific places provided, using general interests.")
    
    restraunts = input("What type of restaurants are you interested in? ")
    hotels = input("What type of hotels are you interested in? ")

    budget = input("What is your budget for this trip? ")
    time = input("How many days do you have for this trip? ")
    date = input("What is the start date of your trip? (YYYY-MM-DD) ")
    query = f"Generate an itenerary for a trip to {location} with interests in {interests} and a budget of {budget} and {time} days, starting on {date}."     # TODO: Ask for specific places of interest, types of restaurants, and hotels
    raw_response = agent_executor.invoke({"query": query})
    structured_response = parser.parse(raw_response.get("output"))

    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())