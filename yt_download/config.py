# Where files are saved if no destination is given
#default_save_loc = "./tmp"
default_save_loc = "./tmp"

# Characters not allowed to be in filenames, either due to Windows
# or ffmpeg
forbidden = ["\\", '/', ':', '\"', '*', '|', '<', '>', 
              '~', '`', '\'', '!', "#", "@", "$", "^",
              ',', '(', ')', '&', '.'] 
              
# History file - contains the names of videos that have already been 
# downloaded. Should be in the same directory as download_youtube.py
history_path = "../history.txt"

# Edit option - would you like the downloader to ask if you want to edit
# the title every time? If false, automatic edits will be applied for
# forbidden characters.
edit_option = False
