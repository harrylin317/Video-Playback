import json
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
import pandas as pd

def audio_to_text(audio_file_path, transcript_path):
    try:

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
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
            generate_kwargs={"language": "english"},
        )

        result = pipe(audio_file_path)

        convert_to_csv(result, transcript_path)

        return 0
    except Exception as e:
        print(f"Error occurred when convertin audio to text: {e}")
        return 1
    
def convert_to_csv(transcript, transcript_path):
    df = pd.DataFrame(columns=['timestamp', 'text'])
    chunks = transcript['chunks']
    for chunk in chunks:
        new_row = pd.DataFrame({'timestamp': [chunk['timestamp']], 'text': [chunk['text']]})
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(transcript_path, index=False)

