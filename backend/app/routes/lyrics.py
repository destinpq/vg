from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.lyrics import LyricsToVideoRequest, LyricsToVideoResponse
from app.services.lyrics_service import LyricsService

router = APIRouter()
lyrics_service = LyricsService()

@router.post("/generate", response_model=LyricsToVideoResponse)
async def generate_video_from_lyrics(request: LyricsToVideoRequest):
    """
    Generate a video based on the provided lyrics
    
    - Takes lyrics, language, and optionally style and audio file
    - Converts each line of lyrics into a video prompt
    - Generates video clips for each prompt
    - Stitches the clips together
    - Returns a URL to the final video
    """
    try:
        result = await lyrics_service.generate_video_from_lyrics(
            lyrics=request.lyrics,
            language=request.language,
            style=request.style,
            audio_file=request.audio_file
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating video from lyrics: {str(e)}")

@router.get("/status/{video_id}")
async def get_lyrics_video_status(video_id: str):
    """
    Get the status of a lyrics-to-video generation job
    """
    try:
        result = await lyrics_service.get_job_status(video_id)
        if result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Video job not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving video status: {str(e)}") 