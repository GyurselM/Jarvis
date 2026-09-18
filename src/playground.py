"""
Script de pruebas manuales, para verificar a ojo que las cosas
funcionan de verdad en tu sistema. No forma parte de la lógica
del asistente ni se importa desde ningún otro sitio.
"""

import os
import tempfile

from audio.microphone import record_audio
from audio.speech_to_text import GeminiTranscriber, TranscriptionError
from audio.text_to_speech import EdgeTTSSpeaker
from brain.router import Router
from integrations.llm_client import GeminiClient
from actions.registry import execute_command

if __name__ == "__main__":
    transcriber = GeminiTranscriber()
    router = Router(llm_client=GeminiClient())
    speaker = EdgeTTSSpeaker()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio_path = tmp_file.name

    record_audio(duration_seconds=4, output_path=audio_path)

    try:
        user_text = transcriber.transcribe(audio_path)
    except TranscriptionError as error:
        print(error)
        speaker.speak("No te he entendido, inténtalo de nuevo.")
        os.remove(audio_path)
        exit()

    os.remove(audio_path)

    print("Has dicho:", user_text)

    command = router.decide(user_text)
    print("Command decidido:", command)

    if command is not None:
        result = execute_command(command)
        print("Resultado de ejecutarlo:", result)
        speaker.speak(result.spoken_response)
    else:
        print("El router no encontró ninguna acción para esa frase.")
        speaker.speak("No he entendido qué quieres que haga.")