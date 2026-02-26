# Google Agent Development Kit (ADK) Workshop

Welcome to the Google ADK Workshop! This repository contains a series of hands-on examples and exercises to help you learn how to build, deploy, and manage AI agents using the Google Agent Development Kit.

## Overview

The workshop covers a range of agent types, from simple conversational assistants to complex multi-agent systems and UI automation agents. Each directory represents a specific module in the workshop.

## Project Structure

- **[my_first_agent/](./my_first_agent/)**: Your introduction to the ADK. A simple "Hello World" style agent.
- **[weather_agent/](./weather_agent/)**: A practical example of integrating an external API (OpenWeatherMap) using a Toolset.
- **[reddit_agent/](./reddit_agent/)**: An agent that processes and summarizes Reddit content.
- **[planner_agent/](./planner_agent/)**: Demonstrates a multi-agent workflow using YAML configuration for research and planning.
- **[computer_use_agent/](./computer_use_agent/)**: An advanced agent capable of interacting with a computer (via Playwright/Chrome) to perform UI-based tasks.

## Prerequisites

To participate in this workshop, you will need:

1.  **Google Gemini API Key:** You can obtain one from [Google AI Studio](https://aistudio.google.com/).
2.  **Python 3.10+:** Ensure you have a modern version of Python installed.
3.  **Google ADK:** Install the ADK via pip:
    ```bash
    pip install google-adk
    ```
4.  *(Optional)* **OpenWeatherMap API Key:** Required for the `weather_agent` module.
5.  *(Optional)* **Playwright:** Required for the `computer_use_agent` module.

## Getting Started

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/google/htf-adk-workshop.git
    cd htf-adk-workshop
    ```

2.  **Set Up Your Environment:**
    Create a `.env` file in the root directory (or individual agent directories) with your API keys:
    ```env
    GOOGLE_API_KEY=your_google_api_key
    OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
    ```

3.  **Explore the Modules:**
    Navigate to each agent directory and follow the instructions in their respective `README.md` files.

## Common ADK Commands

The ADK provides a CLI for interacting with your agents:

- **Run an agent:**
  ```bash
  adk run path/to/agent.py --prompt "Your question here"
  ```
- **Start an API server for an agent:**
  ```bash
  adk api_server path/to/agent.py --port 8000
  ```
- **Start the Web interface for the agent:**
  ```bash
  adk web_server path/to/agent.py --port 8000
  ```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details (if available).
