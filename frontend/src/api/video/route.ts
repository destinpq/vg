import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const requestData = await request.json();
    const { prompt, duration, quality, style } = requestData;
    
    // Get the API URL from environment variable
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // ALWAYS force Replicate and disable Hunyuan, ignoring any other settings
    const params = new URLSearchParams({
      prompt,
      duration: duration.toString(),
      quality,
      style,
      force_replicate: "true",  // ALWAYS force Replicate
      use_hunyuan: "false",     // ALWAYS disable local Hunyuan
      human_focus: "true"       // Better results with human focus
    });
    
    // Call backend API with GET request
    const response = await fetch(`${apiUrl}/video/generate?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Backend API error');
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in video generation API route:', error);
    return NextResponse.json(
      { error: 'Failed to generate video' },
      { status: 500 }
    );
  }
} 