#!/usr/bin/env python3

import requests
import sys
import json
import re
import os

# Change to main.py dir
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

from uuid import uuid4
from moviepy.config import change_settings
from random import randint
from config import config
from tiktokvoice import tts
from preview import *
from video import *
from utils import *

if __name__ == "__main__":
    response = requests.get(config['TEDDIT_ENDPOINT'])

    if (response.status_code != 200):
        print("ERROR: Cound not reach teddit API")
        sys.exit()
        
    postData = response.json()

    ## If not specified in config, use data from API
    title = config['CUSTOM_TITLE'] if config['CUSTOM_TITLE'] != "" else postData["title"]
    content = config['CUSTOM_CONTENT_PATH'] if config['CUSTOM_CONTENT_PATH'] != "" else postData["selftext"]

    # Generating Image preview
    previewPath = genPreview({
        "{username}": postData["author"],
        "{time_posted}": relativeTime(datetime.fromtimestamp(postData["created"])),
        "{title}": title,
        "{upvotes}": humanFormat(postData["ups"]),
        "{comments_count}": humanFormat(postData["num_comments"])
    })

    # Cleaning post from html and other garbage
    # text = remove_html_tags(postData["selftext"]).strip()
    text = removeHtmlTags(content).strip()
    sentences = text.replace('\n', '. ').strip().split(".")
    sentences = list(filter(lambda x: x != "", map(lambda x: x.strip(), sentences)))

    paths = []
    # Generate TTS for every sentence
    for sentence in sentences:
        currentTTSPath = f"{config['TEMP_PATH']}/{uuid4()}.mp3"
        tts(sentence, config['TIKTOK_VOICE'], filename=currentTTSPath)

        audioClip = AudioFileClip(currentTTSPath)
        audioClip.audio_fadein(0.01).audio_fadeout(0.01) # Fixing audio glitches occuring every audio clip change
        paths.append(audioClip)

    # Creating intro audio
    introPath = f"{config['TEMP_PATH']}/{uuid4()}.mp3"
    tts(title, config['TIKTOK_VOICE'], filename=introPath)
    introAudio = AudioFileClip(introPath)
    introAudio.audio_fadein(0.01).audio_fadeout(0.01) # For audio glitches

    # Generate subtitles
    subtitlesPath = generate_subtitles(sentences, paths, introAudio.duration)

    # Adding all audios
    paths.insert(0, introAudio)
    finalAudioPath = f"{config['TEMP_PATH']}/{uuid4()}.mp3"
    finalAudio = concatenate_audioclips(paths)
    finalAudio.write_audiofile(finalAudioPath)

    # Preview as ImageClip
    previewClip = ImageClip(previewPath).set_start(0).set_duration(introAudio.duration).set_position(("center", "center"))
    
    # Creating cropped clip video
    clip = VideoFileClip(config['BG_VIDEO_PATH'])
    num = randint(10, int(clip.duration - finalAudio.duration - 10))
    clip = clip.subclip(num, num + finalAudio.duration)

    # Resizing to 9:16
    (w, h) = clip.size
    crop_width = h * 9/16
    x1, x2 = (w - crop_width)//2, (w+crop_width)//2
    y1, y2 = 0, h
    croppedClip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)

    generate_video(croppedClip, previewClip, finalAudioPath, subtitlesPath, config['OUTPUT_PATH'] if config['OUTPUT_PATH'] != "" else f"../{title}.mp4")

    # Clean temp afterwards
    if config['CLEAN_TEMP']:
        cleanDir(config['TEMP_PATH'])