from pytube import YouTube
from pytube import Playlist
from pytube import exceptions as pytube_exceptions
from tqdm import tqdm
#from gooey import Gooey
import sys
import os
import argparse
from yt_download.config import edit_option, forbidden, default_save_loc


def setup():
    # Parser setup
    parser = argparse.ArgumentParser(epilog="Run without arguments for the GUI (currently not implemented), "
                                            "with arguments for CLI.")

    # -db DATABSE -u USERNAME -p PASSWORD -size 20
    parser.add_argument("url",
                        help="URL for the video or playlist to be converted. Wrap in quotes if it contains special "
                             "characters.")
    parser.add_argument("-f", "--format", default="mp3", help="Desired File Format, either mp3 (default) or mp4")
    parser.add_argument("-d", "--destination", default=default_save_loc,
                        help="Destination directory where the file is to be saved. The default save location may be "
                             "changed in the config file.")
    parser.add_argument("-s", "--save", action="store_true",
                        help="Assumes a playlist link has been provided. The videos are not downloaded. The names of "
                             "all the videos in the playlist are saved to a text file with the name of the playlist.")

    args = parser.parse_args()

    # Name arguments
    ismp4 = False
    link = args.url

    if args.format in ["mp4", "MP4", "Mp4", "mP4"]:
        ismp4 = True
        print("Requested format: mp4")
    elif args.format in ["mp3", "MP3", "Mp3", "mP3"]:
        print("Requested format: mp3")
    else:
        print("Unrecognized file format: ", args.format)
        print("Please input mp3 (default) or mp4.")

    dest = args.destination
    if dest != default_save_loc:
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

    save = args.save

    return link, ismp4, dest, video, save


def download_video(link, ismp4, dest, edit_option=edit_option, already_downloaded=None, newly_downloaded=None):
    if already_downloaded is None:
        already_downloaded = []
    try:
        yt = YouTube(link, on_progress_callback=progress_function)
        vid_title = yt.title
        print("\nDetected video: ", vid_title)

        if vid_title in already_downloaded:
            print("A video with this title has already been downloaded. See history file. Skipping.\n")
            return

        check_chars = check_forbidden_char(vid_title)  # see if there are forbidden chars in title
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
                print("Path: " + str(path))
                stream = yt.streams.filter(only_audio=True).first()
                print("Stream info: " + str(stream))

                print("Downloading...")
                stream.download(dest, filename=title)
                print("Download complete.")

                print("Converting to mp3...")
                print("File size: " + str(stream.filesize / 1000) + " kB")
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


def download_playlist(link, ismp4, dest, save, already_downloaded=None, newly_downloaded=None):
    try:
        pl = Playlist(link)
        links = pl.video_urls
        print("\nDetected playlist: " + str(pl.title) + "\n")

        if save:
            # If in save mode, just save the titles to a text file and exit
            save_titles(links, write_loc="./" + str(pl.title) + ".txt")
        else:
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
        print("Video or playlist unavailable. Maybe try a different source url. Proceeding to next.")


def save_titles(links, write_loc):
    with open(write_loc, "a+") as f:
        print("Opened file: " + write_loc)
        for link in links:
            try:
                yt = YouTube(link, on_progress_callback=progress_function)
                print("Found video: " + yt.title)
                for line in f:
                    if yt.title in line:
                        print("Video already in file. Skipping.")
                        break
                else:
                    f.write(yt.title + "\n")
                    print("Wrote: " + yt.title)
            except pytube_exceptions.VideoUnavailable or EOFError:
                print("Video Unavailable. Maybe try a different url.")


def isascii(c):
    """Check if char is an ascii char"""
    return len(c) == len(c.encode())


def check_forbidden_char(string):
    culprits = []
    for char in forbidden:
        if char in string:
            culprits.append(char)
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
    current = ((filesize - bytes_remaining) / filesize)
    percent = ('{0:.1f}').format(current * 100)
    progress = int(50 * current)
    status = '█' * progress + '-' * (50 - progress)
    sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
    sys.stdout.flush()


# Check if there are arguments - if not, use GUI
# if len(sys.argv) >= 2:  # if there are any args
#     if not '--ignore-gooey' in sys.argv:
#         sys.argv.append("--ignore-gooey")


# @Gooey(
#     program_name="yt-download",
#     program_description="A simple pytube wrapper for simple youtube video downloads as mp3 and mp4.",
# )
def main():
    link, ismp4, dest, video, save = setup()

    # Check history
    """ NOTE: Currently treats files as duplicates regardless of file types."""
    """ NOTE: Currently there's only one history file, so you can only have a
    given song in one playlist. I need to change this."""

    already_downloaded = []
    newly_downloaded = []

    if video:
        download_video(link, ismp4, dest, edit_option, [], [])
    else:
        download_playlist(link, ismp4, dest, save, [], [])
    # update_history(newly_downloaded)
    end_message(ismp4)


# Run
if __name__ == "__main__":
    main()
