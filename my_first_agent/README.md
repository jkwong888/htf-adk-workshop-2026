# My First Agent

This module is the starting point for the Google ADK Workshop. It introduces you to the basic concepts of building an agent using the Google Agent Development Kit.

## Overview

The `my_first_agent` is a simple, helpful assistant that uses the Gemini model to answer user questions. It's designed to be minimal and easy to understand.

## Prerequisites

- [Google Gemini API Key](https://aistudio.google.com/)

## Setup

1. Ensure you have the `google-adk` package installed.
2. Set your `GOOGLE_API_KEY` environment variable or create a `.env` file in this directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   ```

## Files

- `agent.py`: Contains the definition of the `root_agent` using the `Agent` class from the ADK.

## Usage

### Using the ADK CLI

To run the agent and provide a prompt:

```bash
adk run my_first_agent/agent.py --prompt "Hello! What can you do?"
```

### Starting the API Server

To start a server that allows you to interact with the agent via an API:

```bash
adk api_server my_first_agent/agent.py --port 8000
```

Once the server is running, you can send POST requests to `http://localhost:8000/v1/sessions` to start a session and interact with the agent.
