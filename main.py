"""
So how will this work?

It could be helpful to have a little tkinter interface for this.

Basically the user sets an input folder with the audio in it and each file is processed
one by one.

Here's the flow for one file:
- Load the file
- Cut out the silence
- Compress the audio
- Apply filtering to a target curve

- transcribe the audio with whisper
- reformat raw transcription with ollama using multiple passes

"""

from audio_utils import (
    load_audio,
    simple_gate,
    trim_silence,
    peak_normalize
)

from transcribe import transcribe_audio
from reformat import reformat_basic
from utils import write_to_txt

def one_main(path):


    # load the audio
    audio, sr = load_audio(path)

    # normalize file peak
    audio = peak_normalize(audio)

    # remove silence
    audio = trim_silence(audio, sr)
    audio = simple_gate(audio, sr)

    # transcribe
    raw_transcription = transcribe_audio()

    # process transcription output x# of times
    reasoning_reformat = True
    reformatted_transcription = reformat_basic(raw_transcription, retry=5)
    write_to_txt(reformatted_transcription)




def TESTING():

    import soundfile as sf
    from audio_utils import simple_gate, trim_silence

    path = "/Volumes/WORK/HOWLING/Howling Music Dropbox/★ Howling Master Assets ★/Matthew Cosgrove/Bad Chick_HM003218/STEMS/FULL/Bad Chick_HM003218_Full_Fmin_113bpm_Main Vocal.wav"

    audio, sr = sf.read(path)

    audio = simple_gate(audio, sr)
    audio = trim_silence(audio, sr)

    sf.write("/Users/noah/Desktop/gate_test.wav", audio, sr)



TESTING()


