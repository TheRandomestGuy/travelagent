import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp import ClientSession
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import AsyncOpenAI

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
    query = "What is our company's vacation policy?"
    print(f"\nQuery: {query}")

    response = await process_query(query)
    print(f"\nResponse: {response}")

    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())