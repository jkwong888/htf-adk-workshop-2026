# Computer Use Agent

The Computer Use Agent is an advanced module that demonstrates how to build agents capable of interacting with a computer (via a browser) to perform UI-based tasks.

## Overview

This agent uses Playwright and the Gemini Computer Use model to perform complex, multi-step actions on websites. It includes support for safety acknowledgements, which are crucial when the model detects potentially risky UI interactions.

## Prerequisites

- [Google Gemini API Key](https://aistudio.google.com/)
- [Playwright](https://playwright.dev/) installed on your machine.
- *(Optional)* [Browserbase API Key](https://www.browserbase.com/) if you're using Browserbase as a remote browser.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r computer_use_agent/requirements.txt
   ```
2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```
3. Set your environment variables or create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   BROWSERBASE_API_KEY=your_browserbase_api_key (optional)
   BROWSERBASE_PROJECT_ID=your_browserbase_project_id (optional)
   HEADLESS=true (optional, defaults to false)
   ```

## Files

- `agent.py`: Contains the definition of the `Computer Use Agent` and its safety acknowledgement logic.
- `playwright_computer.py`: A wrapper for Playwright that provides the agent with computer-use capabilities.
- `verify.py`: A script for verifying the agent's functionality.
- `requirements.txt`: Python dependencies for this module.

## Usage

### Using the ADK CLI

To run the agent and provide a prompt:

```bash
adk run computer_use_agent/agent.py --prompt "Navigate to google.com and search for 'latest AI trends'."
```

### Running the Verification Script

To run the verification script:

```bash
python3 computer_use_agent/verify.py
```

### Starting the API Server

To start a server that allows you to interact with the agent via an API:

```bash
adk api_server computer_use_agent/agent.py --port 8000
```
Once the server is running, you can interact with it at `http://localhost:8000/v1/sessions`.
