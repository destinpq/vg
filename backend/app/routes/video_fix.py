"""
Fix for the OpenAI API key issue in video generation.
"""
import os
import logging
from typing import List
import openai

def setup_openai_api_key():
    """
    Setup OpenAI API key from environment and check if it's working.
    Returns True if the API key is configured, False otherwise.
    """
    # Try to get the API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If not in environment, try to get it from .env file's value
    if not api_key:
        try:
            env_file_path = os.path.join(os.getcwd(), ".env")
            print(f"Looking for .env file at: {env_file_path}")
            
            with open(env_file_path, "r") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip()
                        # Remove quotes if present
                        if api_key.startswith('"') and api_key.endswith('"'):
                            api_key = api_key[1:-1]
                        elif api_key.startswith("'") and api_key.endswith("'"):
                            api_key = api_key[1:-1]
                        break
        except Exception as e:
            logging.error(f"Error reading API key from .env file: {e}")
    
    # Set the API key in the OpenAI client
    if api_key:
        openai.api_key = api_key
        
        # For the new AsyncOpenAI client
        os.environ["OPENAI_API_KEY"] = api_key
        
        print(f"OpenAI API key configured. Length: {len(api_key)}")
        logging.info(f"OpenAI API key configured. Length: {len(api_key)}")
        return True
    else:
        print("OpenAI API key not found in environment or .env file.")
        logging.error("OpenAI API key not found in environment or .env file.")
        return False

async def generate_sequential_prompts_fixed(initial_prompt: str, num_prompts: int, segment_duration: int) -> List[str]:
    """Calls OpenAI to generate a sequence of evolving prompts. Fixed version that checks for API key."""
    # Set up the API key
    api_key_configured = setup_openai_api_key()
    
    if not api_key_configured:
        logging.error("OpenAI API key not configured. Using fallback prompts.")
        return [f"{initial_prompt} - Segment {i+1}/{num_prompts} (OpenAI disabled)" for i in range(num_prompts)]

    try:
        system_message = f"""You are a creative assistant helping generate prompts for a sequence of short video clips that will be stitched together. 
        The total video will be {num_prompts * segment_duration} seconds long, composed of {num_prompts} segments, each {segment_duration} seconds long.
        Based on the initial user prompt, generate a list of {num_prompts} distinct text prompts, one for each segment.
        Each prompt should describe the scene or action for its {segment_duration}-second segment.
        The prompts must flow logically from one to the next, creating a cohesive visual narrative or evolution.
        Maintain consistency in characters, setting, and style unless the evolution implies a change.
        Focus on clear, visual descriptions suitable for a text-to-video model.
        Output ONLY the list of prompts, each on a new line. Do not include numbering or any other text.
        Example output for 3 prompts:
A cat sleeping peacefully on a sunny windowsill.
 The cat slowly stretches and yawns, opening its eyes.
 The cat jumps off the windowsill and walks towards its food bowl.
        """
        
        user_message = f"Initial prompt: {initial_prompt}"
        
        # Create the client with the API key from environment
        client = openai.AsyncOpenAI()
        completion = await client.chat.completions.create(
            model="gpt-4-turbo-preview", # Or use gpt-4o if available/preferred
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            n=1,
            temperature=0.7, # Adjust for creativity vs coherence
            max_tokens=num_prompts * 70 # Estimate tokens needed
        )
        
        prompts_text = completion.choices[0].message.content.strip()
        prompts_list = [p.strip() for p in prompts_text.split('\n') if p.strip()]
        
        if not prompts_list:
             raise Exception("OpenAI returned empty prompts.")
             
        # Optional: Truncate or pad if OpenAI doesn't return exactly num_prompts
        if len(prompts_list) > num_prompts:
            prompts_list = prompts_list[:num_prompts]
        elif len(prompts_list) < num_prompts:
            # Repeat last prompt or add generic ones
            last_prompt = prompts_list[-1] if prompts_list else initial_prompt
            prompts_list.extend([last_prompt] * (num_prompts - len(prompts_list)))
            
        return prompts_list
    except Exception as e:
        logging.error(f"Error generating prompts with OpenAI: {e}")
        # Fallback: return simple prompts
        return [f"{initial_prompt} - Segment {i+1}/{num_prompts} (OpenAI error: {str(e)})" for i in range(num_prompts)] 