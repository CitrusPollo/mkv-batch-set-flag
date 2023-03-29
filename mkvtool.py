import os
import json
from termcolor import colored
from pprint import pprint


# Load mkv track info into a json format
def read_mkv_info(file) -> dict:
    command = f'mkvmerge -i "{file}" -F json'
    mkv_info = os.popen(command).read()
    mkv_info = json.loads(mkv_info)
    tracks = mkv_info["tracks"]
    for track in tracks:
        track["properties"].pop("codec_private_data", None)
    # pprint(mkv_info)
    return tracks


# Define track properties
class Track:
    def __init__(self, track) -> None:
        properties = track["properties"]

        self.name = properties.get("track_name", "None")
        self.number = properties["number"]
        self.language = properties["language"]
        self.type = track["type"]


# Read embedded tracks in mkv
def get_mkv_tracks(tracks) -> dict:
    mkv_tracks = list()
    for track in tracks[1:]:  # First track is the video track
        mkv_tracks.append(Track(track))
    return mkv_tracks


# Count how many audio tracks and sub tracks ther are in the mkv file
def count_tracks(mkv_tracks) -> tuple:
    audio_count = sum([x.type == "audio" for x in mkv_tracks])
    sub_count = sum([x.type == "subtitles" for x in mkv_tracks])

    return audio_count, sub_count


# Set default flag to jap audio and eng subtitles
def set_track_flag(track, audio_count, sub_count) -> int:
    track_names = ["dialog", "full", "english"]

    is_jpn_audio = track.type == "audio" and track.language == "jpn"
    is_dialog_sub = any(text in track.name.lower() for text in track_names)
    is_eng_sub = track.type == "subtitles" and track.language == "eng"

    flag_default = 0
    if is_jpn_audio or (is_jpn_audio and audio_count == 1):
        flag_default = 1
    if is_eng_sub and (is_dialog_sub or sub_count == 1):
        flag_default = 1
    if sub_count == 1:
        flag_default = 1

    return flag_default


# Append the modified tracks to the prompt string
def update_prompt(prompt, track, flag) -> str:
    color = "dark_grey" * (1 - flag) + "green" * flag
    prompt += colored(
        f" Track:{track.number}"
        f" Type:{track.type[:3]}"
        f" Language:{track.language}"
        f" Name:{track.name}"
        "\n",
        color,
    )
    return prompt


# Compile mkvpropedit command
def update_command(command, track, flag) -> str:
    command += (
        f" --edit track:{track.number}"
        f" --set flag-default={flag}"
        f" --set flag-forced={flag}"
    )
    return command


# Print the complete prompt message and the Pass status
def output_prompt(prompt, flag_count) -> None:
    toggle = 1 if flag_count == 2 else 0
    color = "red" * (1 - toggle) + "cyan" * toggle
    check = "Missing track" * (1 - toggle) + "Pass" * toggle

    prompt += colored(check, color) + "\n"

    print(prompt)


# The parent function
def update_mkv_tracks(file, mkv_tracks) -> None:
    audio_count, sub_count = count_tracks(mkv_tracks)

    command = f'mkvpropedit "{file}"'
    prompt = (
        f"{file} \n" f" Audio tracks:{audio_count}" f" Subtitle tracks:{sub_count} \n"
    )
    flag_count = 0  # Value 2 means one audio and one sub are activated

    # Compile the command and prompt
    for track in mkv_tracks:
        flag = set_track_flag(track, audio_count, sub_count)
        flag_count += flag

        command = update_command(command, track, flag)
        prompt = update_prompt(prompt, track, flag)

    # Run mkvpropedit command
    os.popen(command)
    output_prompt(prompt, flag_count)
