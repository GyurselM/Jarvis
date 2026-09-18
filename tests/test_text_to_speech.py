from unittest.mock import patch
from audio.text_to_speech import EdgeTTSSpeaker


def test_speak_generates_plays_and_cleans_up():
    # __new__ crea el objeto sin ejecutar __init__, así evitamos
    # inicializar pygame.mixer de verdad durante el test.
    speaker = EdgeTTSSpeaker.__new__(EdgeTTSSpeaker)
    speaker._voice = "es-ES-AlvaroNeural"

    with patch.object(EdgeTTSSpeaker, "_generate_audio", return_value="fake.mp3") as mock_gen, \
         patch.object(EdgeTTSSpeaker, "_play_audio") as mock_play, \
         patch("audio.text_to_speech.os.remove") as mock_remove:
        speaker.speak("Hola")

    mock_gen.assert_called_once_with("Hola")
    mock_play.assert_called_once_with("fake.mp3")
    mock_remove.assert_called_once_with("fake.mp3")