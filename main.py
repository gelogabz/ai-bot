import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError(
        "GEMINI_API_KEY not found in environment. Create a .env file with GEMINI_API_KEY='your_api_key_here' and don't commit it."
    )

# Create Gemini client
client = genai.Client(api_key=api_key)


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose output")
    args = parser.parse_args()

    prompt = args.user_prompt

    # Build messages list using types.Content
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=messages)

        # Verify usage metadata is present
        usage = getattr(response, "usage_metadata", None)
        if usage is None:
            raise RuntimeError(
                "Gemini API response missing usage metadata; request may have failed."
            )

        # Helper to extract token counts from either dict-like or object-like usage
        def _get_token(u, *names):
            for name in names:
                if isinstance(u, dict):
                    val = u.get(name)
                else:
                    val = getattr(u, name, None)
                if val is not None:
                    return val
            return None

        prompt_tokens = _get_token(
            usage, "prompt_tokens", "input_tokens", "prompt_token_count")
        response_tokens = _get_token(
            usage, "response_tokens", "completion_tokens", "response_token_count")

        # Print verbose metadata only if requested
        if args.verbose:
            print(f"User prompt: {prompt}")

            if prompt_tokens is None:
                print("Prompt tokens: unknown")
            else:
                print(f"Prompt tokens: {prompt_tokens}")

            if response_tokens is None:
                print("Response tokens: unknown")
            else:
                print(f"Response tokens: {response_tokens}")

            print("Response:")
            print(response.text)
        else:
            # Non-verbose: only print the model response
            print(response.text)
    except Exception as e:
        print("Request to Gemini API failed:", e)
        raise


if __name__ == "__main__":
    main()
