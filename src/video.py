import uuid
import srt_equalizer

from config import config
from typing import List
from moviepy.editor import *
from datetime import timedelta
from moviepy.video.fx.all import fadeout, fadein
from moviepy.video.tools.subtitles import SubtitlesClip

def generateSubtitlesLocally(sentences: List[str], audioClips: List[AudioFileClip]) -> str:
    def convertToSrtTimeFormat(totalSeconds):
        # Convert total seconds to the SRT time format: HH:MM:SS,mmm
        if totalSeconds == 0:
            return "0:00:00,000"

        return str(timedelta(seconds=totalSeconds)).replace('.', ',')[0:11]

    # Skip the intro
    subtitles = []
    startTime = audioClips[0].duration

    for i in range(1, len(sentences)):
        duration = audioClips[i].duration
        endTime = startTime + duration

        # Format: subtitle index, start time --> end time, sentence
        subtitles.append(f"{i}\n{convertToSrtTimeFormat(startTime)} --> {convertToSrtTimeFormat(endTime)}\n{sentences[i]}\n")
        startTime += duration  # Update start time for the next subtitle

    return "\n".join(subtitles)


def generateSubtitles(sentences: List[str], audioClips: List[AudioFileClip]) -> str:
    # Save subtitles
    subtitlesPath = f"{config['TEMP_PATH']}/{uuid.uuid4()}.srt"
    subtitles = generateSubtitlesLocally(sentences, audioClips)

    with open(subtitlesPath, "w") as file:
        file.write(subtitles + '\n') # Fixes last line not showing

    # Equalize subtitles
    srt_equalizer.equalize_srt_file(subtitlesPath, subtitlesPath, 100)

    return subtitlesPath

def generateVideo(videoClip: VideoClip, audioFileClip: AudioFileClip, imageClip: ImageClip, subtitlesPath: str, resultPath: str) -> None:
    # Make a generator that returns a TextClip when called with consecutive
    generator = lambda txt: TextClip(
        txt,
        font=config['FONT_PATH'],
        fontsize=config['FONT_SIZE'],
        color=config['FONT_COLOR'],
        stroke_color=config['STROKE_COLOR'],
        stroke_width=config['STROKE_WIDTH'],
        method='caption',
        size=(0.75*617, None)
    )

    # Burn the subtitles into the video
    subtitles = SubtitlesClip(subtitlesPath, generator)
    result = CompositeVideoClip([
        videoClip.set_fps(config['TARGET_FPS']),
        imageClip,
        subtitles.set_pos(("center", "center"))
    ])

    # Add the audio
    result = result.set_audio(audioFileClip.set_duration(audioFileClip.duration - 0.15)) # Fixes audio glitch at the end
    result.write_videofile(resultPath, threads=12)

    return VideoFileClip(resultPath)

def divideIntoParts(videoClip: VideoClip, title: str):
    if (videoClip.duration <= config['MAX_VIDEO_LENGTH']):
        return False

    generator = lambda txt: TextClip(
        txt,
        font=config['FADEOUT_FONT_PATH'],
        fontsize=config['FADEOUT_FONT_SIZE'],
        color=config['FADEOUT_FONT_COLOR'],
        method='caption',
        size=(0.75*617, None)
    )

    partsCount = int(videoClip.duration // config['MAX_VIDEO_LENGTH'] + 1)
    clipDuration = videoClip.duration / partsCount
    fadeoutDuration = config['FADEOUT_DURATION']
    fadeoutTextDuration = config['FADEOUT_TEXT_DURATION']

    currentTime = 3 # The first part will be +3 secs, but the code is cleaner soo....

    for i in range(partsCount):
        ## cut
        videoPart = videoClip.subclip(currentTime - 4, currentTime + clipDuration if i < partsCount - 1 else videoClip.duration)
        
        if i < partsCount - 1:
            ## fadeOut
            videoPart = fadeout(videoPart, fadeoutDuration)

            ## new part adnotation
            trailerText = generator(f"Stay tuned\nfor\nPart {i+2}")
            trailerText = trailerText.set_start(videoPart.duration - fadeoutTextDuration).set_duration(fadeoutTextDuration).set_pos(("center", "center"))

            videoPart = CompositeVideoClip([
                videoPart.audio_fadeout(fadeoutDuration),
                fadein(trailerText, fadeoutTextDuration)
            ])

        videoPart.write_videofile(f"{config['OUTPUT_FOLDER']}/{title} - part {i+1}.mp4", threads=12)
        currentTime = currentTime + clipDuration

    return True