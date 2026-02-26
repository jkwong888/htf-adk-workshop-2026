import argparse
import sys
import json
import requests

def main():
    parser = argparse.ArgumentParser(description="A weather agent client.")
    parser.add_argument("--url", required=True, help="The base URL of the agent API server.")
    parser.add_argument("--prompt", help="The prompt to send to the weather agent. If not provided, it will read from stdin.")
    parser.add_argument("--user-id", default="cli_user", help="The user ID to use (default: cli_user).")
    parser.add_argument("--app-name", default="weather_agent", help="The application name (default: weather_agent).")

    args = parser.parse_args()

    # Determine prompt source
    if args.prompt:
        prompt = args.prompt
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            print("Enter your prompt (Ctrl+D to finish):")
            prompt = sys.stdin.read().strip()

    if not prompt:
        print("Error: No prompt provided.")
        sys.exit(1)

    base_url = args.url.rstrip("/")
    app_name = args.app_name
    user_id = args.user_id

    # 1. Create a new session
    # Endpoint: POST /apps/{app_name}/users/{user_id}/sessions
    session_url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions"
    try:
        # We can send an empty JSON for defaults
        response = requests.post(session_url, json={})
        response.raise_for_status()
        session_data = response.json()
        session_id = session_data["id"]
        # print(f"Created new session: {session_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating session: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response status: {e.response.status_code}")
             print(f"Response body: {e.response.text}")
        sys.exit(1)

    # 2. Send the prompt to the /run endpoint
    # Endpoint: POST /run
    run_url = f"{base_url}/run"
    payload = {
        "appName": app_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {
            "parts": [{"text": prompt}],
            "role": "user"
        }
    }
    
    try:
        response = requests.post(run_url, json=payload)
        response.raise_for_status()
        
        # Output the response
        try:
            results = response.json()
            # The agent returns a list of message objects. 
            # We want the last one that has 'text' in its parts.
            final_text = None
            for message in reversed(results):
                if "content" in message and "parts" in message["content"]:
                    for part in message["content"]["parts"]:
                        if "text" in part:
                            final_text = part["text"]
                            break
                if final_text:
                    break
            
            if final_text:
                print(final_text)
            else:
                print(json.dumps(results, indent=2))
        except ValueError:
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with the agent: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response status: {e.response.status_code}")
             print(f"Response body: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
