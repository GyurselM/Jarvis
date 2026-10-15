"""
Salida de voz: convierte texto en audio hablado y lo reproduce.
"""

import asyncio
import os
import subprocess
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

    def __init__(self, voice: str = "es-ES-AlvaroNeural"):
        self._voice = voice
        pygame.mixer.init()

    def speak(self, text: str) -> None:
        audio_path = self._generate_audio(text)
        try:
            self._play_audio(audio_path)
        finally:
            os.remove(audio_path)

    def _generate_audio(self, text: str) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            audio_path = tmp_file.name

        try:
            communicate = edge_tts.Communicate(text, self._voice)
            asyncio.run(communicate.save(audio_path))
        except Exception:
            # Si falla la generación, no dejamos el archivo vacío en disco.
            os.remove(audio_path)
            raise

        return audio_path

    def _play_audio(self, audio_path: str) -> None:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()


# El texto NUNCA se mete dentro de este script: se envía por la entrada
# estándar. Así, aunque el texto contuviera comillas o comandos, no se
# ejecutaría nada (el texto de Jarvis sale de un LLM y hay que tratarlo
# como datos, no como código).
POWERSHELL_SCRIPT = (
    "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
    "Add-Type -AssemblyName System.Speech; "
    "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
    "try { $synth.SelectVoiceByHints('NotSet', 'NotSet', 0, "
    "[System.Globalization.CultureInfo]::GetCultureInfo('es-ES')) } catch {}; "
    "$synth.Speak([Console]::In.ReadToEnd())"
)


class WindowsSpeaker(Speaker):
    """
    Voz local de Windows (System.Speech): funciona sin internet y sin
    instalar nada. Suena más robótica que Edge, pero sirve de respaldo.
    Usa una voz en español si hay alguna instalada en el sistema.
    """

    def speak(self, text: str) -> None:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", POWERSHELL_SCRIPT],
            input=text,
            encoding="utf-8",
            check=True,
            timeout=30,
        )


class FallbackSpeaker(Speaker):
    """Intenta hablar con el locutor principal y, si falla, usa el de respaldo."""

    def __init__(self, primary: Speaker, fallback: Speaker):
        self._primary = primary
        self._fallback = fallback

    def speak(self, text: str) -> None:
        try:
            self._primary.speak(text)
        except Exception as error:
            print(f"Voz principal no disponible ({type(error).__name__}), uso la de respaldo.")
            self._fallback.speak(text)