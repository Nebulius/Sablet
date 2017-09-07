import csv
import click
import math

import moviepy.editor as mpy


PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_WIDTH = 1363
PROGRESS_BAR_POSITION = (41, 1000)

clip = mpy.VideoFileClip("Enregistrements/Embarqué/CameraBallon-complet.mp4").subclip(0, 5*60)
clip_gui = mpy.ImageClip('data/video/cadre_données_vide.png').set_duration(clip.duration)

composition = [clip, clip_gui]

def gen_numeric_text_position(text, x, y):
	'''
	On centre comme on peut :D
	'''
	# No data
	if text == 'N/A':
		return (x + 10, y + 16)

	# Positive; 0 <= n < 10
	elif len(text) == 1:
		return (x + 40, y) if text != '1' else (x + 65, y)

	# Positiv; 10 <= n < 100
	elif len(text) == 2 and text[0] != '-':
		return (x + 15, y) if text[1] == '1' else (x, y)

	# Negative, -10 < n <= -1
	elif len(text) == 2:
		return (x + 22, y) if text[1] == '1' else (x + 11, y)

	# Negative, -100 < n <= -10
	elif len(text) == 3:
		return (x - 35, y) if text[1] == '1' else (x - 44, y)


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
			altitude_text = str(int(float(data[5]) / 1000)) if data[5] != '-' else 'N/A'
			altitude_text_clip = (mpy.TextClip(
					altitude_text,
					fontsize=100 if altitude_text != 'N/A' else 60,
					font='JuraL',
					color='white'
				)
				.set_pos(gen_numeric_text_position(altitude_text, 1485, 956))
				.set_duration(1)
				.set_start(second))

			# Temperature
			temperature_text = data[4] if data[4] != '-' else 'N/A'
			temperature_text_clip = (mpy.TextClip(
					temperature_text,
					fontsize=100 if temperature_text != 'N/A' else 60,
					font='JuraL',
					color='white'
				)
				.set_pos(gen_numeric_text_position(temperature_text, 1735, 956))
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

print('\nAssemblage de {} clips...\n'.format(len(composition)))

video = mpy.CompositeVideoClip(composition)
#video.save_frame('frame_na.png', t=38)

video.write_videofile("Vidéos/Données brutes/Camera-Données-5m.mp4")
