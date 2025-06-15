from setuptools import setup, find_packages

setup(
    name="tts",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fire",
        "soundfile",
        "sounddevice",
        "kokoro",  # make sure this is the correct package name
        "chatterbox-tts",  # add Chatterbox TTS support
        "markdown",
        "beautifulsoup4",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "tts=tts.cli:main",
        ],
    },
    python_requires=">=3.11",
    author="Your Name",
    author_email="your.email@example.com",
    description="TTS command line tool supporting Kokoro and Chatterbox engines",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or your chosen license
        "Operating System :: OS Independent",
    ],
)