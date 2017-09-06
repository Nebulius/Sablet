import csv
import sys

from datetime import datetime, timedelta
from pytz import timezone

# Le raspberry n'était pas à l'heure, correctif nécessaire (valeur exacte
# calculée à partir des relevés d'horaires effectués sur le moment, prenant en
# compte l'heure d'été)
SECONDS_SHIFT = 19680 - 2 * 3600

files = ['temperature_external.tsv', 'temperature_internal.tsv', 'pressure_altitude.tsv']

for file in files:
	with open('data/raw/' + file, 'r') as csv_file_raw, open('data/fixed/' + file, 'w', newline='') as csv_file_fix:
		data_reader = csv.reader(csv_file_raw, delimiter='\t')
		data_writer = csv.writer(csv_file_fix, dialect='excel-tab', delimiter='\t')

		for row in data_reader:
			if len(row) < 2: continue
			data_writer.writerow([float(row[0]) + SECONDS_SHIFT, *row[1:]])

with open('data/raw/altitude_real_estimed.tsv', 'r') as csv_file_raw, open('data/fixed/altitude_real_estimed.tsv', 'w', newline='') as csv_file_fix:
	data_reader = csv.reader(csv_file_raw, delimiter='\t')
	data_writer = csv.writer(csv_file_fix, dialect='excel-tab', delimiter='\t')

	launch = datetime(year=2017, month=8, day=17, hour=13, minute=12)

	for row in data_reader:
		if len(row) < 2: continue
		data_writer.writerow([(launch + timedelta(minutes=float(row[0]))).timestamp(), float(row[1]) * 1000])
