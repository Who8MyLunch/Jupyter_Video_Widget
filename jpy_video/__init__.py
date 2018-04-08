from ._version import version_info, __version__

from .video import *

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-video',
        'require': 'jupyter-video/extension'
    }]
