import os
import json
import torch
import traceback
import whisperx
import gc

class AudioToText:        
    def audio_to_text(self, audio_path, transcript_path):  
        try:  
            print('Extracting text from audio...')
            device = "cuda" 
            audio_file = audio_path
            batch_size = 8 # reduce if low on GPU mem
            compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

            # 1. Transcribe with original whisper (batched)
            model = whisperx.load_model("large-v2", device, compute_type=compute_type, language='en')

            audio = whisperx.load_audio(audio_file)
            result = model.transcribe(audio, batch_size=batch_size)

            # delete model if low on GPU resources
            gc.collect(); torch.cuda.empty_cache(); del model

            # 2. Align whisper output
            model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

            with open(transcript_path, "w") as outfile: 
                json.dump(result['word_segments'], outfile)

            print("Transcript created successfully")
            return 0
        except Exception as e:
            print(f"Error occurred when converting audio to text: {e}")
            traceback.print_exc()
            return -1

        
    def process(self, args):
        if args['run_audio_to_text']:
            audio_path = args['audio_path']
            transcript_path = args['transcript_path']
            status = self.audio_to_text(audio_path, transcript_path)
            return status
        else:
            print('Skip extracting text from audio')
            return 0


    
