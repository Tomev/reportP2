from PointData import P2Point, LineParts
import os
import glob
import numpy as np
from math import sqrt, ceil
import matplotlib.pyplot as plt


def st_dev(data):
    avg_data = sum(data) / len(data)
    stDev = sum([(x - avg_data) ** 2 for x in data])
    stDev /= len(data) - 1
    return sqrt(stDev)


# Get to the files
script_path = os.path.join(os.path.dirname(__file__), "TR")
data_folders = [x[0] for x in os.walk(script_path)][1:]
files_in_folder = []

for folder in data_folders:
    files_in_folder.append(glob.glob(folder + '/*.txt'))

# Parse them
print('Parsing data files...')

chan1_data = []
chan2_data = []
time_unit_scale = 1

for folder_num in range(0, len(data_folders)):
    # for folder_num in range(0, 1):

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
    print(f'delta = {avg_deltas[len(avg_deltas) - 1]}')
    deltas_stdevs.append(st_dev(deltas))

print(deltas_stdevs)

folder_parts = []
for folder_name in data_folders:
    folder_parts.append(folder_name.split('\\')[2])
print(folder_parts)

print(len(folder_parts))

for i in range(len(avg_deltas)):
    avg_deltas[i] = ceil(avg_deltas[i] / 0.01) * 0.01
    deltas_stdevs[i] = ceil(deltas_stdevs[i] / 0.01) * 0.01
print(avg_deltas)
print(deltas_stdevs)

avg_delta_table = ''
for i in range(len(avg_deltas)):
    avg_delta_table += str(avg_deltas[i])[:5] + '&'
print(avg_delta_table)

print(len(avg_deltas))

avg_delta_u_table = ''

for i in range(len(deltas_stdevs)):
    avg_delta_u_table += str(deltas_stdevs[i])[:5] + '&'
print(avg_delta_u_table)

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

v_string = ''
uv_string = ''

for i in range(len(vs)):
    v_string += str(vs[i])[:5] + '&'
    uv_string += str(u_vs[i])[:5] + '&'

print(v_string)
print(uv_string)

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

print('Rounding values...')
for i in range(len(u_v)):
    u_v[i] = round(u_v[i])
    x[i] = ceil(x[i] / 100) * 100
    y[i] = ceil(y[i] / 100) * 100
    u_v[i] = ceil(u_v[i] / 100) * 100

print('Counting trend line coeffs...')
trend, cov = np.polyfit(x=x, y=y, deg=2, cov=True)

a = float(trend[0])
b = float(trend[1])
c = float(trend[2])

trend_y_vals = []
trend_x_vals = []

for x_val in range(3000, 31000):
    trend_y_vals.append(a * (x_val * x_val) + b * x_val + c)
    trend_x_vals.append(x_val)

print(trend)

for el in np.diag(cov):
    print(sqrt(el))

print('Plotting...')

print('=======================================')
print(x)
print(y)
print(u_v)
print(u_E)
print('=======================================')

x_string = ''
y_string = ''

for i in range(len(y)):
    x_string += str(x[i]) + '&'
    y_string += '$' + str(int(str(y[i]).split('.')[0])/1000.0) + '\pm' + str(u_v[i] / 1000.0) + '$&'

print(x_string)
print(y_string)

chi = 0

for i in range(len(x)):
    chi += ((y[i] - (a * x[i]**2 + b * x[i] + c)) / u_v[i])**2

chi /= len(x) - 1
print(f'chi = {chi}')


plt.errorbar(x, y, xerr=u_E, yerr=u_v, fmt='o')
plt.plot(trend_x_vals, trend_y_vals)
plt.ylabel('v (m / s)')
plt.xlabel('E (V / m)')
plt.show()

print('Finished.')
