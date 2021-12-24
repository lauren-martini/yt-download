from pytube import YouTube
from pytube import Playlist
from pytube import exceptions as pytube_exceptions
from tqdm import tqdm
import sys
import os
import argparse
import yt_download.config as cfg


def setup():
    # Parser setup
    parser = argparse.ArgumentParser(epilog="")

    #-db DATABSE -u USERNAME -p PASSWORD -size 20
    parser.add_argument("url", help="URL for the video or playlist to be converted. Wrap in quotes if it contains special characters.")
    parser.add_argument("-f", "--format", default="mp3", help="Desired File Format, either mp3 (default) or mp4")
    parser.add_argument("-d", "--destination", default=cfg.default_save_loc, help="Destination directory where the file is to be saved. The default save location may be changed in the config file.")

    args = parser.parse_args()

    # Name arguments
    link = args.url

    if args.format in ["mp4", "MP4", "Mp4", "mP4"]: 
        ismp4 = True
        print("Requested format: mp4")
    elif args.format in ["mp3", "MP3", "Mp3", "mP3"]:
        ismp4 = False
        print("Requested format: mp3")
    else:
        print("Unrecognized file format: ", args.format)
        print("Please input mp3 (default) or mp4.")

    dest = args.destination
    if dest != cfg.default_save_loc:
        print("\nDestination path: ", dest)
        if not os.path.exists(dest):
            os.mkdir(dest)
            print("Directory not found. Created directory.")
    else:
        print("\nNo save location specified.")
        print("Saving to: " + dest)
        
    # Check if video or playlist
    video = False
    if link.find("/playlist?list=") == -1:
        video = True

    return link, ismp4, dest, video

        
def download_video(link, ismp4, dest, edit_option=cfg.edit_option, already_downloaded=[], newly_downloaded=[]):
    try:
        yt = YouTube(link, on_progress_callback=progress_function)
        vid_title = yt.title
        print("\nDetected video: ", vid_title)

        if vid_title in already_downloaded:
            print("A video with this title has already been downloaded. See history file. Skipping.\n")
            return
            
        check_chars = check_forbidden_char(vid_title) # see if there are forbidden chars in title
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
            if len(check_chars) > 0:
                print("Forbidden characters detected. Removing.")
                title = remove_forbidden_chars(title)
                print("Auto-edited title: " + title)
             
        path = os.path.join(dest, title)
        
        # Requested mp3 download:
        if not ismp4:
            if not os.path.exists(path + ".mp3"):
                stream = yt.streams.filter(only_audio=True).first()
                print("Stream info: " + str(stream))
                
                print("Downloading...")
                stream.download(dest, filename=title)
                print("Download complete.")
                
                print("Converting to mp3...")
                print("File size: " + str(stream.filesize/1000) + " kB") 
                input_file = "%s.mp4"
                input_format = "%s.3gpp"
                os.system("ffmpeg -stats -hide_banner -loglevel fatal -i \"%s\" \"%s.mp3\"" % (path, path))
                os.system("rm \"%s\"" % path)
                print("Done! \n")
                newly_downloaded.append(vid_title)
                
            else:
                print("File already exists. Continuing...\n")
            
        # Requested mp4 download:
        else:
            if not os.path.exists(path + ".mp4"):
                stream = yt.streams.filter(file_extension="mp4").first()
                print("Stream info: " + str(stream))
                
                print("Downloading...")
                stream.download(dest)
                print("Download complete.")
                newly_downloaded.append(vid_title)
                
            else:
                print("File already exists. Continuing...\n")
                
    except pytube_exceptions.VideoUnavailable or EOFError:
        print("Video Unavailable. Maybe try a different url.")


def download_playlist(link, ismp4, dest, already_downloaded=[], newly_downloaded=[]):
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
            download_video(vid_link, ismp4, dest, edit_all, already_downloaded, newly_downloaded)
        
        if not ismp4:
            clean_up_extra_mp4s(dest)
            
    except pytube_exceptions.VideoUnavailable:
        print("Video Unavailable. Maybe try a different source url. Proceeding to next.")


def isascii(c):
    """Check if char is an ascii char"""
    return len(c) == len(c.encode())


def check_forbidden_char(string):
    culprits = []
    for char in cfg.forbidden:
        if char in string:
            culprits.append(char)
    if not isascii(string):
        print("Non-ascii characters detected. Removing.")
        culprits.append("nonascii char")
    return culprits


def remove_forbidden_chars(string):
    for char in string:
        if char in cfg.forbidden:
            string = string.replace(char, "")
        if not isascii(char):
            string = string.replace(char, "")
    if string.endswith('.'):
        string = string[:-1]
    return string

    
def clean_up_extra_mp4s(dest):
    """If mp4 --> mp3 conversion occurred, find and remove unwanted mp4s"""
    for filename in os.listdir(dest):
        if filename.endswith(".mp4"):
            print("\nDetected missed mp4s.")
            print("Converting any missed mp4s to mp3.")
            targets = os.path.join(dest, "*.mp4")
            os.system("for f in " + targets + "; do ffmpeg -loglevel error -i \"$f\" \"${f%.*}.mp3\"; done")
            print("Conversion complete. Removing leftover mp4 files.\n")
            os.system("rm " + targets)
            break


def update_history(newly_downloaded):
    print(newly_downloaded)


def end_message(ismp4):
    """Message displayed after download and conversion are complete."""
    if ismp4:
        print("\n ~~~~~ DONE! Happy watching! :) ~~~~~ \n")
    else:
        print("\n ~~~~~ DONE! Happy listening! :) ~~~~~ \n")


def progress_function(stream, chunk, bytes_remaining):
    """Monitor download progress and display as a progress bar."""
    filesize = stream.filesize
    current = ((filesize - bytes_remaining)/filesize)
    percent = ('{0:.1f}').format(current*100)
    progress = int(50*current)
    status = '█' * progress + '-' * (50 - progress)
    sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
    sys.stdout.flush()


def main():
    link, ismp4, dest, video = setup()
    
    # Check history
    """ NOTE: Currently treats files as duplicates regardless of file types."""
    """ NOTE: Currently there's only one history file, so you can only have a
    given song in one playlist. I need to change this."""

    already_downloaded = []
    newly_downloaded = []

    if video:
        download_video(link, ismp4, dest, cfg.edit_option, [], [])
    else:
        download_playlist(link, ismp4, dest, [], [])
    #update_history(newly_downloaded)
    end_message(ismp4)


# Run
if __name__ == "__main__":
    main()
