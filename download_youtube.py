#! /usr/bin/python3
from pytube import YouTube
from pytube import Playlist
from pytube import exceptions as pytube_exceptions
from tqdm import tqdm
import sys
import os
import yd_config as cfg

forbidden = cfg.forbidden # Load forbidden filename characters

usage = "youtube_downloader link_to_vid_or_playlist [format (default=mp3, mp4)] [destination]\nBe use to wrap the link in quotes!"

# Check No. Arguments
if len(sys.argv) == 1: # no arguments passed
    print(usage)
    print("Pass the link to a youtube video to download the video to this folder.")
    print("Otherwise, pass a playlist link to download the entire playlist.")
    print("Downloading as mp3 requires ffmpeg.")
    sys.exit()

if len(sys.argv) > 4:
    print(usage)
    print("Too many args.")
    sys.exit()

# Name arguments
link = str(sys.argv[1])

mp4 = False
if len(sys.argv) >= 3:
    format = str(sys.argv[2])
    if format == "mp4":
        mp4 = True
        print("Requested format: mp4")

dest = cfg.default_save_loc
if len(sys.argv) == 4:
    dest = str(sys.argv[3])
    print("\nDestination path: ", dest)
    if not os.path.exists(dest):
        os.mkdir(dest)
        print("Created directory.")
    else:
        print("Directory already exists.")
else:
    print("\nNo save location specified.")
    print("Saving to: " + dest)
    
# Check if video or playlist
video = False
if link.find("/playlist?list=") == -1:
    video = True

# Check history
""" NOTE: Currently treats files as duplicates regardless of file types."""
""" NOTE: Currently there's only one history file, so you can only have a
given song in one playlist. I need to change this."""

already_downloaded = []
newly_downloaded = []
# try:
    # with open(cfg.history_file, 'r') as history:
        # for line in history:
            # already_downloaded.append(line[:-1]) # ignore newline
# except (FileNotFoundError, IOError) as e:
    # print(e)
    # print("\nWARNING: history file not found or could not be accessed.")
    # check = input("Continue? y/n    ")
    # if check not in ["y", "n", "Y", "N", "yes", "no"]:
        # check = str(input("Please enter y/n    "))
    # if check not in ["y", "Y", "yes"]:
        # sys.exit()
        
def download_video(link, dest=None, edit_option=True):
    try:
        yt = YouTube(link, on_progress_callback=progress_function)
        vid_title = yt.title
        print("\nDetected video: ", vid_title)

        if vid_title in already_downloaded:
            print("A video with this title has already been downloaded. See history file. Skipping.\n")
            return
        
        if not mp4:
            stream = yt.streams.filter(only_audio=True).first()

            check_chars = check_forbidden_char(vid_title)
            title = vid_title
            
            if edit_option:
                if len(check_chars) > 0:
                    print("WARNING: This title contains a forbidden character: ", check_chars)
                    print("If you don't edit it, the forbidden characters will be removed.\n")
                    
                edit = str(input("Would you like to edit this title? y/n    "))
                
                while edit not in ["y", "n", "Y", "N", "yes", "no"]:
                    edit = str(input("Please enter y/n    "))
                
                if edit in ["y", "Y", "yes"]:
                    title = str(input("New Title:  "))
                else:
                    title = remove_forbidden_chars(title)
                    print("Edited title: " + title)
            else: 
                if check_chars is not None:
                    print("Forbidden characters detected. Removing.")
                    title = remove_forbidden_chars(title)
                    print("Auto-edited title: " + title)
                 
            path = os.path.join(dest, title)
            
            if not os.path.exists(path + ".mp3"):
                print("Downloading...")
                stream.download(dest, filename=title)
                print("Download complete.")
                
                print("Converting to mp3...")
                print("File size: " + str(stream.filesize/1000) + " kB") 
                input_file = "%s.mp4"
                input_format = "%s.3gpp"
                os.system("ffmpeg -stats -hide_banner -loglevel error -i \"%s\" \"%s.mp3\"" % (path, path))
                os.system("rm \"%s\"" % path)
                print("Done! \n")
                newly_downloaded.append(vid_title)
                
            else:
                print("File already exists. Continuing...\n")
            
        else:
  
            print("Downloading...")
            yt.streams.first().download(dest)
            print("Download complete.")
            newly_downloaded.append(vid_title)
        
    except pytube_exceptions.VideoUnavailable or EOFError:
        print("Video Unavailable.")
    
def download_playlist(link, dest=None):
    try:
        pl = Playlist(link)
        #pl.populate_video_urls() # gen list of video links
        links = pl.video_urls
        print("\nDetected playlist: " + str(pl.title) + "\n")
        
        print("Would you like the option to edit the title of each video before it is downloaded? y/n")
        print("Note that titles with forbidden characters will automatically have them removed if you select no.")
        edit_all = str(input("\n"))
        while edit_all not in ["y", "n", "Y", "N", "yes", "no"]:
            print("Please enter y/n")
            edit_all = str(input())
                
        edit_all = True if edit_all in ["y", "Y", "yes"] else False
        for vid_link in tqdm(links):
            download_video(vid_link, dest, edit_all)
        
        if not mp4:
            clean_up_extra_mp4s(dest)
            
    except pytube_exceptions.VideoUnavailable:
        print("Video Unavailable. Proceeding to next.")
        

isascii = lambda s: len(s) == len(s.encode())

def check_forbidden_char(string):
    culprits = []
    for char in forbidden:
        if char in string:
            culprits.append(forbidden)
    if not isascii(string):
        print("Non-ascii characters detected. Removing.")
        culprits.append("nonascii char")
    return culprits
    
def remove_forbidden_chars(string):
    for char in string:
        if char in forbidden:
            string = string.replace(char, "")
        if not isascii(char):
            string = string.replace(char, "")
    if string.endswith('.'):
        string = string[:-1]
    return string
    
def clean_up_extra_mp4s(dest):
    for filename in os.listdir(dest):
        if filename.endswith(".mp4"):
            print("\nDetected missed mp4s.")
            print("Converting any missed mp4s to mp3.")
            targets = os.path.join(dest, "*.mp4")
            os.system("for f in " + targets + "; do ffmpeg -loglevel error -i \"$f\" \"${f%.*}.mp3\"; done")
            print("Conversion complete. Removing leftover mp4 files.\n")
            os.system("rm " + targets)
            break

def update_history():
    print(newly_downloaded)
    # print("\nUpdating history file.")
    # with open(cfg.history_file, 'a') as history:
        # for title in newly_downloaded:
            # history.write(title + "\n")

def end_message():
    if mp4:
        print("\n ~~~~~ DONE! Happy watching! :) ~~~~~ \n")
    else:
        print("\n ~~~~~ DONE! Happy listening! :) ~~~~~ \n")

def progress_function(stream, chunk, bytes_remaining):
    filesize = stream.filesize
    current = ((filesize - bytes_remaining)/filesize)
    percent = ('{0:.1f}').format(current*100)
    progress = int(50*current)
    status = '█' * progress + '-' * (50 - progress)
    sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
    sys.stdout.flush()

# Run
if video:
    download_video(link, dest)
    update_history()
    end_message()
else:
    download_playlist(link, dest)
    update_history()
    end_message()
