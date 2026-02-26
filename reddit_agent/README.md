# Reddit Agent

The Reddit Agent is designed to process and summarize Reddit content using the Google Agent Development Kit and Apify.

## Overview

This agent is capable of taking Reddit post data (provided in JSON format) and generating clear, structured summaries, including titles, context, and engagement metrics (e.g., number of comments).

## Prerequisites

- [Google Gemini API Key](https://aistudio.google.com/)
- [Apify API Key](https://apify.com/) (if you're using Apify to fetch the Reddit data)

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r reddit_agent/requirements.txt
   ```
2. Set your `GOOGLE_API_KEY` and `APIFY_API_TOKEN` environment variables or create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   APIFY_API_TOKEN=your_apify_api_token
   ```

## Files

- `agent.py`: Contains the definition of the `reddit_agent`.
- `monitor.py`: A script for monitoring Reddit content and processing it with the agent.
- `requirements.txt`: Python dependencies for this module.

## Usage

### Using the ADK CLI

To run the agent and provide a prompt:

```bash
adk run reddit_agent/agent.py --prompt "Summarize this Reddit post: [JSON DATA HERE]"
```

### Running the Monitor Script

To run the monitor script:

```bash
python3 reddit_agent/monitor.py
```
*(Note: Ensure you have your environment variables set correctly before running the script.)*

### Starting the API Server

To start a server that allows you to interact with the agent via an API:

```bash
adk api_server reddit_agent/agent.py --port 8000
```
