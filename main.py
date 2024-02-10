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
sys.path.append('src')

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
    content = getFileContent(config['CUSTOM_CONTENT_PATH']) if config['CUSTOM_CONTENT_PATH'] != "" else postData["selftext"]

    print(f"{bcolors.OKCYAN}Generating preview image...{bcolors.ENDC}")
    # Generating preview image
    previewPath = genPreview({
        "{username}": postData["author"],
        "{time_posted}": relativeTime(datetime.fromtimestamp(postData["created"])),
        "{title}": title,
        "{upvotes}": humanFormat(postData["ups"]),
        "{comments_count}": humanFormat(postData["num_comments"])
    })
    print(f"{bcolors.OKCYAN}Generating preview image... {bcolors.OKGREEN}{bcolors.BOLD}DONE{bcolors.ENDC}")

    # Cleaning post from html and other garbage
    # TODO: clean this code out, I leave it be for now
    text = removeHTMLTags(content).strip()
    sentences = text.replace('\n', '. ').strip().split(".")
    sentences = list(filter(lambda x: x != "", map(lambda x: x.strip(), sentences)))
    sentences.insert(0, title)

    print(f"{bcolors.OKCYAN}Rendering audio files...{bcolors.ENDC}")
    audioPaths = []
    # Generate TTS for every sentence
    for sentence in sentences:
        currentTTSPath = f"{config['TEMP_PATH']}/{uuid4()}.mp3"
        tts(sentence, config['TIKTOK_VOICE'], filename=currentTTSPath)

        # Fades fix audio glitches occuring almost every audio clip change
        audioPaths.append(AudioFileClip(currentTTSPath).audio_fadein(0.05).audio_fadeout(0.05))
    print(f"{bcolors.OKCYAN}Rendering audio files... {bcolors.OKGREEN}{bcolors.BOLD}DONE{bcolors.ENDC}")

    # Generate subtitles
    print(f"{bcolors.OKCYAN}Rendering subtitles...{bcolors.ENDC}")
    subtitlesPath = generateSubtitles(sentences, audioPaths)
    print(f"{bcolors.OKCYAN}Rendering subtitles... {bcolors.OKGREEN}{bcolors.BOLD}DONE{bcolors.ENDC}")

    print(f"{bcolors.OKCYAN}Rendering final video...{bcolors.ENDC}")
    # Adding all audios
    finalAudio = concatenate_audioclips(audioPaths)

    # Preview as ImageClip
    previewClip = ImageClip(previewPath).set_start(0).set_duration(audioPaths[0].duration).set_position(("center", "center"))
    
    # Creating cropped clip video
    clip = VideoFileClip(config['BG_VIDEO_PATH'])
    num = randint(10, int(clip.duration - finalAudio.duration - 10))
    clip = clip.subclip(num, num + finalAudio.duration)

    # Resizing to 9:16
    # https://stackoverflow.com/a/74586686
    (w, h) = clip.size
    crop_width = h * 9/16
    x1, x2 = (w - crop_width)//2, (w+crop_width)//2
    y1, y2 = 0, h
    croppedClip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)

    generateVideo(croppedClip, finalAudio, previewClip, subtitlesPath, f"{config['OUTPUT_PATH']}/{title}.mp4" if config['OUTPUT_PATH'] != "" else f"{title}.mp4")
    print(f"{bcolors.OKCYAN}Rendering final video... {bcolors.OKGREEN}{bcolors.BOLD}DONE{bcolors.ENDC}")

    # Clean temp afterwards
    if config['CLEAN_TEMP']:
        print(f"{bcolors.OKCYAN}Cleaning temp files...{bcolors.ENDC}")
        cleanDir(config['TEMP_PATH'])
        print(f"{bcolors.OKCYAN}Cleaning temp files... {bcolors.OKGREEN}{bcolors.BOLD}DONE{bcolors.ENDC}")