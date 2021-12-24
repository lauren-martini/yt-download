from setuptools import setup

setup(
        name="yt-downloader",
        version="0.1.0",
        packages=["yt-downloader"],
        license="MIT",
        description="A wrapper for pytube3 that makes it easier to download videos and playlists as mp3 or mp4.",
        url="https://github.com/lauren-martini/yt-downloader",
        install_requires=[
            'python_version >= 3',
            'pytube3',
            'tqdm',
            'ffmpeg',
        ],
)
