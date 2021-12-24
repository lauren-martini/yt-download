from setuptools import setup

setup(
        name="yt-downloader",
        version="0.1.0",
        packages=["yt-downloader"],
        install_requires=[
            'python_version >= 3',
            'pytube',
            'tqdm',
            'ffmpeg',
        ],
)
