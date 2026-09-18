"""
Salida de voz: convierte texto en audio hablado y lo reproduce.
"""

import asyncio
import os
import tempfile

import edge_tts
import pygame


class Speaker:
    """Interfaz que cualquier motor de texto a voz debe cumplir."""

    def speak(self, text: str) -> None:
        raise NotImplementedError


class EdgeTTSSpeaker(Speaker):
    """
    Implementación usando edge-tts: voces neuronales de Microsoft Edge,
    gratuitas y sin necesitar clave API.

    Voces en español disponibles, por ejemplo:
    - "es-ES-AlvaroNeural" (hombre, España)
    - "es-ES-ElviraNeural" (mujer, España)
    """

    def __init__(self, voice: str = "es-ES-ElviraNeural"):
        self._voice = voice
        pygame.mixer.init()

    def speak(self, text: str) -> None:
        audio_path = self._generate_audio(text)
        self._play_audio(audio_path)
        os.remove(audio_path)

    def _generate_audio(self, text: str) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            audio_path = tmp_file.name

        communicate = edge_tts.Communicate(text, self._voice)
        asyncio.run(communicate.save(audio_path))

        return audio_path

    def _play_audio(self, audio_path: str) -> None:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()