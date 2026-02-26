from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='reddit_agent',
    description='An agent that summarizes and analyzes Reddit posts.',
    instruction='You are an assistant that summarizes Reddit posts provided in JSON format. Provide a clear summary of the title, context, and engagement (like number of comments).'
)