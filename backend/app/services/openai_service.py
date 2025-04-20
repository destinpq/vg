"""
OpenAI Integration Service for creative prompt interpretation and enhancement
"""

import os
import json
from openai import OpenAI, AsyncOpenAI
from typing import Dict, Any, List, Optional
from app.utils.config import get_settings

settings = get_settings()

# Initialize OpenAI API client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:
    """Service for OpenAI API integration"""
    
    @staticmethod
    async def enhance_video_prompt(prompt: str, style: str = "realistic") -> Dict[str, Any]:
        """
        Use GPT-4 to analyze and enhance a video generation prompt
        
        Args:
            prompt: The original user prompt
            style: The desired style (realistic, abstract, etc.)
            
        Returns:
            Dictionary with enhanced prompt information and visualization guidance
        """
        try:
            if style == "realistic" or "realistic" in prompt.lower() or "hyper realistic" in prompt.lower() or "photorealistic" in prompt.lower():
                system_message = """
                You are a master cinematographer and visual effects director specializing in hyper-realistic digital content creation.
                Analyze the user's prompt and provide guidance for generating an extremely photorealistic video.
                
                For the prompt, return a JSON object with the following:
                
                1. "enhanced_prompt": An expanded version of the original prompt with EXTREME detail on textures, lighting, camera movement, 
                   and photorealistic elements. Focus on physical reality, real-world physics, and photographic terminology.
                2. "scene_type": The primary environment [urban, nature, interior, underwater, aerial, macro, etc.]
                3. "visual_elements": 5-7 SPECIFIC hyper-realistic elements that should be clearly visible (textures, materials, etc.)
                4. "lighting_conditions": Detailed description of lighting (e.g., "golden hour side lighting with soft shadows and subtle lens flare")
                5. "camera_movement": Specific, gradual camera movement (e.g., "slow dolly in with subtle handheld stabilization")
                6. "photorealism_details": Technical details that add realism (depth of field, film grain, micro-expressions, etc.)
                7. "color_grading": Film-like color treatment (e.g., "Alexa LUT with slight cyan in shadows, warm highlights")
                8. "composition_notes": Cinematography notes on framing and composition
                
                Structure your response as a valid JSON object with no additional text. Focus EXCLUSIVELY on creating guidance for
                HYPER-REALISTIC content that would be indistinguishable from real footage.
                """
            else:
                system_message = """
                You are an expert AI video director and visual artist. Analyze the user's video prompt 
                and provide structured creative direction for generating a video visualization.
                
                For each prompt, return a JSON object with the following:
                
                1. "enhanced_prompt": An enhanced version of the original prompt with more visual detail
                2. "scene_type": One of [nature, urban, ocean, sky, abstract, fantasy, portrait, space, weather]
                3. "color_palette": List of 3-5 color names that would work well for this scene
                4. "visual_elements": List of 3-5 specific visual elements to include 
                5. "mood": The overall emotional tone or atmosphere
                6. "movement_pattern": Description of how elements should move (e.g., "floating clouds", "pulsating waves")
                7. "time_of_day": Suggested time of day for the scene if applicable
                8. "composition_guidance": Notes on visual composition and layout
                
                Structure your response as a valid JSON object only, with no additional text.
                """
            
            user_message = f"Create video visualization guidance for: {prompt}"
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract JSON from the response
            result_text = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            try:
                result = json.loads(result_text)
                print(f"Enhanced prompt: {result['enhanced_prompt']}")
                # Add the style that was used
                result["style_used"] = style
                return result
            except json.JSONDecodeError:
                print(f"Failed to parse JSON from OpenAI response: {result_text}")
                return {
                    "enhanced_prompt": prompt,
                    "scene_type": "abstract",
                    "color_palette": ["blue", "purple", "pink"],
                    "visual_elements": ["waves", "particles", "glow"],
                    "mood": "ambient",
                    "movement_pattern": "flowing waves",
                    "time_of_day": "unspecified",
                    "composition_guidance": "centered focal point with dynamic movement",
                    "style_used": style
                }
                
        except Exception as e:
            print(f"Error in OpenAI service: {e}")
            # Return default values if OpenAI call fails
            return {
                "enhanced_prompt": prompt,
                "scene_type": "abstract",
                "color_palette": ["blue", "purple", "pink"],
                "visual_elements": ["waves", "particles", "glow"],
                "mood": "ambient",
                "movement_pattern": "flowing waves",
                "time_of_day": "unspecified",
                "composition_guidance": "centered focal point with dynamic movement",
                "style_used": style
            }
            
    @staticmethod
    async def generate_scene_description(prompt: str, style: str = "realistic") -> str:
        """
        Generate a detailed scene description for video generation
        
        Args:
            prompt: The original user prompt
            style: The desired style (realistic, abstract, etc.)
            
        Returns:
            Detailed scene description
        """
        try:
            if style == "realistic" or "realistic" in prompt.lower() or "hyper realistic" in prompt.lower() or "photorealistic" in prompt.lower():
                system_message = """
                You are a world-class film director and cinematographer specializing in photorealistic CGI and visual effects.
                
                Convert the user's prompt into an EXTREMELY detailed, hyper-realistic scene description that could be used by 
                a high-end CGI team. Your description should:
                
                1. Focus on extreme photorealism - specify textures, materials, lighting, atmosphere, and camera work
                2. Include technical details a cinematographer would note - lens choice, depth of field, camera movement
                3. Describe subtle realistic elements - micro-expressions, fine textures, atmospheric effects
                4. Indicate how light interacts with surfaces realistically
                5. Be approximately 150-200 words to capture significant detail
                
                Provide only the technical description, nothing else. Focus exclusively on creating guidance that would
                result in footage indistinguishable from a real, high-production value film.
                """
            else:
                system_message = """
                You are an expert AI cinematographer and visual artist. Convert the user's simple prompt 
                into a detailed scene description that could be used to generate a video. 
                
                Your description should:
                1. Be highly visual and detailed
                2. Include specific colors, textures, and movements
                3. Describe how elements interact and change over time
                4. Be around 100-150 words
                
                Provide only the description, nothing else.
                """
            
            user_message = f"Create a detailed scene description for: {prompt}"
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500  # Increased for more detailed descriptions
            )
            
            # Extract the scene description
            scene_description = response.choices[0].message.content.strip()
            print(f"Generated scene description: {scene_description[:100]}...")
            return scene_description
            
        except Exception as e:
            print(f"Error generating scene description: {e}")
            return prompt
            
    @staticmethod
    async def get_realistic_image_prompt(text_prompt: str) -> str:
        """
        Convert a text prompt into a detailed image generation prompt optimized for realism
        
        Args:
            text_prompt: The original user prompt
            
        Returns:
            Enhanced image generation prompt
        """
        try:
            system_message = """
            You are an expert in creating optimal prompts for photorealistic AI image generation.
            
            Convert the user's text into a highly detailed prompt for generating an ultra-realistic image.
            Your output should:
            
            1. Start with "photorealistic, 8k, ultra-detailed"
            2. Specify camera details (lens type, camera model, etc.)
            3. Include lighting specifics (golden hour, studio lighting, etc.)
            4. Mention materials and textures in extreme detail
            5. Reference specific film stocks or photography styles
            6. Include technical terms that boost realism
            
            Provide ONLY the optimized prompt, no explanations or other text.
            """
            
            user_message = f"Create an ultra-realistic image generation prompt for: {text_prompt}"
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            # Extract the enhanced prompt
            enhanced_prompt = response.choices[0].message.content.strip()
            print(f"Enhanced realistic image prompt: {enhanced_prompt[:100]}...")
            return enhanced_prompt
            
        except Exception as e:
            print(f"Error generating realistic image prompt: {e}")
            return f"photorealistic, 8k, ultra-detailed {text_prompt}" 