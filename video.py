import os
import uuid
import requests
import srt_equalizer

from typing import List
from moviepy.editor import *
from datetime import timedelta
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip

def __generate_subtitles_locally(sentences: List[str], audio_clips: List[AudioFileClip], start_time: complex = 0) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track
    Returns:
        str: The generated subtitles
    """

    def convert_to_srt_time_format(total_seconds):
        # Convert total seconds to the SRT time format: HH:MM:SS,mmm
        if total_seconds == 0:
            return "0:00:00,000"

        return str(timedelta(seconds=total_seconds)).replace('.', ',')[0:11]

    subtitles = []

    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
        duration = audio_clip.duration
        end_time = start_time + duration

        # Format: subtitle index, start time --> end time, sentence
        subtitles.append(f"{i}\n{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n{sentence}\n")

        start_time += duration  # Update start time for the next subtitle

    return "\n".join(subtitles)


def generate_subtitles(sentences: List[str], audio_clips: List[AudioFileClip], start_time: complex = 0) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track

    Returns:
        str: The path to the generated subtitles.
    """

    # Save subtitles
    subtitles_path = f"subtitles/{uuid.uuid4()}.srt"
    subtitles = __generate_subtitles_locally(sentences, audio_clips, start_time)

    with open(subtitles_path, "w") as file:
        file.write(subtitles + '\n') # Fixing last line not showing

    # Equalize subtitles
    srt_equalizer.equalize_srt_file(subtitles_path, subtitles_path, 9999)

    print("[+] Subtitles generated.")

    return subtitles_path

def generate_video(videoFileClip: VideoFileClip, imageClip: ImageClip, tts_path: str, subtitles_path: str) -> str:
    """
    This function creates the final video, with subtitles and audio.

    Args:
        video_path (str): The path to the combined video.
        tts_path (str): The path to the text-to-speech audio.
        subtitles_path (str): The path to the subtitles.

    Returns:
        str: The path to the final video.
    """
    # Make a generator that returns a TextClip when called with consecutive
    generator = lambda txt: TextClip(
        txt,
        font="fonts/Roboto.ttf",
        fontsize=36,
        color="#FFFF00",
        stroke_color="black",
        stroke_width=2,
        method='caption',
        size=(0.75*617, None)

    )

    # Burn the subtitles into the video
    subtitles = SubtitlesClip(subtitles_path, generator)
    result = CompositeVideoClip([
        videoFileClip.set_fps(50),
        imageClip,
        subtitles.set_pos(("center", "center"))
    ])

    # Add the audio
    audio = AudioFileClip(tts_path)
    audio = audio.set_duration(audio.duration - 0.15) # Fixes audio glitch at the end
    result = result.set_audio(audio)

    result.write_videofile("output.mp4", threads=3)

    return "output.mp4"