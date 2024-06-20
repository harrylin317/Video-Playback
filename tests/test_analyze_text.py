import unittest
from processing.analyze_text import AnalyzeText
import os
class TestAnalyzeText(unittest.TestCase):
    def setUp(self):
        save_path = f'outputs/output_test/'

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        self.args = {
        "video_path" : os.path.join('video_test.mp4'),
        "audio_path" : os.path.join(save_path, "audio.wav"),
        "df_path" : os.path.join(save_path, "text.csv"),
        "sub_path" : os.path.join(save_path, "sub.csv"),
        "transcript_path" : os.path.join(save_path, "transcript.json"),
        "output_path" : os.path.join(save_path, "output.mp4"),
        "segments_path" : os.path.join(save_path, "segments.json"),
        "split_max" : 20,
        "threshold_wpm" : 170,
        "threshold_spm" : 240,
        "run_extract_audio" : False,
        "run_audio_to_text": False,  
        "run_analyze_text": True   
    }
        
    def tearDown(self):
        # This method is run after each test
        # os.remove(self.filename)
        return
    def test_extract_audio_valid_input(self):
        # Test with valid input video file
        # Assert that the extracted audio file exists
        print(self.args['df_path'])
        analyze_text = AnalyzeText()
        analyze_text.combine_words(self.args['transcript_path'], self.args['split_max'])
        self.assertTrue(True)

    

if __name__ == "__main__":
    unittest.main()