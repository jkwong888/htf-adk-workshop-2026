# Planner Agent (Multi-Agent System)

This module demonstrates a multi-agent workflow using YAML configuration for research and planning.

## Overview

The `planner_agent` is a multi-agent system built using the Google Agent Development Kit. It features a root agent that delegates research and planning tasks to specialized sub-agents. This approach allows for modular, scalable, and complex workflows.

## Prerequisites

- [Google Gemini API Key](https://aistudio.google.com/)

## Setup

1. Ensure you have the `google-adk` package installed.
2. Set your `GOOGLE_API_KEY` environment variable or create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   ```

## Files

- `root_agent.yaml`: The entry point for the multi-agent system. Defines the root agent and its sub-agents.
- `planner_agent.yaml`: Configuration for the planning agent.
- `research_loop_agent.yaml`: Configuration for the research agent, including its loop and sub-agents.
- `critic_agent.yaml`: Configuration for the critic agent that provides feedback on research and plans.

## Workflow

1.  **User Inquiry:** The user provides a research topic to the `root_agent`.
2.  **Delegation:** The `root_agent` delegates the task to the `research_loop_agent`.
3.  **Research & Planning:** The `research_loop_agent` orchestrates a research loop involving the `planner_agent` and `critic_agent`.
4.  **Final Plan:** The `root_agent` receives the final research plan and presents it to the user.

## Usage

### Using the ADK CLI

To run the multi-agent system and provide a prompt:

```bash
adk run planner_agent/root_agent.yaml --prompt "Research the impact of climate change on local agriculture and provide a 5-step research plan."
```

### Starting the API Server

To start a server that allows you to interact with the multi-agent system via an API:

```bash
adk api_server planner_agent/root_agent.yaml --port 8000
```
Once the server is running, you can interact with it at `http://localhost:8000/v1/sessions`.
