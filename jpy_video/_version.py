
import json
import os

#------------------------------------------------
# Helper functions
def read_json(fname):
    """Read JSON-serialized data from file
    """
    with open(fname, 'r') as fp:
        info = json.load(fp)

    return info



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

# Python version
version_info = (0, 4, 0, 'dev.0')

__version__ = parse_version(version_info)

# NPM version pulled directly from package.json
p = os.path.realpath(os.path.dirname(__file__))
f = os.path.join(p, '..', 'js', 'package.json')
data = read_json(f)

__npm_module_version__ = data['version']
__npm_module_name__ = data['name']
