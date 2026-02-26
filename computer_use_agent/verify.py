import asyncio
import os
from agent import root_agent
from google.adk.plugins import ReflectAndRetryToolPlugin

async def main():
    print("Initializing agent...")
    
    # Run the prompt
    prompt = """
    show available places on airbnb.
    We are planning a trip from Mar 1 2026 to Mar 4 2026.
    We want to visit Vancouver.
    There 1 adult.
    we want to spend less than $1000 CAD for the whole trip
    we want to only consider places with more than 4.0 stars.
    """

    print(f"Sending prompt to agent: {prompt}")
    
    from google.adk import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
    
    runner = Runner(
        app_name="computer_use_demo",
        agent=root_agent,
        session_service=InMemorySessionService(),
        auto_create_session=True,
        plugins=[
            ReflectAndRetryToolPlugin(max_retries=3)
        ]
    )

    # We will use the stream method
    new_message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    async for event in runner.run_async(user_id="test_user", session_id="test_session", new_message=new_message):
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'text') and event.content.text:
                print(f"Agent: {event.content.text}")
        if event.get_function_calls():
            for call in event.get_function_calls():
                 print(f"Tool Call: {call.name}({call.args})")

if __name__ == "__main__":
    asyncio.run(main())
