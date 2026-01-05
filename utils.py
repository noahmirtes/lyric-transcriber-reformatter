import os

def write_to_txt(output_path, lyrics):
    # Clean up each line by stripping trailing whitespace
    cleaned_lines = [line.rstrip() for line in lyrics.splitlines()]

    # Join the cleaned lines back together with line breaks
    cleaned_lyrics = '\n'.join(cleaned_lines)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_lyrics)


def get_folder_contents_recursive(path, target_extensions):
    pass