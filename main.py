import os
import argparse
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_function import available_functions, call_function

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
        # Allow the model to iterate with tool calls until it returns a final answer.
        for _ in range(20):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0,
                    tools=[available_functions],
                ),
            )

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

            # Add model candidates to history so the model can see its own outputs
            candidates = getattr(response, "candidates", None)
            if candidates:
                for cand in candidates:
                    messages.append(cand.content)

            # Handle any function calls the model requested
            function_calls = getattr(response, "function_calls", None)

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

            if function_calls:
                function_responses = []
                for function_call in function_calls:
                    function_call_result = call_function(
                        function_call, verbose=args.verbose)

                    if not getattr(function_call_result, "parts", None):
                        raise RuntimeError("call_function returned no parts")

                    part = function_call_result.parts[0]
                    if getattr(part, "function_response", None) is None:
                        raise RuntimeError(
                            "function_response is missing from part")

                    if getattr(part.function_response, "response", None) is None:
                        raise RuntimeError(
                            "function_response.response is missing")

                    function_responses.append(part)

                    if args.verbose:
                        print(f"-> {part.function_response.response}")

                # Append the function results as a user message so the model sees them
                messages.append(types.Content(
                    role="user", parts=function_responses))
                # Continue the loop to let the model react to the tool results
                continue

            # No function calls => final assistant response
            if not function_calls:
                print(response.text)
                break

        else:
            print("Maximum iterations reached without a final response.")
            sys.exit(1)
    except Exception as e:
        print("Request to Gemini API failed:", e)
        raise


if __name__ == "__main__":
    main()
