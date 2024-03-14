import subprocess
import traceback

class ExtractAudio:
    def extract_audio(self, video_path, audio_path):
        try:
            print("Extracting audio...")
            command = f"ffmpeg -y -i {video_path} {audio_path}"
            subprocess.check_call(command, shell=True)
            print("Audio file created successfully.")
            return 0
        except Exception as e:
            print(f"Error occurred when extracting audio: {e}")
            traceback.print_exc()
            return -1
        
    def process(self, args):
        if args['run_extract_audio']:
            video_path = args['video_path']
            audio_path = args['audio_path']        
            status = self.extract_audio(video_path, audio_path)
            return status
        else:
            print('Skip extracting audio from video')
            return 0
