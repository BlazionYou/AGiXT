try:
    from whisper_cpp import Whisper
except ImportError:
    import sys
    import subprocess

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "whisper-cpp-pybind",
        ]
    )
    from whisper_cpp import Whisper

import base64
import requests
import os
import re
from Extensions import Extensions


class whisper_stt(Extensions):
    def __init__(self, WHISPER_MODEL="base.en", **kwargs):
        self.commands = {
            "Transcribe Audio from File": self.transcribe_audio_from_file,
            "Transcribe Base64 Audio": self.transcribe_base64_audio,
        }
        # https://huggingface.co/ggerganov/whisper.cpp
        # Models: tiny, tiny.en, base, base.en, small, small.en, medium, medium.en, large, large-v1
        if WHISPER_MODEL not in [
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "medium",
            "medium.en",
            "large",
            "large-v1",
        ]:
            self.WHISPER_MODEL = "base.en"
        else:
            self.WHISPER_MODEL = WHISPER_MODEL
        os.makedirs(os.path.join(os.getcwd(), "models", "whispercpp"), exist_ok=True)
        model_path = os.path.join(
            os.getcwd(), "models", "whispercpp", f"ggml-{WHISPER_MODEL}.bin"
        )
        if not os.path.exists(model_path):
            r = requests.get(
                f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{WHISPER_MODEL}.bin",
                allow_redirects=True,
            )
            open(model_path, "wb").write(r.content)

    async def transcribe_audio_from_file(self, filename: str = "recording.wav"):
        w = Whisper(model_path=os.path.join(os.getcwd(), "models"))
        file_path = os.path.join(os.getcwd(), "WORKSPACE", filename)
        if not os.path.exists(file_path):
            raise RuntimeError(f"Failed to load audio: {filename} does not exist.")
        w.transcribe(file_path)
        return w.output()

    async def transcribe_base64_audio(self, base64_audio: str):
        # Save the audio as a file then run transcribe_audio_from_file.
        # Find any timestamps that start with year- like "2023-" until the end of the timestamp with a "Z " and remove them
        timestamp_pattern = r"\d{4}-[^Z]+Z ?"
        output_string = base64_audio
        while re.search(timestamp_pattern, output_string):
            output_string = re.sub(timestamp_pattern, "", output_string)
        print(f"Transcribing audio: {output_string}...")
        audio = base64.b64decode(output_string)
        filename = "recording.wav"
        with open(filename, "wb") as f:
            f.write(audio)
        output = await self.transcribe_audio_from_file(filename)
        os.remove(filename)
        return output
