import uuid
import srt_equalizer

from config import config
from typing import List
from moviepy.editor import *
from datetime import timedelta
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip

def __generate_subtitles_locally(sentences: List[str], audio_clips: List[AudioFileClip], start_time: float = 0) -> str:
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


def generate_subtitles(sentences: List[str], audio_clips: List[AudioFileClip], start_time: float = 0) -> str:
    # Save subtitles
    subtitles_path = f"{config['TEMP_PATH']}/{uuid.uuid4()}.srt"
    subtitles = __generate_subtitles_locally(sentences, audio_clips, start_time)

    with open(subtitles_path, "w") as file:
        file.write(subtitles + '\n') # Fixing last line not showing

    # Equalize subtitles
    srt_equalizer.equalize_srt_file(subtitles_path, subtitles_path, 128)

    print("[+] Subtitles generated.")

    return subtitles_path

def generate_video(videoFileClip: VideoFileClip, imageClip: ImageClip, tts_path: str, subtitles_path: str, resultPath: str) -> None:
    # Make a generator that returns a TextClip when called with consecutive
    generator = lambda txt: TextClip(
        txt,
        font=config['FONT_PATH'],
        fontsize=config['FONT_SIZE'],
        color=config['COLOR'],
        stroke_color=config['STROKE_COLOR'],
        stroke_width=config['STROKE_WIDTH'],
        method='caption',
        size=(0.75*617, None)

    )

    # Burn the subtitles into the video
    subtitles = SubtitlesClip(subtitles_path, generator)
    result = CompositeVideoClip([
        videoFileClip.set_fps(config['TARGET_FPS']),
        imageClip,
        subtitles.set_pos(("center", "center"))
    ])

    # Add the audio
    audio = AudioFileClip(tts_path)
    audio = audio.set_duration(audio.duration - 0.15) # Fixes audio glitch at the end
    result = result.set_audio(audio)

    result.write_videofile(resultPath, threads=3)