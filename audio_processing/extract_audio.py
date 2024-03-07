import subprocess
def extract_audio(video_path, audio_path):
    try:
        command = f"ffmpeg -i {video_path} {audio_path}"
        subprocess.check_call(command, shell=True)
        return 0
    except Exception as e:
        print(f"Error occurred when extracting audio: {e}")
        return 1
    
