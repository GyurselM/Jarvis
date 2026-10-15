"""
Diagnóstico del detector de palabra de activación. Muestra en tiempo
real el volumen del micrófono y la puntuación del modelo de Jarvis.
Es una herramienta de pruebas, no forma parte del asistente.
"""

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

SAMPLE_RATE = 16000
FRAME_SAMPLES = 1280  # 80 ms

if __name__ == "__main__":
    print("Micrófono por defecto:", sd.query_devices(kind="input")["name"])

    model = Model(inference_framework="onnx")
    print("Habla ahora. Ctrl+C para salir.\n")

    first_frame = True

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=FRAME_SAMPLES,
        channels=1,
        dtype="int16",
    ) as stream:
        try:
            while True:
                data, _overflowed = stream.read(FRAME_SAMPLES)
                frame = data[:, 0]
                predictions = model.predict(frame)

                if first_frame:
                    print("Nombres de los modelos:", list(predictions.keys()), "\n")
                    first_frame = False

                volume = int(np.abs(frame).mean())
                jarvis_score = max(
                    (score for name, score in predictions.items() if "jarvis" in name.lower()),
                    default=0.0,
                )

                if jarvis_score >= 0.1:
                    print(f"\n  >> puntuación Jarvis: {jarvis_score:.2f}")

                print(f"\rVolumen: {volume:5d} | Jarvis: {jarvis_score:.2f}   ", end="", flush=True)
        except KeyboardInterrupt:
            print("\nFin del diagnóstico.")