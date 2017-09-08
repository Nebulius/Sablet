import csv
import click
import math

import moviepy.editor as mpy
import pysrt

from PIL import ImageFont


PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_WIDTH = 1363
PROGRESS_BAR_POSITION = (41, 1000)

MESSAGES_BOX = (41, 1404, 942)  # x1, x2, y
MESSAGES_FONT = ImageFont.truetype('data/video/Jura_Light.ttf', 32)

DATA_FONT = ImageFont.truetype('data/video/Jura_Light.ttf', 100)
DATA_MISSING_FONT = ImageFont.truetype('data/video/Jura_Light.ttf', 60)

ALTITUDE_POSITION = (1595, 956)
ALTITUDE_POSITION_MISSING = (1595, 972)

TEMPERATURE_POSITION = (1845, 956)
TEMPERATURE_POSITION_MISSING = (1845, 972)


clip = mpy.VideoFileClip("Enregistrements/Embarqué/CameraBallon-complet.mp4").subclip(0, 8*60)
clip_gui = mpy.ImageClip('data/video/cadre_données_vide.png').set_duration(clip.duration)

composition = [clip, clip_gui]


# ------  Text alignment utils

def text_center(text, font, x1, x2, y):
	'''
	Centers a text in the given space, between x1 and x1
	and at y, using the given font. Returns the position
	of the top-left corner to be used with moviepy.

	font must be a PIL.ImageFont instance.
	'''
	x_center = int((float(abs(x2 - x1)) / 2.0) + min(x1, x2))
	text_box = font.getsize(text)
	return (x_center - (float(text_box[0]) / 2.0), y)

def text_align_right(text, font, x, y):
	'''
	Returns the position a text should have, for it to
	ends at the given position.

	font must be a PIL.ImageFont instance.
	'''
	text_box = font.getsize(text)
	return (x - text_box[0], y)


# ------  Data on the video

with open('data/video/video_aggregate.tsv') as aggregate_file:
	aggregate = csv.reader(aggregate_file, delimiter='\t')

	print()
	with click.progressbar(aggregate, length=clip.duration, label='Préparation des données...') as bar:
		for data in bar:
			second = int(data[0])

			# End reached?
			if second > clip.duration:
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

messages = pysrt.open('data/video/messages.srt')

with click.progressbar(messages, label='Préparation des messages...') as bar:
	for message in bar:
		start = message.start.seconds
		duration = message.duration.seconds
		text = message.text_without_tags

		if start > clip.duration:
			continue

		message_clip = (mpy.TextClip(
					text,
					fontsize=32,
					font='JuraL',
					color='white'
				)
				.set_pos(text_center(text, MESSAGES_FONT, *MESSAGES_BOX))
				.set_duration(duration + 1.2 if start != 0 else duration + 0.6)
				.set_start(max(0, start - 0.6))
				.fx(mpy.vfx.fadein, .6)
				.fx(mpy.vfx.fadeout, .6))

		composition.append(message_clip)


# ------  Final render

print('\nAssemblage de {} clips...\n'.format(len(composition)))

video = mpy.CompositeVideoClip(composition)
#video.save_frame('frame_na.png', t=0.3)

video.write_videofile("Vidéos/Données brutes/Camera-Données-5m-medium.mp4", threads=6, preset='medium')
