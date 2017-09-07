import csv

from datetime import datetime, timedelta
from collections import OrderedDict

'''
This scripts aggregates all the data from the various files and writes
an unique TSV file with all required data into it, in order per line:
0. the second in the video (starting at 0)
1. the timestamp, rounded
2. the percentage _of the flight_, not rounded, between 0 and 1
3. the internal temperature, rounded, in °C
4. the external temperature, rounded, in °C
5. the altitude, rounded, in meters
6. the pressure, rounded, in kPa

If the data is not available, "-" is stored instead.
'''

with open('data/fixed/temperature_internal.tsv') as temperature_in_file,\
	 open('data/fixed/temperature_external.tsv') as temperature_out_file,\
	 open('data/fixed/pressure_altitude.tsv') as pressure_file,\
	 open('data/fixed/altitude_real_estimed_rp.tsv') as altitude_file,\
	 open('data/video/video_aggregate.tsv', 'w', newline='') as aggregate_file:
	temperature_in = csv.reader(temperature_in_file, delimiter='\t')
	temperature_out = csv.reader(temperature_out_file, delimiter='\t')
	pressure = csv.reader(pressure_file, delimiter='\t')
	altitude = csv.reader(altitude_file, delimiter='\t')

	aggregate = csv.writer(aggregate_file, dialect='excel-tab', delimiter='\t')

	launch = datetime(2017, 8, 17, 13, 12, 0)
	video_start = launch - timedelta(seconds=12)
	video_end = video_start + timedelta(hours=2, minutes=12, seconds=12)
	touchdown = datetime(2017, 8, 17, 15, 30, 0)

	current = video_start
	step = timedelta(seconds=1)

	def write_aggr_line(moment, temperature_in=None, temperature_out=None, altitude=None, pressure=None):
		'''
		aggregate: a CSV writer
		moment: the moment in the time for that line
		temperature, altitude, pressure: should be evident
		'''
		aggregate.writerow([
			(moment - video_start).seconds,
			int(moment.timestamp()),
			0.0 if moment < launch else '{:.8f}'.format(float((moment - launch).seconds) / float((touchdown - launch).seconds)),
			int(float(temperature_in)) if temperature_in is not None else '-',
			int(float(temperature_out)) if temperature_out is not None else '-',
			int(float(altitude)) if altitude is not None else '-',
			int(float(pressure)) if pressure is not None else '-'
		])

	# We first write the part before the launch in the video
	while current < launch:
		write_aggr_line(current)
		current += step

	# We have to aggregate the data from various sources with various timestamps.
	# There is not a data point for each timestamp in each data source, but *almost*,
	# so no interpolation or polynomial regression required here. If a point is missing,
	# we only use the previous known.

	def index_data_by_timestamp(data):
		'''
		Takes an iterable yelding lists (e.g. CSV reader)
		containing a timestamp as the first item of the list
		and returns a dict with timestamps as keys and
		the other items of the list as (list) value.

		Assumes each timestamp (int-rounded) is unique in the
		data source.

		Returns the indexed dict.
		'''
		indexed_data = OrderedDict()
		for item in data:
			indexed_data[int(float(item[0]))] = item[1:]
		return indexed_data

	def first_key_after(ordered_dict, ref_key):
		'''
		Returns the first item value of an ordered dict
		(or any dict but the concept of “first” is
		meaningless for non-ordered dicts), that is
		greater than the given key value, assuming
		numeric keys.
		'''
		for key, value in ordered_dict.items():
			if key < ref_key: continue
			return value

	idx_temperature_in = index_data_by_timestamp(temperature_in)
	idx_temperature_out = index_data_by_timestamp(temperature_out)
	idx_pressure = index_data_by_timestamp(pressure)
	idx_altitude = index_data_by_timestamp(altitude)

	timestamp = int(current.timestamp())

	current_temperature_in = first_key_after(idx_temperature_in, timestamp)
	current_temperature_out = first_key_after(idx_temperature_out, timestamp)
	current_pressure = first_key_after(idx_pressure, timestamp)
	current_altitude = first_key_after(idx_altitude, timestamp)

	while current <= video_end:
		timestamp = int(current.timestamp())

		current_temperature_in = idx_temperature_in.get(timestamp, current_temperature_in)
		current_temperature_out = idx_temperature_out.get(timestamp, current_temperature_out)
		current_pressure = idx_pressure.get(timestamp, current_pressure)
		current_altitude = idx_altitude.get(timestamp, current_altitude)

		write_aggr_line(
			current,
			temperature_in=current_temperature_in[0],
			temperature_out=current_temperature_out[0],
			pressure=current_pressure[0],
			altitude=max(float(current_altitude[0]), 0)
		)
		current += step
