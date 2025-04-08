
import sys
from mcp.server import Server
from mcp import types
from pymisp import PyMISP, PyMISPError, MISPEvent, MISPAttribute, MISPObject
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
        }),
        types.Tool(name="search_logs", description="Get all logs", inputSchema={
            "type": "object", "properties": {}
        }),
        types.Tool(name="search_attribute", description="Search attribute by value", inputSchema={
            "type": "object", "properties": {
                "value": {"type": "string"}
            }, "required": ["value"]
        }),
        types.Tool(
            name="complex_query",
            description="Search MISP using complex OR query values",
            inputSchema={"type": "object", "properties": {"values": {"type": "array", "items": {"type": "string"}}}, "required": ["values"]},
        ),
        types.Tool(
            name="search_updated_events",
            description="Search for recently updated MISP events",
            inputSchema={"type": "object", "properties": {"timestamp": {"type": "string"}}, "required": ["timestamp"]},
        ),
        types.Tool(
            name="create_event",
            description="Create a new MISP event",
            inputSchema={
                "type": "object",
                "properties": {
                    "info": {"type": "string"},
                    "distribution": {"type": "integer"},
                    "threat_level_id": {"type": "integer"},
                    "analysis": {"type": "integer"},
                    "tag": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["info"]
            }
        ),
        types.Tool(
            name="add_attribute",
            description="Add an attribute to an existing MISP event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                    "disable_correlation": {"type": "boolean"}
                },
                "required": ["event_id", "type", "value"]
            }
        ),
        types.Tool(
            name="create_object",
            description="Create a domain-ip MISP object",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "domain": {"type": "string"},
                    "ip": {"type": "string"},
                    "first_seen": {"type": "string"},
                    "last_seen": {"type": "string"}
                },
                "required": ["event_id", "domain", "ip"]
            }
        ),
        types.Tool(
            name="publish_event",
            description="Publish a MISP event",
            inputSchema={"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]}
        ),
        types.Tool(
            name="delete_attribute",
            description="Soft delete an attribute from an event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "attribute_id": {"type": "string"}
                },
                "required": ["event_id", "attribute_id"]
            }
        ),
        types.Tool(
            name="delete_object",
            description="Delete an object from an event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "object_uuid": {"type": "string"}
                },
                "required": ["event_id", "object_uuid"]
            }
        ),
        types.Tool(
            name="delete_event",
            description="Delete an entire MISP event",
            inputSchema={"type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"]}
        ),
        types.Tool(
            name="delete_tag",
            description="Delete a tag from MISP",
            inputSchema={"type": "object", "properties": {"tag": {"type": "string"}}, "required": ["tag"]}
        ), # Administrative
                types.Tool(
            name="add_user",
            description="Add a new user to MISP",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "org_id": {"type": "string"},
                    "role_id": {"type": "string"}
                },
                "required": ["email", "org_id", "role_id"]
            }
        ),
        types.Tool(
            name="list_users",
            description="List all users in MISP",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="delete_user",
            description="Delete a MISP user by ID",
            inputSchema={
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="edit_user",
            description="Edit a MISP user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "email": {"type": "string"}
                },
                "required": ["user_id", "email"]
            }
        ),


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
    
    if name == "search_logs":
        logs = misp.get_logs()
        return [types.TextContent(type="text", text=str(logs))]
    
    if name == "search_attribute":
        attributes = misp.search(controller='attributes', value=arguments["value"])
        return [types.TextContent(type="text", text=str(attributes))]
    if name == "complex_query":
        query = misp.build_complex_query(or_parameters=arguments["values"])
        result = misp.search(value=query, pythonify=False)
        return [types.TextContent(type="text", text=str(result))]

    elif name == "search_updated_events":
        result = misp.search(timestamp=arguments["timestamp"], metadata=True)
        return [types.TextContent(type="text", text=str(result))]

    if name == "create_event":
        event = MISPEvent()
        event.info = arguments["info"]
        event.distribution = arguments.get("distribution", 0)
        event.threat_level_id = arguments.get("threat_level_id", 2)
        event.analysis = arguments.get("analysis", 0)
        tag = arguments.get("tag")
        if tag:
            event.add_tag(tag)
        input_date = arguments.get("date")
        if input_date:
            event.set_date(input_date)
        else:
            event.set_date(datetime.now())
        return [types.TextContent(type="text", text=event.to_json())]

    if name == "add_attribute":
        event = misp.get_event(arguments["event_id"])['Event']
        me = MISPEvent()
        me.load(event)
        attr = me.add_attribute(
            arguments["type"],
            arguments["value"],
            disable_correlation=arguments.get("disable_correlation", False)
        )
        return [types.TextContent(type="text", text=attr.to_json())]

    if name == "create_object":
        event = misp.get_event(arguments["event_id"])['Event']
        me = MISPEvent()
        me.load(event)
        misp_object = MISPObject('domain-ip')
        misp_object.comment = 'Auto-generated domain-ip object'
        misp_object.add_attribute('domain', value=arguments['domain'])
        misp_object.add_attribute('ip', value=arguments['ip'])
        if 'first_seen' in arguments:
            misp_object.add_attribute('first-seen', value=arguments['first_seen'])
        if 'last_seen' in arguments:
            misp_object.add_attribute('last-seen', value=arguments['last_seen'])
        me.add_object(misp_object)
        return [types.TextContent(type="text", text=me.to_json())]

    if name == "publish_event":
        event = misp.get_event(arguments["event_id"])['Event']
        me = MISPEvent()
        me.load(event)
        me.publish()
        return [types.TextContent(type="text", text=f"Event {arguments['event_id']} published: {me.published}")]
    
    if name == "delete_attribute":
        event = misp.get_event(arguments["event_id"])['Event']
        me = MISPEvent()
        me.load(event)
        attr_to_delete = None
        for attr in me.attributes:
            if str(attr.id) == arguments["attribute_id"]:
                attr_to_delete = attr
                break
        if attr_to_delete is None:
            return [types.TextContent(type="text", text=f"Attribute ID {arguments['attribute_id']} not found in event {arguments['event_id']}")]
        attr_to_delete.delete()
        return [types.TextContent(type="text", text=f"Soft-deleted attribute {arguments['attribute_id']} from event {arguments['event_id']}")]

    if name == "delete_object":
        result = misp.delete_object(arguments["object_uuid"])
        return [types.TextContent(type="text", text=f"Deleted object with UUID {arguments['object_uuid']}:", )]

    if name == "delete_event":
        result = misp.delete_event(arguments["event_id"])
        return [types.TextContent(type="text", text=f"Deleted event with ID {arguments['event_id']}")]

    if name == "delete_tag":
        result = misp.delete_tag(arguments["tag"])
        return [types.TextContent(type="text", text=f"Deleted tag '{arguments['tag']}'")]
    

    # Server administration API
    if name == "add_user":
        from pymisp import MISPUser
        user = MISPUser()
        user.email = arguments["email"]
        user.org_id = arguments["org_id"]
        user.role_id = arguments["role_id"]
        result = misp.add_user(user, pythonify=True)
        return [types.TextContent(type="text", text=str(result))]

    if name == "list_users":
        result = misp.users(pythonify=True)
        return [types.TextContent(type="text", text=str(result))]

    if name == "delete_user":
        result = misp.delete_user(arguments["user_id"])
        return [types.TextContent(type="text", text=f"Deleted user ID {arguments['user_id']}")]

    if name == "edit_user":
        from pymisp import MISPUser
        user = MISPUser()
        user.id = arguments["user_id"]
        user.email = arguments["email"]
        result = misp.edit_user(user, pythonify=True)
        return [types.TextContent(type="text", text=str(result))]
 

    



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