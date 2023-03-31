## What is this?
This Python program automates the process of setting JPN audio and full ENG subtitles as default tracks for mkv files. 

## Requirements
You need only two programs, `mkvmerge` and `mkvpropedit`. These are part of the [MKVToolNix](https://mkvtoolnix.download/) program bundle which can be downloaded [here](https://mkvtoolnix.download/downloads.html) as installer or portable. Available in various operating systems including Windows, Linux, and Mac.

If you install MKVToolNix, add its directory to your environment path variable. Else if you download it as portable, just copy the executables `mkvmerge` and `mkvpropedit` in the same directory as the Python scripts.

## Why do I need this?
If you run this script once, you won't ever have to manually select your preferred audio and subtitle tracks for each video in your video player. 
Some video players like VLC Media Player on Android don't support choosing a preferred language for audio and subtitles.

## How does it work?
This program reads all mkv files inside a directory and subdirectories. 
For each mkv file, `mkvmerge` finds what tracks are present. 
We look for four properties: `name`, `number`, `type`, and `language`.

<details>
<summary><h3>Brief overview about track properties</h3></summary>

- `name` is the label assigned to a track, useful for mkv files that provide subtitles for full dialog and for song lyrics only.
- `number` is the index of the track in the mkv file. Usually, video track always comes first at `number = 1`, followed by an audio track, and so on.
- `type` can be one of these: `video`, `audio`, `subtitles`. Naturally, a complete mkv file should contain at least three different tracks.
- `language` tells what the track's language is. For Japanese, `language=jpn` while for English, `language=eng`. 
Some tracks may not have any assigned language like video tracks, thus `lanuage=und` which means undetermined.
</details>

Because we know each track's properties, we can find tracks with `(type=audio and language=jpn)` or `(type=subtitles and language=eng)` and give these tracks a `flag-default=1` assignment. Otherwise, we give unwanted tracks `flag-default=0`.

The program automates the sending of command-line arguments to `mkvpropedit`. Here is an example of a generated command line effortlessly:
```bat
mkvpropedit "Anime S01E01.mkv" \
--edit track:2 --set flag-default=1 --set flag-forced=1 \ 
--edit track:3 --set flag-default=0 --set flag-forced=0 \
--edit track:4 --set flag-default=1 --set flag-forced=1 \
--edit track:5 --set flag-default=0 --set flag-forced=0 \
```
provided that `track:2` is a JPN audio track and `track:4` is full ENG dialogue subtitles track, while `track:3` is an ENG audio track and `track:5` is a song lyrics track. Remember that `track:1` is the video track so there is no need to modify it.

If there is at least one JPN audio track and at least one ENG dialogue subtitles track set to default after this process, then the program returns a `Pass` indicator.
Below is a sample output after a successful processing of an mkv file:
```diff
Anime S01E01.mkv
  Audio tracks:2 Subtitle tracks:2
+ Track:2 Type:aud Language:jap Name:Japanese Dub
# Track:3 Type:aud Language:eng Name:English Dub
+ Track:4 Type:sub Language:eng Name:English Sub
# Track:5 Type:sub Language:jap Name:Japanese Sub
@@ Pass @@
```
The text coloring is handled by the `termcolor` library in Python, so there will be no printed special characters.
## How fast is it?
Aside from that it only switches few flags but not recreate the mkv files entirely, this program utilizes `multiprocessing`. This means that multiple instances of `mkvpropedit` is being run, and that multiple files are being processed concurrently. 

Processing a library of 180 anime episodes takes about **7 seconds** to complete.

Furthermore, not all mkv files have the same number and order of tracks. 
A commandline argument for one mkv file might not work for the other. 
This is why it's important to check the tracks' properties. 
But you don't have to because this program saves you from stopping in between episodes just to change tracks.
