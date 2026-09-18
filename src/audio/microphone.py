"""
Grabación de audio desde el micrófono.
"""

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000


def record_audio(duration_seconds: int, output_path: str) -> str:
    """
    Graba audio del micrófono durante duration_seconds y lo guarda
    como un archivo .wav estándar (PCM 16 bits) en output_path.
    """
    print(f"Grabando {duration_seconds} segundos... habla ahora.")
    recording = sd.rec(
        int(duration_seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    sf.write(output_path, recording, SAMPLE_RATE, subtype="PCM_16")
    print("Grabación terminada.")

    return output_path