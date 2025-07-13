from fastmcp import Client
import asyncio

client = Client("server.py")

async def call_tool():
    async with client:
        
        # result = await client.call_tool("read_email", {"query": "after:2025-07-07", "max_results": 15})
        # result = await client.call_tool("read_email", {"query": "after:2025-07-07 before:2025-07-08", "max_results": 10})
        result = await client.call_tool("read_email", {"query": "", "max_results": 5})
        print(result)

        # result = await client.call_tool("send_email", {"to": "atinesh.s@gmail.com", "subject": "Test Email", "body": "This is a test email."})
        # print(result)

        # result = await client.call_tool("read_calendar", {"query": "", "time_min": "2025-06-25T00:00:00Z", "time_max": "2025-07-05T23:59:59Z"})
        # print(result)

        # result = await client.call_tool("update_calendar", {"summary": "Test Event", "description": "This is a test event.", "start_date": "2025-07-06T10:00:00Z", "end_date": "2025-07-07T11:00:00Z", "meeting_link": True, "attendees": ["atinesh.singh.ml@gmail.com"]})
        # print(result)

asyncio.run(call_tool())