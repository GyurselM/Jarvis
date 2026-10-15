from unittest.mock import patch, MagicMock
from audio.text_to_speech import EdgeTTSSpeaker, FallbackSpeaker, WindowsSpeaker, Speaker


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


def test_fallback_speaker_uses_primary_when_it_works():
    primary = MagicMock(spec=Speaker)
    fallback = MagicMock(spec=Speaker)

    FallbackSpeaker(primary, fallback).speak("Hola")

    primary.speak.assert_called_once_with("Hola")
    fallback.speak.assert_not_called()


def test_fallback_speaker_uses_fallback_when_primary_fails():
    primary = MagicMock(spec=Speaker)
    primary.speak.side_effect = RuntimeError("403")
    fallback = MagicMock(spec=Speaker)

    FallbackSpeaker(primary, fallback).speak("Hola")

    fallback.speak.assert_called_once_with("Hola")


def test_windows_speaker_sends_text_through_stdin_not_inside_command():
    hostile_text = "Hola'; Remove-Item -Recurse C:\\"

    with patch("audio.text_to_speech.subprocess.run") as mock_run:
        WindowsSpeaker().speak(hostile_text)

    args, kwargs = mock_run.call_args
    assert kwargs["input"] == hostile_text
    assert all("Remove-Item" not in part for part in args[0])