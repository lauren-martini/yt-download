from pytube import YouTube

#url = "https://www.youtube.com/playlist?list=PLocQeghkorOWXJ3tu8YwNfbwjxTJ2UZWV"

url = "https://www.youtube.com/watch?v=osRSZaCswds&list=PLocQeghkorOWXJ3tu8YwNfbwjxTJ2UZWV&index=6&t=0s"

for i in range(0, 50):
    yt = None
    yt = YouTube(url)
    print(i)

exit()
