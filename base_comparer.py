from PointData import P2Point, LineParts
import os
import glob
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt


def st_dev(data):
    avg_data = sum(data) / len(data)
    stDev = sum([(x - avg_data)**2 for x in data])
    stDev /= len(data) - 1
    return sqrt(stDev)


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

print("Parsing completed. Finding deltas of bases...")

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

        # Get the bases, assuming that they would be first points with value >= of 0.25 of peak_point.
        # 0.25 was selected empirically to remove most of the noise.

        base1_point = chan1_data[folder_num][point_set_num][0]
        base2_point = chan2_data[folder_num][point_set_num][0]

        for point_number in range(0, len(chan1_data[folder_num][point_set_num])):
            if float(chan1_data[folder_num][point_set_num][point_number].chan) >= 0.25 * float(peak1_point.chan):
                base1_point = chan1_data[folder_num][point_set_num][point_number]
                break

        for point_number in range(0, len(chan2_data[folder_num][point_set_num])):
            if float(chan2_data[folder_num][point_set_num][point_number].chan) >= 0.25 * float(peak2_point.chan):
                base2_point = chan1_data[folder_num][point_set_num][point_number]
                break

        # Count delta time
        deltas.append(time_unit_scale * (float(base2_point.time) - float(base1_point.time)))

    avg_deltas.append(sum(deltas) / len(deltas))
    print(f'delta = {avg_deltas[len(avg_deltas) -1]}')
    deltas_stdevs.append(st_dev(deltas))


print('Found. Getting velocities with uncertainties...')

vs = []
u_vs = []
u_s = 0.01e-2  # in m
length1 = 9.42  # cm
length2 = 4.82  # cm

for folder_num in range(0, len(chan1_data)):

    print(data_folders[folder_num])

    s = 0

    if data_folders[folder_num].split(os.sep).pop()[0] == '1':
        s = length1
    else:
        s = length2

    vs.append(s / avg_deltas[folder_num])
    u_vs.append(
        sqrt((u_s / avg_deltas[folder_num]) ** 2 + (s * deltas_stdevs[folder_num] / (avg_deltas[folder_num] ** 2)) ** 2)
    )


print('Got. Initializing dictionary...')

plot_dict = dict()
uncertainties_dict = dict()

for i in range(400, 3100, 100):
    plot_dict[i] = []
    uncertainties_dict[i] = []

print('Adding velocity data to dictionaries...')
for folder_num in range(0, len(chan1_data)):

    print(data_folders[folder_num])

    V = data_folders[folder_num].split(os.sep).pop().split('v')[1]
    if len(V) > 2:
        V = V[:2]

    V = int(V) * 1e2

    plot_dict[V].append(vs[folder_num])
    uncertainties_dict[V].append(u_vs[folder_num])

print(plot_dict)
print(uncertainties_dict)

print('Averaging values in dicts...')
for key in plot_dict:
    plot_dict[key] = sum(plot_dict[key]) / len(plot_dict[key])
    uncertainties_dict[key] = sum(uncertainties_dict[key]) / len(uncertainties_dict[key])

print(plot_dict)
print(uncertainties_dict)

print('Getting data for plot...')
x = []
y = []
u_v = []

for key in plot_dict:
    # plot_dict[key] = sum(plot_dict[key]) / len(plot_dict[key])
    # It's U in volts divided by 10 cm = 1e-2 m, which is the length of area with homogeneous electric field.
    x.append((key / 1e-1))
    # Velocity is not in cm / us thus it should be rescaled by 1e-2 / 1e-6 = 1e4
    y.append(plot_dict[key] * 1e4)
    # Uncertainties are
    u_v.append(uncertainties_dict[key] * 1e4)

print('Counting uncertainties...')
u_E = [10 for x_val in x]

print('Counting trend line coeffs...')
trend = np.polyfit(x=x, y=y, deg=2)

a = float(trend[0])
b = float(trend[1])
c = float(trend[2])

trend_y_vals = []
trend_x_vals = []

for x_val in range(3000, 31000):
    trend_y_vals.append(a * (x_val * x_val) + b * x_val + c)
    trend_x_vals.append(x_val)

print('Plotting...')

print(u_vs)
print(u_E)

plt.errorbar(x, y, xerr=u_E, yerr=u_v, fmt='o')
plt.plot(trend_x_vals, trend_y_vals)
plt.ylabel('v (m / s)')
plt.xlabel('E (V / m)')
plt.show()

print('Finished.')
