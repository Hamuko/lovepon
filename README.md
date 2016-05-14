# lovepon

Perfectly executed WebMs.

## Requirements

lovepon most likely requires Python 3, since I have not bothered to test it with Python 2. Also, as a wrapper for [ffmpeg](https://ffmpeg.org/), it does require ffmpeg and prefarably to be built with the libraries that make it possible to encode VP8 video and Vorbis audio. Burning subtitles onto the videos requires ffmpeg support for subtitle rendering, like building ffmpeg against [libass](https://github.com/libass/libass).

## Installation

Use pip to install the git master.

    pip install git+https://github.com/Hamuko/lovepon

## Usage

Use `lovepon --help` to print the following helpful message.

    Usage: lovepon [OPTIONS] FILE

      Command-line wrapper for ffmpeg designed to ease converting video files to
      WebM files.

    Options:
      -b, --bandwidth TEXT     Manually set the used bandwidth, e.g. 5M.
      -e, --end TEXT           End time for the encode, e.g. 01:12:34.555.
      --resolution INTEGER...  Output video width and height in pixels.
      --sound / --no-sound     Output video with sound.
      -s, --start TEXT         Start time for the encode, e.g. 01:09.100.
      --subs / --no-subs       Output video with subtitles.
      -t, --target-size TEXT   Target filesize for the encode.
      --verbose                Turn on ffmpeg output.
      --help                   Show this message and exit.

### Target filesize options

You can either specify a size numerically (`1G`, `1M`, `1K`, `1B`) or use `4ch` to shit out something that you can upload to [4chan](https://www.4chan.org/).
