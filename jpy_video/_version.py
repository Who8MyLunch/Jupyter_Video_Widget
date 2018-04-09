
import json
import os



def parse_version(version_info):
    N = len(version_info)

    tpl3 = '{:d}.{:d}.{:d}'
    tpl4 = '{:d}.{:d}.{:d}-{:s}'

    if N > 3:
        if not version_info[3]:
            N = 3

    if N < 3:
        raise ValueError('Expected at least three terms in "version_info": {}'.format(N))
    if N == 3:
        version = tpl3.format(version_info[0], version_info[1], version_info[2])
    elif N > 3:
        version = tpl4.format(version_info[0], version_info[1], version_info[2], version_info[3])

    return version

#------------------------------------------------
#------------------------------------------------

version_info = (0, 4, 0, 'dev.1')

__version__ = parse_version(version_info)

__npm_module_version__ = __version__   # Make sure package.json contains exactly the same version number
__npm_module_name__ = 'jupyter-video'
