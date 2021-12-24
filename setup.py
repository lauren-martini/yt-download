from setuptools import setup

setup(
        name="yt-download",
        version="0.1.1",
        packages=["yt_download"], # containing folder for yt_downloader.py
        license="MIT",
        description="A wrapper for pytube3 that makes it easier to download videos and playlists as mp3 or mp4.",
        url="https://github.com/lauren-martini/yt-download",
        py_modules=['yt_download/yt_download', 'yt_download/config'], # module is yt_download.py
        author="lauren-martini",
        author_email="lmartini@cs.washington.edu",
        install_requires=[
            'pytube==11.0.2',
            'tqdm',
            'ffmpeg',
        ],
        entry_points={
            'console_scripts': [
                'yt-download = yt_download.yt_download:main',
            ],
        },
        #include_package_data=True,
        #package_data={'yt_download': ['yt_download/config.py']},
        #data_files = [(
        #    '/usr/local/etc', ['yt_download/config.py']
        #    )
        #],
)
