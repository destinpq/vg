import os
import sys
import pytest
import asyncio
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the utils module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import generate_prompts_from_lyrics, generate_prompts_from_lyrics_sync, HINDI_EXAMPLES

@pytest.mark.asyncio
async def test_generate_prompts_from_lyrics_async():
    """Test async version of the lyrics to prompts function."""
    # Test with empty lyrics
    assert await generate_prompts_from_lyrics("") == []
    
    # Test with single line lyrics
    lyrics = "This is a test lyric line"
    prompts = await generate_prompts_from_lyrics(lyrics)
    assert len(prompts) == 1
    assert prompts[0]["line"] == lyrics
    assert prompts[0]["index"] == 0
    assert "prompt" in prompts[0]
    
    # Test with multiple lines
    lyrics = "Line 1\nLine 2\nLine 3"
    prompts = await generate_prompts_from_lyrics(lyrics)
    assert len(prompts) == 3
    assert prompts[0]["line"] == "Line 1"
    assert prompts[1]["line"] == "Line 2"
    assert prompts[2]["line"] == "Line 3"
    
    # Test with style
    style = "noir"
    prompts = await generate_prompts_from_lyrics("Test with style", style=style)
    assert style in prompts[0]["prompt"].lower() or "cinematic scene" in prompts[0]["prompt"].lower()
    
    # Test Hindi examples
    for hindi, expected_en in HINDI_EXAMPLES.items():
        prompts = await generate_prompts_from_lyrics(hindi, language="hindi")
        assert len(prompts) == 1
        assert prompts[0]["prompt"] == expected_en
        assert prompts[0]["line"] == hindi

def test_generate_prompts_from_lyrics_sync():
    """Test sync version of the lyrics to prompts function."""
    # Test with empty lyrics
    assert generate_prompts_from_lyrics_sync("") == []
    
    # Test with single line lyrics
    lyrics = "This is a test lyric line"
    prompts = generate_prompts_from_lyrics_sync(lyrics)
    assert len(prompts) == 1
    assert prompts[0]["line"] == lyrics
    assert prompts[0]["index"] == 0
    assert "prompt" in prompts[0]
    
    # Test Hindi examples
    for hindi, expected_en in HINDI_EXAMPLES.items():
        prompts = generate_prompts_from_lyrics_sync(hindi, language="hindi")
        assert len(prompts) == 1
        assert prompts[0]["prompt"] == expected_en
        assert prompts[0]["line"] == hindi

if __name__ == "__main__":
    # Run tests manually
    pytest.main(["-xvs", __file__]) 