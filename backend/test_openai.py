"""
Simple test script to verify that the OpenAI API key works.
"""
import os
import sys
import openai
import asyncio
from dotenv import load_dotenv

# Try to load from .env file
load_dotenv()

# Get the API key
api_key = os.environ.get("OPENAI_API_KEY")

print(f"API Key found: {'Yes, length: ' + str(len(api_key)) if api_key else 'No'}")

# Configure it explicitly
if api_key:
    openai.api_key = api_key

    # For the AsyncOpenAI client as well
    os.environ["OPENAI_API_KEY"] = api_key

async def test_openai_async():
    """Test if the OpenAI AsyncClient works with the configured API key."""
    try:
        client = openai.AsyncOpenAI()
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ],
            max_tokens=50
        )
        print("\nAsyncOpenAI response received:")
        print(completion.choices[0].message.content)
        return True
    except Exception as e:
        print(f"\nAsyncOpenAI Error: {str(e)}")
        return False

# Run the async test
if __name__ == "__main__":
    print("\nTesting OpenAI API key...")
    result = asyncio.run(test_openai_async())
    if result:
        print("OpenAI API key is working correctly!")
    else:
        print("OpenAI API key test failed!")
    
    sys.exit(0 if result else 1) 