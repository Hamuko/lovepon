from setuptools import find_packages, setup
import os
import re
import subprocess


script_path = os.path.dirname(os.path.realpath(__file__))
re_version = r'v([0-9\.]*-?[0-9]*)?'
COMMAND_DESCRIBE_VERSION = ['git', 'describe', '--tags']
SUBPROCESS_KWARGS = {
    'cwd': script_path,
    'stdout': subprocess.PIPE,
    'stderr': subprocess.PIPE
}


def get_setup_version():
    """Return a version string that can be used with the setup method. Includes
    additional commits since the last tagged commit.
    """
    return '0.1'
    if os.path.isdir('.git'):
        process = subprocess.Popen(COMMAND_DESCRIBE_VERSION,
                                   **SUBPROCESS_KWARGS)
        process.wait()
        version = process.communicate()[0].decode("utf-8").strip()
        return re.match(re_version, version).group(1)
    else:
        return '0.1'


setup(
    name='lovepon',
    version=get_setup_version(),
    description='Perfectly executed WebMs.',
    url='https://github.com/Hamuko/lovepon',
    author='Hamuko',
    author_email='hamuko@burakku.com',
    license='Apache2',
    packages=find_packages(),
    install_requires=['Click'],
    entry_points={
        'console_scripts': ['lovepon=lovepon.lovepon:cli'],
    }
)
