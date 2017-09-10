import csv
import os
import warnings

from pytz import timezone
from datetime import datetime

import numpy as np

import matplotlib.pyplot as plt

warnings.simplefilter('ignore', np.RankWarning)

root, _ = os.path.split(os.path.abspath(__file__))
root += '/'

with open(root + '../data/fixed/altitude_real_estimed.tsv', 'r') as altitude_discrete_file,\
     open(root + '../data/fixed/altitude_real_estimed_rp.tsv', 'w', newline='') as altitude_rp:
	altitude_discrete_csv = csv.reader(altitude_discrete_file, delimiter='\t')
	altitude_rp_csv = csv.writer(altitude_rp, dialect='excel-tab', delimiter='\t')

	moments = []
	altitudes = []

	for row in altitude_discrete_csv:
		moments.append(float(row[0]))
		altitudes.append(float(row[1]))

	moments_asc = np.array(moments[:20])
	altitudes_asc = np.array(altitudes[:20])

	moments_desc_1 = np.array(moments[19:23])
	altitudes_desc_1 = np.array(altitudes[19:23])

	moments_desc_2 = np.array(moments[22:24])
	altitudes_desc_2 = np.array(altitudes[22:24])

	moments_desc_3 = np.array(moments[23:])
	altitudes_desc_3 = np.array(altitudes[23:])

	altitudes_asc_rp = np.polyfit(moments_asc, altitudes_asc, 3)
	altitudes_desc_1_rp = np.polyfit(moments_desc_1, altitudes_desc_1, 3)
	altitudes_desc_2_rp = np.polyfit(moments_desc_2, altitudes_desc_2, 3)
	altitudes_desc_3_rp = np.polyfit(moments_desc_3, altitudes_desc_3, 3)

	print(datetime.fromtimestamp(moments_asc[0]).strftime('%H:%M'), datetime.fromtimestamp(moments_asc[-1]).strftime('%H:%M'), altitudes_asc_rp)
	print(datetime.fromtimestamp(moments_desc_1[0]).strftime('%H:%M'), datetime.fromtimestamp(moments_desc_1[-1]).strftime('%H:%M'), altitudes_desc_1_rp)
	print(datetime.fromtimestamp(moments_desc_2[0]).strftime('%H:%M'), datetime.fromtimestamp(moments_desc_2[-1]).strftime('%H:%M'), altitudes_desc_2_rp)
	print(datetime.fromtimestamp(moments_desc_3[0]).strftime('%H:%M'), datetime.fromtimestamp(moments_desc_3[-1]).strftime('%H:%M'), altitudes_desc_3_rp)

	altitudes_asc_rp_p = np.poly1d(altitudes_asc_rp)
	altitudes_desc_1_rp_p = np.poly1d(altitudes_desc_1_rp)
	altitudes_desc_2_rp_p = np.poly1d(altitudes_desc_2_rp)
	altitudes_desc_3_rp_p = np.poly1d(altitudes_desc_3_rp)

	"""
	xp_asc = np.linspace(moments_asc[0], moments_asc[-1], moments_asc[-1] - moments_asc[0])
	xp_desc_1 = np.linspace(moments_desc_1[0], moments_desc_1[-1], moments_desc_1[-1] - moments_desc_1[0])
	xp_desc_2 = np.linspace(moments_desc_2[0], moments_desc_2[-1], moments_desc_2[-1] - moments_desc_2[0])
	xp_desc_3 = np.linspace(moments_desc_3[0], moments_desc_3[-1], moments_desc_3[-1] - moments_desc_3[0])

	plt.plot(
		moments, altitudes, '.',
		xp_asc, altitudes_asc_rp_p(xp_asc), '-',
		xp_desc_1, altitudes_desc_1_rp_p(xp_desc_1), '-',
		xp_desc_2, altitudes_desc_2_rp_p(xp_desc_2), '-',
		xp_desc_3, altitudes_desc_3_rp_p(xp_desc_3), '-',
	)
	
	plt.show()
	"""

	xp = np.linspace(moments[0], moments[-1], moments[-1] - moments[0])

	grps = [
		altitudes_asc_rp_p, altitudes_desc_1_rp_p,
		altitudes_desc_2_rp_p, altitudes_desc_3_rp_p
	]

	index = 0
	nb_grps = len(grps)
	threshold = 18

	for moment in xp:
		y = grps[index](moment)

		if index < nb_grps - 1:
			y2 = grps[index + 1](moment)
			if abs(y2 - y) < threshold:
				print('index', index, '- y2 - y =', y2 - y, '- switching')
				index += 1
				y = y2

		altitude_rp_csv.writerow([moment, y])
