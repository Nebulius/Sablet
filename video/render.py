import csv
import math
import os
import sys

import click
import moviepy.editor as mpy
import pysrt

from PIL import ImageFont

from utils import text_align_right


root, _ = os.path.split(os.path.abspath(__file__))
root += '/'


PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_WIDTH = 1363
PROGRESS_BAR_POSITION = (41, 1000)

DATA_FONT = ImageFont.truetype(root + '../data/video/Jura_Light.ttf', 100)
DATA_MISSING_FONT = ImageFont.truetype(root + '../data/video/Jura_Light.ttf', 60)

ALTITUDE_POSITION = (1595, 956)
ALTITUDE_POSITION_MISSING = (1595, 972)

TEMPERATURE_POSITION = (1845, 956)
TEMPERATURE_POSITION_MISSING = (1845, 972)


# Loads data in second-indexed dict
aggregate = []

with open(root + '../data/video/video_aggregate.tsv') as aggregate_file:
    aggregate_csv = csv.reader(aggregate_file, delimiter='\t')

    for item in aggregate_csv:
        aggregate.append(item)


def render_data_on_clip(base_clip, destination, starts_at=None, during=None, messages_file=None):
    '''
    Renders a video with data on it.

    base_clip: The base clip to add data into.
    starts_at: The rendered clip will start there.
    during: The rendered clip will be this duration.
    messages_file: if not none, adds messages from the given srt
      file (a pysrt reader object).
    '''
    if starts_at is None:
        starts_at = 0

    if during is None:
        during = base_clip.duration

    clip = base_clip.subclip(starts_at, starts_at + during)
    clip_gui = mpy.ImageClip(root + '../data/video/cadre_données_vide.png').set_duration(clip.duration)

    composition = [clip, clip_gui]

    # ------  Data on the video

    print()
    with click.progressbar(aggregate[starts_at:starts_at + during], length=clip.duration, label='Préparation des données...') as bar:
        for data in bar:
            second = int(data[0])

            # Altitude
            missing = data[5] == '-'

            altitude_text = str(int(float(data[5]) / 1000)) if not missing else 'N/A'
            altitude_text_clip = (mpy.TextClip(
                    altitude_text,
                    fontsize=100 if not missing else 60,
                    font='JuraL',
                    color='white'
            )
                .set_pos(text_align_right(
                    altitude_text, DATA_FONT if not missing else DATA_MISSING_FONT,
                    *(ALTITUDE_POSITION if not missing else ALTITUDE_POSITION_MISSING))
            )
                .set_duration(1)
                .set_start(second - starts_at))

            # Temperature
            missing = data[4] == '-'

            temperature_text = data[4] if not missing else 'N/A'
            temperature_text_clip = (mpy.TextClip(
                    temperature_text,
                    fontsize=100 if not missing else 60,
                    font='JuraL',
                    color='white'
            )
                .set_pos(text_align_right(
                    temperature_text, DATA_FONT if not missing else DATA_MISSING_FONT,
                    *(TEMPERATURE_POSITION if not missing else TEMPERATURE_POSITION_MISSING))
            )
                .set_duration(1)
                .set_start(second - starts_at))

            # Progress bar
            bar_width = int(math.floor(float(data[2]) * PROGRESS_BAR_WIDTH))
            progress_bar = (mpy.ColorClip(
                    color=(255, 255, 255),
                    size=(bar_width, PROGRESS_BAR_HEIGHT),
                    duration=1)
                .set_pos(PROGRESS_BAR_POSITION)
                .set_start(second - starts_at))

            composition += [altitude_text_clip, temperature_text_clip, progress_bar]

    # ------  Messages above the progress bar (read from a subtitles file)

    if messages_file is not None:
        from render_messages import add_messages_clips
        composition += add_messages_clips(messages_file, clip.duration)

    # ------  Final render

    print(f'\nAssemblage de {len(composition)} clips...\n')

    video = mpy.CompositeVideoClip(composition)
    # video.save_frame('frame_na.png', t=0.3)

    video.write_videofile(destination, threads=6, preset='medium', audio=False)


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    if 'help' in sys.argv:
        print(sys.argv[0], '[part duration in seconds [first rendered part (starts at 1)]] [no-messages]')
        exit()

    clip = mpy.VideoFileClip(root + '../../Enregistrements/Embarqué/CameraBallon-complet.mp4')

    add_messages = 'no-messages' not in sys.argv
    messages = pysrt.open(root + '../data/video/messages.srt') if add_messages else None

    parts_length = int(sys.argv[1]) if len(sys.argv) > 1 and is_int(sys.argv[1]) else 5 * 60
    parts = math.ceil(float(clip.duration) / float(parts_length))

    first_part = int(sys.argv[2]) - 1 if len(sys.argv) > 2 and is_int(sys.argv[2]) else 0

    for part in range(first_part, parts):
        destination = f'{root}../../Vidéos/Données brutes/Camera-Donnees-{part + 1}-of-{parts}.mp4'
        start = part * parts_length

        print(f'\n---------------------\n\nRendu de la vidéo {part + 1} de {parts}...')
        render_data_on_clip(clip, starts_at=start, during=parts_length, destination=destination)
