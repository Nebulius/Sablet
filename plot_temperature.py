import csv
import sys

from datetime import datetime, timedelta
from pytz import timezone
from collections import defaultdict

import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')  # Commenter sous Windows (sauf si ça marche tel quel, j'sais pas)

from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates


# Datasets names
DATASETS = [
    'all',
    'temperature', 'temperature-int', 'temperature-ext',
    'pressure',
    'altitude', 'altitude-from-pressure', 'altitude-real', 'altitude-real-rp'
    'diff-temperature'
]


## Aide et vérification des arguments

if len(sys.argv) > 1 and sys.argv[1] == 'help':
    print(sys.argv[0], 'all (the default), or')
    print(sys.argv[0], '<list of space-separated data to plot> (up to three, see below), or')
    print(sys.argv[0], 'diff-temperatures (compares external temperature from temperature and pressure sensors), or')
    print(sys.argv[0], 'help (this help).')
    print()
    print('Available dataset:', ', '.join(DATASETS))
    exit()


args = sys.argv[1:]
invalid_args = []

for arg in args:
    if arg not in DATASETS:
        invalid_args.append(arg)

for arg in invalid_args:
    args.remove(arg)

if 'all' in args or not args:
    args = ['temperature', 'pressure', 'altitude']


## Chargement et interprétation des données

with open('data/fixed/temperature_external.tsv', 'r') as temp_file_ext, open('data/fixed/temperature_internal.tsv', 'r') as temp_file_int,\
     open('data/fixed/pressure_altitude.tsv', 'r') as pressure_file, open('data/fixed/altitude_real_estimed.tsv') as altitude_file,\
     open('data/fixed/altitude_real_estimed_rp.tsv') as altitude_rp_file:
    temps_ext = csv.reader(temp_file_ext, delimiter='\t')
    temps_int = csv.reader(temp_file_int, delimiter='\t')
    pressure = csv.reader(pressure_file, delimiter='\t')
    altitudes_real_estimed = csv.reader(altitude_file, delimiter='\t')
    altitudes_real_estimed_rp = csv.reader(altitude_rp_file, delimiter='\t')

    moments = []
    values_int = []
    values_ext = []

    def get_plots_lists(data, is_pressure=False):
        """
        Format des données pour la température : 
        timestamp, température en degrés Celsius
        
        Format des données pour la pression : 
        timestamp, pression, altitude évaluée, température en degrés Celsius
        """
        moments = []
        temperatures = []
        pressures = []
        altitudes = []

        prev_moment = None
        prev_temp_ext = None

        for row in data:
            if len(row) < 2: continue
            moment = datetime.fromtimestamp(float(row[0]), tz=timezone('Europe/Paris'))

            # Suppression des données hors plage de lancement ou incohérentes
            if prev_moment is not None and moment < prev_moment: continue
            if moment.hour < 9 or moment.hour > 16: continue
            prev_moment = moment

            moments.append(moment)
            
            if is_pressure:
                pressures.append(float(row[1]))
                altitudes.append(float(row[2]))
                temperatures.append(float(row[3]))
            else:
                temperatures.append(float(row[1]))
        
        if is_pressure:
            return moments, pressures, altitudes, temperatures
        
        return moments, temperatures


    moments_int, values_int = get_plots_lists(temps_int)
    moments_ext, values_ext = get_plots_lists(temps_ext)
    moments_pressure, pressures, altitudes, temperatures_pressure = get_plots_lists(pressure, True)
    moments_altitudes_real_estimed, values_altitudes_real_estimed = get_plots_lists(altitudes_real_estimed)
    moments_altitudes_real_estimed_rp, values_altitudes_real_estimed_rp = get_plots_lists(altitudes_real_estimed_rp)


## Traitement des données de pression et d'altitude aberrantes

def detect_and_fix_bad_data(data, threshold, replace_with='prev_good'):
    """
    Detects bad data in a sequence and replaces these data.
    
    Bad data is values more than <threshold> lower or higher of the previous good data,
    considering the first data point is good.
    
    A bad data point is replaced by:
    - the previous good data point, if <replace_with> is set to 'prev_good';
    - the raw value of <replace_with>, else.
    
    The list is updated in place and returned.
    
    TODO improve this
    """
    last_good_data = data[0]
    
    for data_point_idx in range(len(data)):
        data_point = data[data_point_idx]
        
        if abs(data_point - last_good_data) < threshold:
            last_good_data = data_point
            continue
        
        # Here the data is not good
        data[data_point_idx] = last_good_data if replace_with == 'prev_good' else replace_with
    
    return data


