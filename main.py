#!/usr/bin/env python3

from preview import *
from tiktokvoice import tts
from uuid import uuid4
from moviepy.config import change_settings
from video import *
from utils import *
from random import randint

import os
import requests
import sys
import json
import re

if __name__ == "__main__":
    response = requests.get("https://teddit.zaggy.nl/r/stories/comments/196l3ak/my_exboyfriend_got_me_a_bottle_of_wine_for_my/?api")

    if (response.status_code != 200):
        print("ERROR: Cound not reach teddit API")
        sys.exit()
        
    postData = response.json()

    # title = "My roommate wore three pairs of jeans every single day. The reason behind this ended up making me vomit."
    title = postData["title"]

    # Generating Image preview
    previewPath = genPreview({
        "{username}": postData["author"],
        "{time_posted}": relativeTime(datetime.fromtimestamp(postData["created"])),
        "{title}": title,
        "{upvotes}": humanFormat(postData["ups"]),
        "{comments_count}": humanFormat(postData["num_comments"])
    }, True)

    # Get content
    with open('content.txt', "r") as f:
        content = f.read()

    # Cleaning post from html and other garbage
    # text = remove_html_tags(postData["selftext"]).strip()
    text = remove_html_tags(content).strip()
    sentences = text.replace('\n', '. ').strip().split(".")
    sentences = list(filter(lambda x: x != "", map(lambda x: x.strip(), sentences)))
    print(sentences)

    paths = []
    # Generate TTS for every sentence
    for sentence in sentences:
        currentTTSPath = f"tmp/{uuid4()}.mp3"
        tts(sentence, "en_us_007", filename=currentTTSPath)

        audioClip = AudioFileClip(currentTTSPath)
        audioClip.audio_fadein(0.01).audio_fadeout(0.01) # Fixing audio glitches occuring every audio clip change
        paths.append(audioClip)

    # Creating intro audio
    introPath = f"tmp/{uuid4()}.mp3"
    tts(title, "en_us_007", filename=introPath)
    introAudio = AudioFileClip(introPath)
    introAudio.audio_fadein(0.01).audio_fadeout(0.01) # For audio glitches

    # Generate subtitles
    subtitlesPath = generate_subtitles(sentences, paths, introAudio.duration)

    # Adding all audios
    paths.insert(0, introAudio)
    finalAudioPath = f"tmp/{uuid4()}.mp3"
    finalAudio = concatenate_audioclips(paths)
    finalAudio.write_audiofile(finalAudioPath)
    
    # Creating cropped clip video
    clip = VideoFileClip('video.mp4')
    num = randint(10, int(clip.duration - finalAudio.duration - 10))
    clip = clip.subclip(num, num + finalAudio.duration)

    # Resizing to 9:16
    (w, h) = clip.size
    crop_width = h * 9/16
    x1, x2 = (w - crop_width)//2, (w+crop_width)//2
    y1, y2 = 0, h
    croppedClip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)

    generate_video(croppedClip,ImageClip(previewPath).set_start(0).set_duration(introAudio.duration).set_position(("center", "center")), finalAudioPath, subtitlesPath)