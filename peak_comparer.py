from PointData import P2Point, LineParts
import os
import glob
from math import sqrt


def st_dev(data):
    avg_data = sum(data) / len(data)
    stdev = sum([(x - avg_data)**2 for x in data])
    stdev /= len(data) - 1
    return sqrt(stdev)

# Get to the files
script_path = os.path.join(os.path.dirname(__file__), "TR")
data_folders = [x[0] for x in os.walk(script_path)][1:]
files_in_folder = []

for folder in data_folders:
    files_in_folder.append(glob.glob(folder + '/*.txt'))


# Parse them
print('Parsing data files')

chan1_data = []
chan2_data = []
time_unit_scale = 1

for folder_num in range(0, len(data_folders)):
#for folder_num in range(0, 1):

    print(data_folders[folder_num])

    chan1_data.append([])
    chan2_data.append([])

    for file_path in files_in_folder[folder_num]:
        chan1_data[folder_num].append([])
        chan2_data[folder_num].append([])

        opened_file = open(file_path, "r")
        opened_file.readline()  # Omit headers line
        opened_file.readline()  # Only important unit is for time (micro seconds)
        opened_file.readline()  # Omit empty line

        line = opened_file.readline()

        while line != '':
            chan1_data[folder_num][len(chan1_data[folder_num]) - 1].append(P2Point(line, LineParts.CHAN_A))
            chan2_data[folder_num][len(chan2_data[folder_num]) - 1].append(P2Point(line, LineParts.CHAN_B))
            line = opened_file.readline()

        opened_file.close()

print("Parsing completed. Finding deltas of peaks...")

avg_deltas = []
deltas_stdevs = []

# Find peaks
for folder_num in range(0, len(chan1_data)):

    print(data_folders[folder_num])
    deltas = []

    for point_set_num in range(0, len(chan1_data[folder_num])):

        # Initialize points
        peak1_point = chan1_data[folder_num][point_set_num][0]
        peak2_point = chan2_data[folder_num][point_set_num][0]

        # Get peaks in this set
        for point_number in range(0, len(chan1_data[folder_num][point_set_num])):

            if float(chan1_data[folder_num][point_set_num][point_number].chan) > float(peak1_point.chan):
                peak1_point = chan1_data[folder_num][point_set_num][point_number]
            if float(chan2_data[folder_num][point_set_num][point_number].chan) > float(peak2_point.chan):
                peak2_point = chan2_data[folder_num][point_set_num][point_number]

        # Count delta time
        deltas.append(time_unit_scale * (float(peak2_point.time) - float(peak1_point.time)))

    avg_deltas.append(sum(deltas) / len(deltas))
    print(f'delta = {avg_deltas[len(avg_deltas) -1]}')
    deltas_stdevs.append(st_dev(deltas))


print('Found. Getting velocities...')

vs = []
length1 = 9.42  # cm
length2 = 4.82  # cm

for folder_num in range(0, len(chan1_data)):

    print(data_folders[folder_num])

    if data_folders[folder_num].split(os.sep).pop()[0] == '1':
        vs.append(length1 / avg_deltas[folder_num])
    else:
        vs.append(length2 / avg_deltas[folder_num])

print('Got. Initializing dictionary...')

plot_dict = dict()

for i in range(400, 3100, 100):
    plot_dict[i] = []

print('Adding velocity data to dictionaries...')
for folder_num in range(0, len(chan1_data)):

    print(data_folders[folder_num])

    V = data_folders[folder_num].split(os.sep).pop().split('v')[1]
    if len(V) > 2:
        V = V[:2]

    V = int(V) * 1e2

    plot_dict[V].append(vs[folder_num])


print('Averaging values in dict...')
for val_list in plot_dict:
    plot_dict[val_list] = sum(plot_dict[val_list]) / len(plot_dict[val_list])

print(plot_dict)







