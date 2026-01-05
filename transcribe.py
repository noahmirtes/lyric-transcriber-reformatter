import whisper
import tempfile

import warnings
warnings.filterwarnings('ignore', message="FP16 is not supported on CPU; using FP32 instead")

# activate virtual environment
# source "/Users/noah/Library/Mobile Documents/com~apple~CloudDocs/Visual Studio/Lyric Transcriber/.venv_transcribe/bin/activate"
# /Users/noah/Library/Mobile Documents/com~apple~CloudDocs/Visual Studio/Lyric Transcriber/.venv_transcribe/bin/python3.10
 
def transcribe_audio(audio):

    # Use a temporary file for whisper
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_wav:
        temp_path = temp_wav.name
        audio.export(temp_path, format="wav")  # Save temp WAV

        # Load Whisper model (using the 'medium' model here)
        model = whisper.load_model("medium.en")
        result = model.transcribe(temp_path)  # Transcribe
        
    return result['text']
