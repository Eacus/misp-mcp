
import sys
from mcp.server import Server
from mcp import types
from pymisp import PyMISP, PyMISPError
from pydantic_settings import BaseSettings, SettingsConfigDict
import asyncio
from mcp.server.stdio import stdio_server


class Settings(BaseSettings):
    MISP_URL: str
    MISP_KEY: str
    MISP_VERIFYCERT: bool

    model_config = SettingsConfigDict(env_file=".env")

env = Settings()

# instance a PyMISP object from the previous parameters
# --- Initialize FastMCP server ---

try:
    misp = PyMISP(
        env.MISP_URL, 
        env.MISP_KEY, 
        env.MISP_VERIFYCERT)
except PyMISPError as e:
    print(f"Error initializing PyMISP: {e}",file=sys.stderr)
    
    exit()

app = Server("MISPerer")
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(name="search_from_date", description="Search all events from a specific date", inputSchema={
            "type": "object", "properties": {
                "date": {"type": "string", "format": "date"}
            }, "required": ["date"]
        }),
        types.Tool(name="search_from_range", description="Search events from a date range", inputSchema={
            "type": "object", "properties": {
                "start": {"type": "string", "format": "date"},
                "end": {"type": "string", "format": "date"}
            }, "required": ["start", "end"]
        }),
        types.Tool(name="search_by_tags", description="Search events by one or more tags", inputSchema={
            "type": "object", "properties": {
                "tags": {"type": "array", "items": {"type": "string"}}
            }, "required": ["tags"]
        }),
        types.Tool(name="search_by_creator", description="Search events by the creator organization", inputSchema={
            "type": "object", "properties": {
                "creator": {"type": "string"}
            }, "required": ["creator"]
        }),
        types.Tool(name="get_event_by_id", description="Get a specific event by ID", inputSchema={
            "type": "object", "properties": {
                "id": {"type": "integer"}
            }, "required": ["id"]
        }),
        types.Tool(name="get_event_by_uuid", description="Get a specific event by UUID", inputSchema={
            "type": "object", "properties": {
                "uuid": {"type": "string"}
            }, "required": ["uuid"]
        }),
        types.Tool(name="list_organisations", description="List all organisations", inputSchema={
            "type": "object", "properties": {}
        }),
        types.Tool(name="search_by_galaxy", description="Search events by galaxy tag", inputSchema={
            "type": "object", "properties": {
                "galaxy": {"type": "string"}
            }, "required": ["galaxy"]
        }),
        types.Tool(name="search_by_taxonomy", description="Search events by taxonomy tag", inputSchema={
            "type": "object", "properties": {
                "taxonomy": {"type": "string"}
            }, "required": ["taxonomy"]
        }),
        types.Tool(name="search_by_attribute", description="Search events by attribute type and value", inputSchema={
            "type": "object", "properties": {
                "type": {"type": "string"},
                "value": {"type": "string"}
            }, "required": ["type", "value"]
        }),
        types.Tool(name="search_by_object", description="Search events with a specific object", inputSchema={
            "type": "object", "properties": {
                "object": {"type": "string"}
            }, "required": ["object"]
        })
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "search_from_date":
        events = misp.search(controller='events', published=True, date_from=arguments["date"], metadata=True)
        return [types.TextContent(type="text", text=str(events))]

    if name == "search_from_range":
        events = misp.search(controller='events', published=True, date_from=arguments["start"], date_to=arguments["end"], metadata=True)
        return [types.TextContent(type="text", text=str(events))]

    if name == "search_by_tags":
        events = misp.search(controller='events', tags=arguments["tags"], metadata=True)
        return [types.TextContent(type="text", text=str(events))]

    if name == "search_by_creator":
        events = misp.search(controller='events', org=arguments["creator"], metadata=True)
        return [types.TextContent(type="text", text=str(events))]

    if name == "get_event_by_id":
        event = misp.get_event(arguments["id"]), 
        return [types.TextContent(type="text", text=str(event))]

    if name == "get_event_by_uuid":
        event = misp.get_event(arguments["uuid"], metadata=True)
        return [types.TextContent(type="text", text=str(event))]

    if name == "list_organisations":
        orgs = misp.get_organisations_list()
        return [types.TextContent(type="text", text=str(orgs))]

    if name == "search_by_galaxy":
        events = misp.search(controller='events', galaxy=arguments["galaxy"] , metadata=True)
        return [types.TextContent(type="text", text=str(events))]

    if name == "search_by_taxonomy":
        events = misp.search(controller='events', tags=[arguments["taxonomy"]], metadata=True)
        return [types.TextContent(type="text", text=str(events))]

    if name == "search_by_attribute":
        attributes = misp.search(controller='attributes', type_attribute=arguments["type"], value=arguments["value"])
        return [types.TextContent(type="text", text=str(attributes))]

    if name == "search_by_object":
        events = misp.search(controller='events', object_name=arguments["object"])
        return [types.TextContent(type="text", text=str(events))]

    raise ValueError(print(f"Tool not found: {name}",file=sys.stderr))


async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())