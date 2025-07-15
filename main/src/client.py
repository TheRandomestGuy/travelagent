import asyncio
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv("../.env")

async def main():
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
            
if __name__ == "__main__":
    asyncio.run(main())