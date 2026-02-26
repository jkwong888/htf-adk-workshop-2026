"""Computer Use Agent with safety acknowledgement support.

The Gemini Computer Use model may include a `safety_decision` in its tool call
args when it detects potentially risky UI interactions (e.g. CAPTCHAs, consent
banners). Per the official documentation, the corresponding FunctionResponse must
include `safety_acknowledgement: "true"` INSIDE the `response` dictionary.

See: https://ai.google.dev/gemini-api/docs/computer-use#acknowledge-safety-decision
"""

from dotenv import load_dotenv
import os
import base64
import logging

from google.genai import types
from google.adk import Agent
from google.adk.models import Gemini
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
from playwright_computer import PlaywrightComputer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()

headless = os.environ.get("HEADLESS", "false").lower() == "true"
cdp_url = os.environ.get("CHROME_CDP_URL")

computer = PlaywrightComputer(
    screen_size=(1400, 900),
    headless=headless,
    cdp_url=cdp_url,
)


# ---------------------------------------------------------------------------
# Before-model callback: screenshots + safety acknowledgement
# ---------------------------------------------------------------------------
def handle_screenshots_callback(callback_context, llm_request):
    """Process tool responses before sending to the model.

    Two responsibilities:
    1. Embed base64 screenshot data as FunctionResponsePart inline_data.
    2. Auto-acknowledge safety decisions by adding `safety_acknowledgement`
       to the FunctionResponse.response dict (per official docs).
    """
    if not llm_request.contents:
        return None

    # --- Step 1: Synchronize call/response IDs across the history ----------
    # Gemini sometimes omits IDs; we generate synthetic ones so the safety
    # acknowledgement can be matched to the correct function call.
    for turn_idx, content in enumerate(llm_request.contents):
        if content.role != 'model' or turn_idx + 1 >= len(llm_request.contents):
            continue
        next_content = llm_request.contents[turn_idx + 1]
        if next_content.role != 'user':
            continue
        for model_part in content.parts:
            if not model_part.function_call:
                continue
            call_name = model_part.function_call.name
            call_id = model_part.function_call.id
            # Find corresponding response in the next turn
            for user_part in next_content.parts:
                if not (user_part.function_response and
                        user_part.function_response.name == call_name):
                    continue
                resp_id = user_part.function_response.id
                if call_id and not resp_id:
                    user_part.function_response.id = call_id
                elif resp_id and not call_id:
                    model_part.function_call.id = resp_id
                elif not call_id and not resp_id:
                    synth_id = f"synth_{turn_idx}_{call_name}"
                    model_part.function_call.id = synth_id
                    user_part.function_response.id = synth_id

    # --- Step 2: Scan ALL model turns for safety_decision calls ------------
    # Map call IDs to True, AND collect tool names that had safety decisions.
    # The API validates the ENTIRE history, not just the latest turn.
    safety_call_ids = set()
    safety_call_names = set()
    for content in llm_request.contents:
        if content.role != 'model':
            continue
        for part in content.parts:
            if not part.function_call:
                continue
            args = part.function_call.args or {}
            if isinstance(args, dict) and 'safety_decision' in args:
                if part.function_call.id:
                    safety_call_ids.add(part.function_call.id)
                safety_call_names.add(part.function_call.name)

    # --- Step 3: Apply acknowledgements + screenshots to ALL user turns ----
    for content in llm_request.contents:
        if content.role != 'user':
            continue
        for part in content.parts:
            fr = part.function_response
            if not fr or not isinstance(fr.response, dict):
                continue

            resp = fr.response

            # Acknowledge safety: add to response dict per official docs
            needs_ack = (
                (fr.id and fr.id in safety_call_ids) or
                (fr.name in safety_call_names)
            )
            if needs_ack and 'safety_acknowledgement' not in resp:
                resp['safety_acknowledgement'] = "true"
                logger.info("Acknowledged safety for %s (id=%s)", fr.name, fr.id)

            # Embed screenshot data as FunctionResponsePart inline_data
            img_dict = resp.get("image")
            if isinstance(img_dict, dict) and img_dict.get("data"):
                try:
                    raw = img_dict["data"]
                    img_bytes = base64.b64decode(raw) if isinstance(raw, str) else raw
                    fr.parts = [
                        types.FunctionResponsePart(
                            inline_data=types.FunctionResponseBlob(
                                mime_type=img_dict.get("mimetype", "image/png"),
                                data=img_bytes,
                            )
                        )
                    ]
                    del resp["image"]
                except Exception as exc:
                    logger.warning("Failed to embed screenshot for %s: %s", fr.name, exc)

    return None


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------
root_agent = Agent(
    model=Gemini(
        model='gemini-2.5-computer-use-preview-10-2025',
        retry_options=types.HttpRetryOptions(
            initial_delay=1,
            attempts=5,
            exp_base=2,
        ),
    ),
    name='computer_use_demo',
    description=(
        'Computer use agent that can operate a browser on a computer to finish'
        ' user tasks'
    ),
    instruction='You are a helpful computer use agent.',
    tools=[ComputerUseToolset(computer=computer)],
    before_model_callback=handle_screenshots_callback,
)