altitudes = detect_and_fix_bad_data(altitudes, 1300)
pressures = detect_and_fix_bad_data(pressures, 5)


## Affichage du graph

first_axis = host_subplot(111, axes_class=AA.Axes)
plt.subplots_adjust(left=0.1, right=0.95 - (0.10 * (len(args) - 1)))

if 'diff-temperatures' in args:
    pass # TODO

else:
    def get_data_and_labels(input):
        '''
        Returns tuple:
        (
            [list of tuples with (x_list, y_list, label)],
            axis label,
            axis ticker (or None)
        )
        or None if invalid input.
        '''
        if input == 'temperature':
            return (
                [
                    (moments_int, values_int, 'Température intérieure'),
                    (moments_ext, values_ext, 'Température extérieure')
                ],
                'Température (°C)',
                ticker.MultipleLocator(10)
            )
        elif input == 'temperature-int':
            return (
                [
                    (moments_int, values_int, 'Température intérieure')
                ],
                'Température (°C)',
                ticker.MultipleLocator(10)
            )
        elif input == 'temperature-ext':
            return (
                [
                    (moments_ext, values_ext, 'Température extérieure')
                ],
                'Température (°C)',
                ticker.MultipleLocator(10)
            )
        elif input == 'pressure':
            return (
                [
                    (moments_pressure, pressures, 'Pression atmosphérique')
                ],
                'Pression (kPa)',
                None
            )
        elif input == 'altitude':
            return (
                [
                    (moments_pressure, altitudes, 'Altitude calculée à partir de la pression'),
                    (moments_altitudes_real_estimed_rp, values_altitudes_real_estimed_rp, 'Altitude plus réaliste estimée')
                ],
                'Altitude (m)',
                None
            )
        elif input == 'altitude-from-pressure':
            return (
                [
                    (moments_pressure, altitudes, 'Altitude calculée à partir de la pression'),
                ],
                'Altitude (m)',
                None
            )
        elif input == 'altitude-real':
            return (
                [
                    (moments_altitudes_real_estimed, values_altitudes_real_estimed, 'Altitude plus réaliste estimée')
                ],
                'Altitude (m)',
                None
            )
        elif input == 'altitude-real-rp':
            return (
                [
                    (moments_altitudes_real_estimed_rp, values_altitudes_real_estimed_rp, 'Altitude plus réaliste estimée (régression polynômiale)')
                ],
                'Altitude (m)',
                None
            )
        else:
            return None
    
    def put_data_into_axis(axis, data):
        '''
        Displays given data in given axis
        axis: a matplotlib axis
        data: a dataset+labels as returned by get_data_and_labels
        '''
        plots, legend, ticker = data
        
        for data_x, data_y, label in plots:
            axis.plot(data_x, data_y, label=label)
        
        axis.set_ylabel(legend)
        
        if ticker is not None:
            axis.yaxis.set_major_locator(ticker)
    
    # Premier axe
    put_data_into_axis(first_axis, get_data_and_labels(args[0]))
    
    # Autres axes
    
    is_third_axis_or_more = False
    offset = 0
    
    for axis_data in args[1:]:
        other_axis = first_axis.twinx()
        
        if is_third_axis_or_more:
            offset += 60
            new_fixed_axis = other_axis.get_grid_helper().new_fixed_axis
            other_axis.axis["right"] = new_fixed_axis(loc="right",
                                                axes=other_axis,
                                                offset=(offset, 0))

            other_axis.axis["right"].toggle(all=True)

        put_data_into_axis(other_axis, get_data_and_labels(axis_data))
        
        if not is_third_axis_or_more:
            is_third_axis_or_more = True

first_axis.set_xlabel('Heure')

first_axis.legend()
first_axis.grid()
first_axis.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=timezone('Europe/Paris')))
first_axis.fmt_xdata = mdates.DateFormatter('%d/%m/%Y %H:%M:%S', tz=timezone('Europe/Paris'))

plt.show()
