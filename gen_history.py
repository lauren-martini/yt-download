from pytube import Playlist
from pytube import YouTube
from pytube import exceptions as pytube_exceptions
from tqdm import tqdm

""" For manually generating history if not done automatically. """

pl = Playlist("https://www.youtube.com/playlist?list=PL5u9rXq186GUzfr3O64K25hDOnqQ3dmEd")
video_links = pl.video_urls

filename = "history.txt"
unavailable = "unavailable.txt"

with open(filename, 'a') as file:
    with open(unavailable, 'a') as u_file:
        for link in tqdm(video_links):
            try:
                yt = YouTube(link)
                title = yt.title
                file.write(title)
                file.write("\n")
            except pytube_exceptions.VideoUnavailable:
                print("video unavailable: ", title)
                u_file.write(title + "\n")
