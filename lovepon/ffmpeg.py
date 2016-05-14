from math import fabs, ceil
from shlex import quote
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
    track_re = re.compile(r'mkvmerge & mkvextract: ([0-9]*)')

    def __init__(self, file):
        self.file = file

        filename = os.path.splitext(os.path.split(self.file)[1])[0]
        self.out_filename = os.path.join(os.getcwd(), filename + '.webm')
        self._temp_dir = tempfile.TemporaryDirectory()
        self._subs_extracted = False

        self.bandwidth = 1
        self.end = None
        self.quiet = True
        self.resolution = ()
        self.sound = False
        self.start = None
        self.subtitles = False
        self.target_filesize = None

    def arguments(self, encode_pass=1):
        """Returns a list of ffmpeg arguments based on the set instance variables.
        """
        arguments = ['ffmpeg', '-y', '-i', self.file]
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

    def encode(self):
        """Performs a two-pass encode. If the class has a specified target
        filesize, performs the encode until either the target filesize has
        been reached or bandwidth changes do not affect filesize.
        """
        kwargs = {
            'cwd': self._temp_dir.name,
            'stderr': subprocess.DEVNULL if self.quiet else None
        }
        old_filesize = 0
        temporary_file = os.path.join(self._temp_dir.name, 'output.webm')
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
            if self.target_filesize:
                if fabs(filesize - old_filesize) < 8 * 1024:
                    click.echo('Bitrate maxed. Stopping.')
                    break
                else:
                    old_filesize = filesize
                if fabs(self.target_filesize - filesize) < 10240:
                    break
                else:
                    self.bandwidth *= self.target_filesize / filesize
            else:
                break
        shutil.move(temporary_file, self.out_filename)
