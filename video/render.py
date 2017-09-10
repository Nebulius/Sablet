import csv
import math
import os
import sys

import click
import moviepy.editor as mpy
import pysrt

from PIL import ImageFont

from utils import text_align_right, text_center


root, _ = os.path.split(os.path.abspath(__file__))
root += '/'


'''
Renders a video with data on it.

If the 'no-messages' flag is passed, flashing messages are not written on the video.
'''


PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_WIDTH = 1363
PROGRESS_BAR_POSITION = (41, 1000)

DATA_FONT = ImageFont.truetype(root + '../data/video/Jura_Light.ttf', 100)
DATA_MISSING_FONT = ImageFont.truetype(root + '../data/video/Jura_Light.ttf', 60)

ALTITUDE_POSITION = (1595, 956)
ALTITUDE_POSITION_MISSING = (1595, 972)

TEMPERATURE_POSITION = (1845, 956)
TEMPERATURE_POSITION_MISSING = (1845, 972)


clip = mpy.VideoFileClip(root + '../../Enregistrements/Embarqué/CameraBallon-complet.mp4')
clip_gui = mpy.ImageClip(root + '../data/video/cadre_données_vide.png').set_duration(clip.duration)

composition = [clip, clip_gui]


# ------  Data on the video

with open(root + '../data/video/video_aggregate.tsv') as aggregate_file:
	aggregate = csv.reader(aggregate_file, delimiter='\t')

	print()
	with click.progressbar(aggregate, length=clip.duration, label='Préparation des données...') as bar:
		for data in bar:
			second = int(data[0])

			# End reached?
			if second >= clip.duration:
				break

			# Altitude
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
				.set_start(second))

			# Temperature
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
				.set_start(second))

			# Progress bar
			bar_width = int(math.floor(float(data[2]) * PROGRESS_BAR_WIDTH))
			progress_bar = (mpy.ColorClip(
					color=(255, 255, 255),
					size=(bar_width, PROGRESS_BAR_HEIGHT),
					duration=1)
				.set_pos(PROGRESS_BAR_POSITION)
				.set_start(second))

			composition += [altitude_text_clip, temperature_text_clip, progress_bar]


# ------  Messages above the progress bar (read from a subtitles file)

if 'no-messages' not in sys.argv:
	from render_messages import add_messages_clips

	messages = pysrt.open(root + '../data/video/messages.srt')
	composition += add_messages_clips(messages, clip.duration)


# ------  Final render

print('\nAssemblage de {} clips...\n'.format(len(composition)))

video = mpy.CompositeVideoClip(composition)
#video.save_frame('frame_na.png', t=0.3)

video.write_videofile(root + '../../Vidéos/Données brutes/CameraDonnées-complet.mp4', threads=6, preset='medium')
