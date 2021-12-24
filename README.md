# yt-download
A wrapper for pytube that simplifies the process of downloading YouTube videos and whole playlists as mp3 and mp4 files. The user may provide either a video or playlist link, the desired file format, and a destination directory. Forbidden video-title characters are detected and removed when downloading. Uses ffmpeg and displays progress with tqdm.

Run as a python script with command-line arguments. Some options are configurable via config.py.
