import subprocess
import os
import json
from PyQt6.QtCore import QThread, pyqtSignal
from utils.paths import get_ffmpeg_path, get_ffprobe_path

class OptimizationEngine(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_path: str, output_path: str, codec: str, crf: int):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.codec = codec
        self.crf = crf
        self.ffmpeg_path = get_ffmpeg_path()
        self.ffprobe_path = get_ffprobe_path()

    def has_video(self) -> bool:
        """Checks if the input file contains a video stream."""
        try:
            cmd = [
                self.ffprobe_path, '-v', 'error', 
                '-select_streams', 'v:0', 
                '-show_entries', 'stream=codec_type', 
                '-of', 'json', self.input_path
            ]
            result = subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            data = json.loads(result)
            return len(data.get('streams', [])) > 0
        except:
            return False

    def run(self):
        try:
            is_video = self.has_video()
            is_output_audio = self.output_path.lower().endswith(('.mp3', '.wav', '.m4a'))
            
            command = [self.ffmpeg_path, '-i', self.input_path]

            if is_video and not is_output_audio:
                command += [
                    '-vcodec', self.codec,
                    '-crf', str(self.crf),
                    '-preset', 'medium'
                ]
            elif is_video and is_output_audio:
                self.log.emit("Extracting audio from video file...")
                command += ['-vn'] # Disable video for audio-only output
            else:
                self.log.emit("Audio-only processing.")

            # Audio settings based on format
            if self.output_path.lower().endswith('.mp3'):
                command += ['-acodec', 'libmp3lame', '-q:a', '2'] # High quality VBR MP3
            elif self.output_path.lower().endswith('.wav'):
                command += ['-acodec', 'pcm_s16le'] # Lossless WAV
            else:
                command += ['-acodec', 'aac', '-b:a', '128k'] # Standard AAC

            command += [
                '-movflags', '+faststart',
                '-y', self.output_path
            ]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if process.stdout:
                for line in process.stdout:
                    self.log.emit(line.strip())

            process.wait()

            if process.returncode == 0:
                self.finished.emit(True, self.output_path)
            else:
                self.finished.emit(False, f"FFmpeg error code: {process.returncode}")

        except Exception as e:
            self.finished.emit(False, str(e))
