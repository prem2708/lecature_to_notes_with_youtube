import os
import yt_dlp

def download_audio_from_url(url, output_path="temp_audio"):
    """
    Downloads audio from a given URL (e.g., YouTube) using yt-dlp.
    
    Args:
        url (str): The URL of the video/audio to download.
        output_path (str): The base name for the output file (without extension).
        
    Returns:
        str: The path to the downloaded audio file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '32',
        }],
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # yt-dlp appends the extension, so we need to find the file
        expected_filename = f"{output_path}.mp3"
        if os.path.exists(expected_filename):
            return expected_filename
        else:
            # Fallback check if something else happened, though mp3 is forced
            return None
            
    except Exception as e:
        # Re-raise the exception with the specific error message from yt-dlp
        raise RuntimeError(f"Download failed: {str(e)}")
