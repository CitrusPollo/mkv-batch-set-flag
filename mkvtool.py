import os
import json
from termcolor import colored
from pprint import pprint


def read_mkv_info(file) -> dict:
    """
    This function runs the `mkvmerge -i` command to input mkv file and returns a JSON output containing info about the tracks inside the file.

    :param file: This is the path of the mkv file.
    """
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


def get_mkv_tracks(tracks: dict) -> list:
    """
    This function returns a list of tracks (objects generated by class Track) present inside an mkv file.

    :param tracks: This is the JSON-formatted output of the mkv info provided by the mkvmerge executable.
    """
    mkv_tracks = list()
    for track in tracks[1:]:  # First track is the video track
        mkv_tracks.append(Track(track))
    return mkv_tracks


def count_tracks(mkv_tracks: list) -> tuple:
    """
    This function counts how many are the the audio tracks and the sub tracks.

    :param mkv_tracks: This is a list of Tracks objects of an mkv file.
    """
    audio_count = sum([x.type == "audio" for x in mkv_tracks])
    sub_count = sum([x.type == "subtitles" for x in mkv_tracks])

    return audio_count, sub_count


# Set default flag to jap audio and eng subtitles
def set_track_flag(track: object, audio_count: int, sub_count: int) -> int:
    """
    This function assigns `flag_default=1` for JAP AUDIO or ENG SUBTITLES. Otherwise, `flag_default=0`.
    If there is only one audio (subtitles) track, `flag_default=1` for that track.
    The variable `flag_default` will be used as commandline argument in `mkvpropedit` later.

    :param track: This is a track (of class Track) inside an mkv file.
    :param audio_count: This is the number of audio tracks inside an mkv file.
    :param sub_count: This is the number of subtitles tracks inside an mkv file.
    """
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
def update_prompt(prompt: str, track: object, flag: bool) -> str:
    """
    This function records which tracks are already determined by `flag_default`.

    :param prompt: This is the initial string in the prompt.
    :param track: This is a track (of class Track) inside an mkv file.
    :param flag: This is a boolean setting for `flag_default`.
    """
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


def update_command(command: str, track: object, flag: bool) -> str:
    """
    This function adds another track to modify in the commandline arguments of `mkvpropedit`

    :param command: This is the initial string of `mkvpropedit` command.
    :param track: This is a track (of class Track) inside an mkv file.
    :param flag: This is a boolean setting for `flag_default`.
    """
    command += (
        f" --edit track:{track.number}"
        f" --set flag-default={flag}"
        f" --set flag-forced={flag}"
    )
    return command


def output_prompt(prompt: str, flag_count: int) -> None:
    """
    This function adds a status check whether there is sufficient audio track(s) and subtitles track(s) set to `flag_default=1`

    :param prompt: This is a string containing the processed tracks.
    :param flag_count: This is the total number of tracks with `flag_default=1`.
    """
    toggle = 1 if flag_count >= 2 else 0
    color = "yellow" * (1 - toggle) + "cyan" * toggle
    check = "Check tracks" * (1 - toggle) + "Pass" * toggle

    prompt += colored(check, color) + "\n"

    print(prompt)


def update_mkv_tracks(file: str, mkv_tracks: list) -> None:
    """
    This function prepares the commandline arguments for `mkvpropedit` with the path `file` as input.
    Once all tracks are processed, `mkvpropedit` is run with the complete commandline arguments.

    :param file: This is the path of the mkv file.
    :param mkv_tracks: This is a list of Tracks objects of an mkv file.
    """
    audio_count, sub_count = count_tracks(mkv_tracks)

    command = f'mkvpropedit "{file}"'
    prompt = f"{file} \n Audio tracks:{audio_count} Subtitle tracks:{sub_count} \n"
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
