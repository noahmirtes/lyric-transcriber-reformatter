import os
import ollama
import time

lyric_folder = '/Volumes/HOWLING/•Dropbox•/Howling Music Dropbox/•Metadata Initiatives•/APM/MISC/Lyric Collecting/HB03_transcriptions'
output_path = '/Volumes/HOWLING/•Dropbox•/Howling Music Dropbox/•Metadata Initiatives•/APM/MISC/Lyric Collecting/HB03_reformats'
lyric_hopper = '/Volumes/HOWLING/•Dropbox•/Howling Music Dropbox/•Metadata Initiatives•/APM/MISC/Lyric Collecting/HB03_LYRIC HOPPER'
# ------------------------------------------ #

def reformat_basic():
    pass


def reformat_retry():
    pass


def reformat_self_check():
    pass

# ------------------------------------------ #


def ollama_lyric_format(lyrics):
    # initialize prompt
    prompt = (
        "Act as a professional editor specializing in formatting lyrics. Reformat the following raw text into properly formatted lyrics. "
        "It is crucial that you follow these instructions exactly:\n"
        "- Do not change, add, or remove any words from the original text.\n"
        "- Do not include section labels such as 'verse,' 'chorus,' or any other labels.\n"
        "- Only arrange the text into a natural and readable lyric format, using line breaks to reflect the song's structure.\n"
        "Your output must be limited strictly to the reformatted lyrics with no additional commentary, explanations, or labels.\n"
        "Here is the raw text:\n"
        f"{lyrics}"
    ) # look up about templates and being able to reuse them. then i can move the prompt outside of the function

    # send message
    response = ollama.chat(
        model='deepseek-r1',
        messages=[{'role' : 'user', 'content' : prompt}]
    )

    try:
        response = response.message.content
        return filter_think(response)
    except Exception as e:
        print(f"an error occured getting ollama result : {e}")
        return None
    


def filter_think(response):
    content_components = response.replace('</think>', '<think>')
    content_components = content_components.split('<think>')
    reply = content_components[-1]

    return reply.strip('\n')
