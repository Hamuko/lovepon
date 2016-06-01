from math import fabs, ceil
from shlex import quote
from datetime import timedelta
import os
import re
import shutil
import subprocess
import tempfile
import click


class FFmpeg(object):
    """Class used for video conversions to WebM. Uses the instance variables to
    generate ffmpeg arguments to run and matches the output video to specified
    parameters.
    """
    duration_re = re.compile(r'Duration: ([0-9:\.]*),')

    def __init__(self, file):
        self.file = file

        filename = os.path.splitext(os.path.split(self.file)[1])[0]
        self.out_filename = os.path.join(os.getcwd(), filename + '.webm')
        self._temp_dir = tempfile.TemporaryDirectory()
        self._subs_extracted = False

        self.bandwidth = None
        self.end = None
        self.quiet = True
        self.resolution = ()
        self.sound = False
        self.start = None
        self.subtitles = False
        self.target_filesize = None
        self.title = None

    def arguments(self, encode_pass=1):
        """Returns a list of ffmpeg arguments based on the set instance variables.
        """
        arguments = ['ffmpeg', '-y', '-i', self.file]
        if self.title:
            arguments += ['-metadata', 'title={}'.format(self.title)]
        if self.subtitles:
            arguments += ['-copyts',
                          '-vf', 'subtitles={},setpts=PTS-STARTPTS'
                          .format(quote(self.file))]
        arguments += ['-sn']
        if self.start:
            arguments += ['-ss', self.start]
        if self.end:
            arguments += ['-to', self.end]
        if self.resolution:
            arguments += ['-s', 'x'.join([str(x) for x in self.resolution])]
        arguments += ['-c:v', 'libvpx']
        if self.sound:
            arguments += ['-c:a', 'libvorbis', '-q:a', '4']
        if self.bandwidth:
            arguments += ['-b:v', str(self.bandwidth) + 'M']
        arguments += ['-pass', str(encode_pass)]
        if not self.sound:
            arguments += ['-an']
        arguments += ['output.webm']
        return arguments

    def default_bitrate(self):
        """Calculates a bitrate to start the encoding process based on the
        target filesize and the length of the output video. The following
        formula is used to calculate the bitrate (Mb/s):
        target size (kB) / video duration (s) / 1024^2 * 8
        """
        seconds = self.duration.total_seconds()
        return self.target_filesize / seconds / 1048576 * 8

    @property
    def duration(self):
        """Return the duration as a timedelta object."""
        if self.start:
            start = self.string_to_timedelta(self.start)
        else:
            start = timedelta(0)
        if self.end:
            end = self.string_to_timedelta(self.end)
        else:
            end = self.string_to_timedelta(self.video_duration)
        return end - start

    @duration.setter
    def duration(self, value):
        """Set the end point for the video based on the start time and duration.
        """
        if self.start:
            start = self.string_to_timedelta(self.start)
        else:
            start = timedelta(0)
        duration = self.string_to_timedelta(value)
        self.end = self.timedelta_to_string(start + duration)

    def encode(self):
        """Performs a two-pass encode. If the class has a specified target
        filesize, performs the encode until either the target filesize has
        been reached or bandwidth changes do not affect filesize.
        """
        kwargs = {
            'cwd': self._temp_dir.name,
            'stderr': subprocess.DEVNULL if self.quiet else None
        }
        old_bitrate = 0
        old_filesize = 0
        temporary_file = os.path.join(self._temp_dir.name, 'output.webm')
        if not self.bandwidth:
            self.bandwidth = self.default_bitrate()
        while True:
            click.echo("Encoding video at {}M."
                       .format(ceil(self.bandwidth * 100) / 100))
            args = self.arguments()
            process = subprocess.Popen(args, **kwargs)
            process.wait()
            args = self.arguments(encode_pass=2)
            process = subprocess.Popen(args, **kwargs)
            process.wait()

            filesize = os.stat(temporary_file).st_size
            click.echo("Encoded video is {} kB."
                       .format(ceil(filesize / 1024)))

            if not self.target_filesize:
                # Stop encoding: bitrate mode used.
                break
            if fabs(self.target_filesize - filesize) < 10240:
                # Stop encoding: File within 10 kB.
                break
            if fabs(filesize - old_filesize) < 8 * 1024:
                click.echo('Bitrate maxed. Stopping.')
                break
            if old_bitrate and old_filesize:
                delta_filesize = filesize - old_filesize
                delta_bitrate = self.bandwidth - old_bitrate
                d = delta_filesize / delta_bitrate
                add_bitrate = -3 * pow(min(d / 300000, 1), 0.25) + 3
            else:
                add_bitrate = 0

            old_bitrate = self.bandwidth
            old_filesize = filesize
            self.bandwidth *= self.target_filesize / filesize + add_bitrate
        shutil.move(temporary_file, self.out_filename)

    def string_to_timedelta(self, time):
        """Converts a timestamp used by FFmpeg to a Python timedelta object."""
        parts = time.split(':')
        try:
            seconds = int(parts[-1].split('.')[0])
        except (IndexError, ValueError):
            seconds, milliseconds = 0, 0
        try:
            milliseconds = int(parts[-1].split('.')[1])
        except (IndexError, ValueError):
            milliseconds = 0
        try:
            minutes = int(parts[-2])
        except (IndexError, ValueError):
            minutes = 0
        try:
            hours = int(parts[-3])
        except (IndexError, ValueError):
            hours = 0
        return timedelta(hours=hours, minutes=minutes,
                         seconds=seconds, milliseconds=milliseconds)

    def timedelta_to_string(self, delta):
        """Converts a timedelta object to a FFmpeg compatible string."""
        hours = delta.seconds // 3600
        minutes = delta.seconds % 3600 // 60
        seconds = delta.seconds % 60
        milliseconds = delta.microseconds // 1000
        return '{}:{}:{}.{}'.format(hours, minutes, seconds, milliseconds)

    @property
    def video_duration(self):
        args = ['ffmpeg', '-i', self.file]
        process = subprocess.Popen(args, stderr=subprocess.PIPE)
        process.wait()
        for line in process.stderr:
            linestr = str(line)
            if ' Duration: ' in linestr:
                return re.search(FFmpeg.duration_re, linestr).group(1)
