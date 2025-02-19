from dotenv import load_dotenv
load_dotenv()
from gtts import gTTS  # pip install gTTS
import requests
from pexelsapi.pexels import Pexels  # pip3 install pexels-api-py
import os
import sys
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import tempfile
import textwrap

# Text to be converted to speech
def makeSounds(text):
    tts = gTTS(text)
    tts.save("quote.mp3")
    
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

def download_video():
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY not found in .env")
        return

    pexel = Pexels(PEXELS_API_KEY)
    # Search for videos with the query 'ocean'
    search_videos = pexel.search_videos(query='ocean',
                                        orientation='portrait',
                                        size='',
                                        color='',
                                        locale='',
                                        page=1,
                                        per_page=15)
    if 'videos' in search_videos and len(search_videos['videos']) > 0:
        video_url = search_videos['videos'][0]['video_files'][0]['link']
        video_filename = 'motivation.mp4'
        response = requests.get(video_url)
        if response.status_code == 200:
            with open(video_filename, 'wb') as f:
                f.write(response.content)
            print(f"Video downloaded successfully as {video_filename}!")
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
    else:
        print("No videos found for the given query.")

def getQuote():
    res = requests.get("https://zenquotes.io/api/random")
    response = res.json()
    quote = response[0]['q']
    return quote

def create_text_image(text, width, height, fontsize=70):
    # Create an image with transparent background
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except IOError:
        font = ImageFont.load_default()
    
    # Wrap long text so it fits nicely
    max_chars_per_line = 40
    wrapped_text = "\n".join(textwrap.wrap(text, width=max_chars_per_line))
    
    # Compute text dimensions with fallback using textbbox if needed
    try:
        text_width, text_height = draw.textsize(wrapped_text, font=font)
    except AttributeError:
        bbox = draw.textbbox((0,0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Draw border (simulate stroke)
    border = 2
    for dx in range(-border, border+1):
        for dy in range(-border, border+1):
            draw.text((x+dx, y+dy), wrapped_text, font=font, fill="black")
    draw.text((x, y), wrapped_text, font=font, fill="white")
    return img

def makeVideo():
    video_file = sys.argv[1] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else 'motivation.mp4'
    if video_file == 'motivation.mp4' and not os.path.exists(video_file):
        download_video()
    
    if not os.path.exists(video_file):
        print(f"Video file '{video_file}' not found. Exiting makeVideo.")
        return
    
    clip = VideoFileClip(video_file)
    quote = getQuote()
    makeSounds(quote)
    
    # Play the generated audio using the default player on Windows
    try:
        os.startfile("quote.mp3")
    except Exception as e:
        print("Could not play audio:", e)

    # Use only the first 10 seconds of the video
    clip = clip.subclip(0, 10)
    
    # Create text overlay image using Pillow
    width, height = clip.size
    text_img = create_text_image(quote, int(width), int(height), fontsize=70)
    tmp_dir = tempfile.gettempdir()
    tmp_text_path = os.path.join(tmp_dir, "text_overlay.png")
    text_img.save(tmp_text_path)
    
    text_clip = ImageClip(tmp_text_path).set_duration(clip.duration)
    
    # Use only the generated quote audio (ensure its duration matches the video)
    audioclip = AudioFileClip("quote.mp3").set_duration(clip.duration)
    
    # Compose the video with the text overlay and generated audio
    video = CompositeVideoClip([clip, text_clip])
    video.audio = audioclip
    video.write_videofile("output.mp4", fps=24)

if __name__ == '__main__':
    makeVideo()