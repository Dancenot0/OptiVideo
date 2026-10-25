import os
import sys

def get_bin_path(name: str):
    """
    Returns the absolute path to the specified executable in the bin directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    executable = f"{name}.exe" if os.name == 'nt' else name
    bin_path = os.path.join(base_dir, 'bin', executable)
    
    if not os.path.exists(bin_path):
        return name # Fallback to system path
    
    return bin_path

def get_ffmpeg_path():
    return get_bin_path('ffmpeg')

def get_ffprobe_path():
    return get_bin_path('ffprobe')
