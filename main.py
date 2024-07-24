from gtts import gTTS  #pip install gTTS
import requests
import json
from pexelsapi.pexels import Pexels  #pip3 install pexels-api-py
import os
from moviepy.editor import *


# Text to be converted to speech
def makeSounds(text):
    tts = gTTS(text)
    tts.save("quotes.mp3")
    
PEXELS_API_KEY = ''


def download_video():
    pexel = Pexels(PEXELS_API_KEY)

    # Search for videos with the query 'ocean'
    search_videos = pexel.search_videos(query='ocean',
                                        orientation='portrait',
                                        size='',
                                        color='',
                                        locale='',
                                        page=1,
                                        per_page=15)

    # Check if there are any videos in the response
    if 'videos' in search_videos and len(search_videos['videos']) > 0:
        # Get the URL of the first video file (assuming HD quality)
        video_url = search_videos['videos'][0]['video_files'][0]['link']

        # Extract the filename from the URL
        video_filename = 'motivation.mp4'

        # Send a GET request to download the video
        response = requests.get(video_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the video file
            with open(video_filename, 'wb') as f:
                f.write(response.content)

            print(f"Video downloaded successfully as {video_filename}!")
        else:
            print(
                f"Failed to download video. Status code: {response.status_code}"
            )
    else:
        print("No videos found for the given query.")


# Call the function to download the video
# download_video()9B26B7
# os.remove('motivation.mp4')
def getQuote():
    res = requests.get("https://zenquotes.io/api/random")
    response = res.json()
    quote = response[0]['q']
    return quote


def makeVideo():
    download_video()
    clip = VideoFileClip("motivation.mp4")
    quote = getQuote()
    makeSounds(quote)  #creates the quote sound video
    os.system("mpg 321 quote.mp3")

    # clipping the video
    clip = clip.subclip(0, 10)

    text_clip = TextClip(quote,
                         fontsize=70,
                         color='white',
                         font='Arial-Bold',
                         method='caption',
                         align='center',
                         stroke_color="black",
                         stroke_width=5)

    # Set the duration of the text clip to match the duration of the video
    text_clip = text_clip.set_duration(clip.duration)

    audioclip = AudioFileClip("quote.mp3")
    new_audioclip = CompositeAudioClip([AudioFileClip("motivation.mp4"),audioclip])

    video = CompositeVideoClip([clip,text_clip])
    video.audio = new_audioclip
    video.write_videofile("output.mp4", fps=24)

# print(getQuote())
