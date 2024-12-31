import click
from .ffmpeg import FFmpeg


def parse_bandwidth(bandwidth):
    """Converts the bandwidth string (e.g. 5M) to a float representing megabits."""
    if bandwidth[-1].lower() == "m":
        return int(bandwidth[:-1])
    elif bandwidth[-1].lower() == "k":
        return int(bandwidth[:-1]) / 1024


def parse_filesize(filesize):
    """Turn the filesize input string (e.g. 5M) into an integer representing bytes."""
    if filesize.lower() == "4ch":
        return 4183040
    elif filesize[-1].lower() == "g":
        exponent = 3
    elif filesize[-1].lower() == "m":
        exponent = 2
    elif filesize[-1].lower() == "k":
        exponent = 1
    elif filesize[-1].lower() == "b":
        exponent = 0
    else:
        click.echo("Invalid filesize.")
        exit(1)
    return int(filesize[:-1]) * pow(1024, exponent)


@click.command()
@click.option("--bandwidth", "-b", help="Manually set the used bandwidth, e.g. 5M.")
@click.option("--crop/--no-crop", default=False, help="Crop the output video frame.")
@click.option("--crop-width", type=int, help="Width of the cropped area in pixels.")
@click.option("--crop-height", type=int, help="Height of the cropped area in pixels.")
@click.option("--crop-x", type=int, help="Staring X coordinate for the crop.")
@click.option("--crop-y", type=int, help="Staring Y coordinate for the crop.")
@click.option("--duration", help="Duration for the output video, e.g. 30.000")
@click.option("--end", "-e", help="End time for the encode, e.g. 01:12:34.555.")
@click.option("--h264", is_flag=True, help="Use h.264 encoding instead of VP8.")
@click.option("--iterations", type=int, help="Maximum iterations for target filesize.")
@click.option("--output", "-o", help="Output filename")
@click.option(
    "--resolution", nargs=2, type=int, help="Output video width and height in pixels."
)
@click.option("--sound/--no-sound", default=False, help="Output video with sound.")
@click.option("--start", "-s", help="Start time for the encode, e.g. 01:09.100.")
@click.option("--subs/--no-subs", default=False, help="Output video with subtitles.")
@click.option("--target-size", "-t", help="Target filesize for the encode.")
@click.option("--title", help="Add a title to file metadata.")
@click.option("--verbose", is_flag=True, help="Turn on ffmpeg output.")
@click.option("--vp9", is_flag=True, help="Use VP9 encoding instead of VP8.")
@click.argument(
    "file", required=True, nargs=1, type=click.Path(exists=True, resolve_path=True)
)
def cli(
    bandwidth,
    crop,
    crop_width,
    crop_height,
    crop_x,
    crop_y,
    duration,
    end,
    h264,
    iterations,
    output,
    resolution,
    sound,
    start,
    subs,
    target_size,
    title,
    verbose,
    vp9,
    file,
):
    """Command-line wrapper for ffmpeg designed to ease converting video files
    to WebM files.
    """
    conversion = FFmpeg(file)
    conversion.start = start
    conversion.end = end
    conversion.h264 = h264
    conversion.vp9 = vp9
    conversion.iterations = iterations
    conversion.output = output

    if crop:
        from .cropper import VideoCropper

        cropper = VideoCropper(conversion)
        cropper.mainloop()
    if all(x is not None for x in (crop_width, crop_height, crop_x, crop_y)):
        conversion.coordinates = (
            crop_x,
            crop_y,
            crop_x + crop_width,
            crop_y + crop_height,
        )
    if duration:
        conversion.duration = duration
    if bandwidth:
        conversion.bandwidth = parse_bandwidth(bandwidth)
    if target_size:
        conversion.target_filesize = parse_filesize(target_size)

    conversion.quiet = not verbose
    conversion.resolution = resolution
    conversion.sound = sound
    conversion.subtitles = subs
    conversion.title = title
    conversion.encode()


if __name__ == "__main__":
    cli()
