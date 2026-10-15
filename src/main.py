"""
Punto de entrada de Jarvis. Solo conecta las piezas y mantiene el
bucle principal: esperar la palabra de activación y grabar la orden,
transcribir, decidir, ejecutar y responder. No contiene lógica propia
de cada pieza.
"""

import os
import tempfile
import time

from actions.registry import execute_command
from audio.speech_to_text import GeminiTranscriber, TranscriptionError
from audio.text_to_speech import EdgeTTSSpeaker, FallbackSpeaker, WindowsSpeaker
from audio.voice_capture import VoiceCapture
from audio.wake_word import OpenWakeWordDetector
from brain.router import Router
from integrations.llm_client import GeminiClient

MIN_COMMAND_CHARS = 3


def new_temp_wav_path() -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        return tmp_file.name


def handle_audio(audio_path: str, transcriber, router, speaker) -> None:
    start = time.perf_counter()
    try:
        user_text = transcriber.transcribe(audio_path)
    except TranscriptionError as error:
        print(error)
        speaker.speak("No te he entendido, inténtalo de nuevo.")
        return
    transcription_seconds = time.perf_counter() - start

    print("Has dicho:", user_text)

    # Descarta silencios y transcripciones absurdas (por ejemplo, una
    # sola letra): no tiene sentido mandarlas al router.
    if len(user_text) < MIN_COMMAND_CHARS:
        print("No he oído ninguna orden.")
        return

    start = time.perf_counter()
    command = router.decide(user_text)
    router_seconds = time.perf_counter() - start

    print("Command decidido:", command)

    if command is None:
        speaker.speak("No he entendido qué quieres que haga.")
        return

    start = time.perf_counter()
    result = execute_command(command)
    action_seconds = time.perf_counter() - start

    print("Resultado:", result)
    print(
        f"Tiempos -> transcripción: {transcription_seconds:.1f}s | "
        f"router: {router_seconds:.1f}s | acción: {action_seconds:.1f}s"
    )

    # Primero se ejecuta la acción y solo después se habla: la respuesta
    # hablada nunca retrasa la acción.
    speaker.speak(result.spoken_response)


def main() -> None:
    detector = OpenWakeWordDetector()
    capture = VoiceCapture(detector)
    transcriber = GeminiTranscriber()
    router = Router(llm_client=GeminiClient())
    speaker = FallbackSpeaker(primary=EdgeTTSSpeaker(), fallback=WindowsSpeaker())

    print("Jarvis listo. Di 'Hey Jarvis' y tu orden seguida. (Ctrl+C para salir)")

    try:
        while True:
            audio_path = new_temp_wav_path()

            try:
                print("Escuchando...")
                if not capture.wait_and_record(audio_path):
                    print("Te he oído, pero no he oído ninguna orden.")
                    continue

                print("Procesando...")
                handle_audio(audio_path, transcriber, router, speaker)
            except Exception as error:
                # Un fallo en un servicio externo no debe tumbar al asistente:
                # lo mostramos y seguimos escuchando.
                print(f"Error inesperado, sigo escuchando: {type(error).__name__}: {error}")
            finally:
                os.remove(audio_path)
    except KeyboardInterrupt:
        print("\nCerrando Jarvis.")
    finally:
        detector.close()


if __name__ == "__main__":
    main()