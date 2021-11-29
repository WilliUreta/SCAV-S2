# SCAV-S2
Repo to deliver the second seminar of the SCAV subject


## Explanation

The s2_main.py file has a set of simple functions that will execute some ffmpeg commands. It can be run as:
```
python3 p2_main.py
```

The functions are the following:
1. Show the Macroblocks and motion vectors of the video.
2. Repackage any video with a sound stream with 2 audio streams. First a aac-coded with low bitrate, and an mp3.
3. Know in which International Broadcasting Standards does a specific video fit. DVB, ISDB, ATSC or DTMB.
4. Embed into the video user provided subtitles. Open caption an srt file.

# Dependencies
You will need to have the some python packages installed: 
- subprocess 
- requests
