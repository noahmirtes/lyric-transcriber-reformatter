import ollama

# ------------------------------------------ #

def filter_think(response):
    content_components = response.replace('</think>', '<think>')
    content_components = content_components.split('<think>')
    reply = content_components[-1]

    return reply.strip('\n')

# ------------------------------------------ #

# TODO : Move the prompts outside of the functions so they're only defined one time

def reformat_basic(raw_transcription : str) -> str:
    # initialize prompt
    prompt = (
        "Act as a professional editor specializing in formatting lyrics. Reformat the following raw text into properly formatted lyrics. "
        "It is crucial that you follow these instructions exactly:\n"
        "- Do not change, add, or remove any words from the original text.\n"
        "- Do not include section labels such as 'verse,' 'chorus,' or any other labels.\n"
        "- Only arrange the text into a natural and readable lyric format, using line breaks to reflect the song's structure.\n"
        "Your output must be limited strictly to the reformatted lyrics with no additional commentary, explanations, or labels.\n"
        "Here is the raw text:\n"
        f"{raw_transcription}"
    )

    # send message
    response = ollama.chat(
        model='deepseek-r1',
        messages=[{'role' : 'user', 'content' : prompt}]
    )

    # extract response
    try:
        response = response.message.content
        return filter_think(response)
    except Exception as e:
        print(f"an error occured getting ollama result : {e}")
        return None


def reformat_retry(raw_transcription, retry_limit=3):
    # initialize prompt
    prompt = (
        "Act as a professional editor specializing in formatting lyrics. Reformat the following raw text into properly formatted lyrics. "
        "It is crucial that you follow these instructions exactly:\n"
        "- Do not change, add, or remove any words from the original text.\n"
        "- Do not include section labels such as 'verse,' 'chorus,' or any other labels.\n"
        "- Only arrange the text into a natural and readable lyric format, using line breaks to reflect the song's structure.\n"
        "Your output must be limited strictly to the reformatted lyrics with no additional commentary, explanations, or labels.\n"
        "Here is the raw text:\n"
        f"{raw_transcription}"
    )

    # send message
    response = ollama.chat(
        model='deepseek-r1',
        messages=[{'role' : 'user', 'content' : prompt}]
    )

    # extract response
    retry = 0
    while True:
        try:
            response = response.message.content
            reformatted = filter_think(response)
            if reformatted and len(reformatted) > 0:
                return reformatted
            elif retry == retry_limit:
                print("Retry Limit reached. Returning last produced transcription.")
                return reformatted
            else:
                print("Received empty reformatted text, retrying...")
                retry += 1
        except Exception as e:
            print(f"an error occured getting ollama result : {e}")
            return raw_transcription


def reformat_self_check(raw_transcription, retry_limit = 3):
    attempt = 1
    while True:

        # initialize the prompt
        quality_check_prompt = f"""
        Act as a professional editor that specializes in poetry and lyric formatting. Review the following reformat for quality and accuracy.
        I am providing both the input text pre-reformat and post-reformat. Your job is to review and determin if the quality is satisfactory.
        
        The reformats must strictly follow these rules:
        - Do not change, add, or remove any words from the original text.
        - Do not include section labels such as 'verse,' 'chorus,' or any other labels.
        - Only arrange the text into a natural and readable lyric format, using line breaks to reflect the song's structure.
        - The reformat must be limited strictly to the raw transcription with no additional commentary, explanations, or labels.

        This is the raw transcription:
        {raw_transcription}

        This is the reformatted text:
        {transcription}

        Review the raw and reformatted lyrics and determine if the reformat abides by the explicit rules I stated. Limit your output to "True" or "False".

        """

        print(f"Running Transcription Attempt {attempt}. . .")
        transcription = reformat_basic(raw_transcription)

        quality_response = ollama.chat(
            model='deepseek-r1',
            messages=[{'role' : 'user', 'content' : quality_check_prompt}]
        )

        reformatted_quality_response = filter_think(quality_response)

        if 'true' in reformatted_quality_response.lower():
            return transcription
        elif attempt == retry_limit:
            return transcription
        else:
            print(f"Transcription quality was not satisfactory. Retrying transcription...")
            attempt += 1


# ------------------------------------------ #

    
