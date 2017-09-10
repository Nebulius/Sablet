import csv
import math
import os

import click
import moviepy.editor as mpy
import pysrt

from PIL import ImageFont

from utils import text_center


root, _ = os.path.split(os.path.abspath(__file__))
root += '/'


MESSAGES_BOX = (41, 1404, 942)  # x1, x2, y
MESSAGES_FONT = ImageFont.truetype(root + '../data/video/Jura_Light.ttf', 32)

def time_to_seconds(time):
	print(time.microsecond)
	return time.hour * 3600 + time.minute * 60 + time.second + (time.microsecond // 1000000)

def add_messages_clips(srt_file, last_second=None):
	'''
	Adds messages from the given srt file (a pysrt reader
	object) to a list of clips and returns the list.
	
	Only messages before the last_second are added (if given).
	'''
	composition = []

	with click.progressbar(srt_file, label='Préparation des messages...') as bar:
		for message in bar:
			start = time_to_seconds(message.start.to_time())
			duration = time_to_seconds(message.duration.to_time())
			text = message.text_without_tags

			if last_second is not None and start > last_second:
				print('\nMessage {} hors limites ({})'.format(text, start))
				continue

			duration = min(last_second - start, duration + 1.2 if start != 0 else duration + 0.6)

			print('\nAjout à {} ({} - {}) pendant {} ({}) de {}'.format(start, message.start.to_time(), message.start.to_time().minute, duration, message.duration, text))
			print('{} vs {}'.format(last_second - start, duration + 1.2 if start != 0 else duration + 0.6))

			message_clip = (mpy.TextClip(
						text,
						fontsize=32,
						font='JuraL',
						color='white'
					)
					.set_pos(text_center(text, MESSAGES_FONT, *MESSAGES_BOX))
					.set_duration(duration)
					.set_start(max(0, start - 0.6))
					.fx(mpy.vfx.fadein, .6)
					.fx(mpy.vfx.fadeout, .6))

			composition.append(message_clip)

	return composition


if __name__ == '__main__':
	clip = mpy.VideoFileClip(root + '../../Vidéos/Données brutes/Camera-Données-8m-medium.mp4')
	messages = pysrt.open(root + '../data/video/messages.srt')

	print()

	composition = [clip, *add_messages_clips(messages, clip.duration)]

	print('\nAssemblage de {} clips...\n'.format(len(composition)))
	print(composition)

	video = mpy.CompositeVideoClip(composition)
	#video.save_frame('frame_na.png', t=0.3)

	video.write_videofile(root + '../../Vidéos/Données brutes/Camera-Données-messages.mp4', threads=6, preset='medium')
