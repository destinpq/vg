"""
Test script for the generate_sequential_prompts_fixed function
"""
import asyncio
import logging
import os
from app.routes.video_fix import setup_openai_api_key, generate_sequential_prompts_fixed

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set up the OpenAI API key explicitly - DO NOT HARD-CODE KEYS
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY" # Uncomment and replace with your key if needed

async def test_generate_prompts():
    """Test the generate_sequential_prompts_fixed function."""
    print("Setting up OpenAI API key...")
    setup_openai_api_key()
    
    print("\nTesting with OpenAI key...")
    prompts = await generate_sequential_prompts_fixed("Eagle soaring high", 5, 3)
    
    print("\nGenerated prompts:")
    for i, prompt in enumerate(prompts):
        print(f"{i+1}: {prompt}")
    
    return prompts

if __name__ == "__main__":
    prompts = asyncio.run(test_generate_prompts())
    print(f"\nSuccessfully generated {len(prompts)} prompts.") 