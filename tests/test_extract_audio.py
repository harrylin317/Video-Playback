import unittest
from audio_to_text.audio_to_text import extract_audio

class TestExtractAudio(unittest.TestCase):
    def test_extract_audio_valid_input(self):
        # Test with valid input video file
        # Assert that the extracted audio file exists
        self.assertTrue(extract_audio("valid_video.mp4"))

    def test_extract_audio_invalid_input(self):
        # Test with invalid input video file
        # Assert that the function returns None
        self.assertIsNone(extract_audio("nonexistent_video.mp4"))

if __name__ == "__main__":
    unittest.main()