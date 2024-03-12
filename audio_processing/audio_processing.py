import subprocess
import os
import json
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
import traceback

class AudioProcessing:
    def extract_audio(self, video_path, audio_path):
        try:
            print("Extracting audio...")
            command = f"ffmpeg -i {video_path} {audio_path}"
            subprocess.check_call(command, shell=True)
            print("Audio file created successfully.")
            return 0
        except Exception as e:
            print(f"Error occurred when extracting audio: {e}")
            traceback.print_exc()
            return -1
        

    def audio_to_text(self, audio_path, transcript_path):            
        try:
            print("Converting audio to text...")
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            print("Device:", device)
            model_id = "openai/whisper-large-v3"
            #model_id = "openai/whisper-tiny"

            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
            )
            model.to(device)
            processor = AutoProcessor.from_pretrained(model_id)
            
            pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=1,
                return_timestamps='word',
                torch_dtype=torch_dtype,
                device=device,
                generate_kwargs={"language": "english"},
            )
            result = pipe(audio_path)

            with open(transcript_path, 'w') as f:
                json.dump(result, f)
            print("Transcript created successfully")
            return 0
        except Exception as e:
            print(f"Error occurred when converting audio to text: {e}")
            traceback.print_exc()
            return -1
        
    def process(self, args):
        video_path = args['video_path']
        audio_path = args['audio_path']
        transcript_path = args['transcript_path']
        
        if not os.path.exists(audio_path):
            status = self.extract_audio(video_path, audio_path)
            if status != 0:
                return -1
        else:
            print("Audio file already exists.")

        if not os.path.exists(transcript_path):
            status = self.audio_to_text(audio_path, transcript_path)
            if status != 0:
                return -1
        else:
            print("Transcript file already exists.")
        
        return 0


    
