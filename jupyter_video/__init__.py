from ._version import version_info, __version__

# from .video import *
# __all__ = ['Video']

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter_video',
        'require': 'jupyter_video/extension'
    }]
