from pytube import YouTube

#C:\Users\lmart\Projects\youtube_downloader
def download_video(link, dest=None, edit_option=True):
    yt = YouTube(link)
    vid_title = yt.title
    print("\nDetected video: ", vid_title)

    #if vid_title in already_downloaded:
    #    print("A video with this title has already been downloaded. See history file. Skipping.\n")
    #    return

    #if not mp4:
    
    stream = yt.streams.filter(only_audio=True).first()

    #check_chars = check_forbidden_char(vid_title)
    check_chars = [0, 1]
    title = vid_title

    if edit_option:
        if len(check_chars) > 0:
            print("WARNING: This title contains a forbidden character: ", check_chars)
            print("If you don't edit it, the forbidden characters will be removed.\n")

        edit = str(input("Would you like to edit this title? y/n    "))
        print("Found: ", edit)
        while edit not in ["y", "n", "Y", "N", "yes", "no"]:
            edit = str(input("Please enter y/n    "))

        if edit in ["y", "Y", "yes"]:
            title = str(input("New Title:  "))
            
test_link = 'https://www.youtube.com/watch?v=V4YsfDD2l3Y&list=PL47a1Ou5h81Ph3JrI7TIcJljA_N4nCX1s&ab_channel=Cevan2'            
download_video(test_link)