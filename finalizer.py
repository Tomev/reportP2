import numpy as np
from math import sqrt, ceil
import matplotlib.pyplot as plt

E = [4000.0, 5000.0, 6000.0, 7000.0, 8000.0, 9000.0, 10000.0, 11000.0, 12000.0, 13000.0, 14000.0, 15000.0, 16000.0, 17000.0, 18000.0, 19000.0, 20000.0, 21000.0, 22000.0, 23000.0, 24000.0, 25000.0, 26000.0, 27000.0, 28000.0, 29000.0, 30000.0]
u_E = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

v_mid = [1967.507563683817, 2754.1121967433296, 2860.155389711077, 3303.8327070484092, 3770.8463319490797, 4211.488224983781, 4670.49747090135, 5122.67095943773, 5590.896451460232, 6054.076862913025, 6513.368518488584, 6974.155656164995, 7447.4068462055475, 7919.285573840541, 8406.96122868986, 8923.404248465697, 9438.595897897289, 9899.36337995089, 10446.310238334934, 10974.36184263928, 11484.136638546455, 12028.900499092439, 12584.90256820592, 13155.586546920835, 13945.725185965473, 14282.550900481981, 14925.958726932711]
v_peak = [1940.10627499059, 2435.6421950840186, 2840.7086934476856, 3291.573741914031, 3741.337438154025, 4205.362961940324, 4663.185498585765, 5124.352363172149, 5599.6226798745665, 6069.668276677691, 6534.792714111471, 7005.335045153709, 7482.18486270738, 7984.82894052917, 8484.957715727543, 9051.852681598622, 9573.311424213358, 10052.137704173512, 10602.084829781665, 11138.238435537047, 11676.199148538035, 12235.946687745394, 12813.84091501093, 13442.96834271769, 14281.806753263145, 14706.691029357778, 15539.092296024906]
u_v_mid = [16.626768053362852, 920.7144631940888, 24.156348988963423, 21.265222564629177, 78.51924533820657, 26.868581862752542, 27.415787319620566, 32.082206839590235, 35.62009821301411, 32.12488402586501, 32.7911750074625, 30.601459803293313, 45.507132069806666, 23.761379291261804, 43.78278801721636, 63.81869271582654, 66.53453935004718, 71.62495792443546, 72.39941902059736, 86.3181138990365, 89.47952122648749, 86.24839853473648, 109.52306113885368, 120.47428718277249, 1163.8559826028068, 128.4508633961017, 148.62757370194214]
u_v_peak = [16.74191802902827, 314.24045664483367, 24.477749149691544, 25.821599580885223, 20.932770689482854, 27.243558019380284, 29.15092608354166, 33.42128818792276, 33.15286419640866, 33.7291401492823, 28.08068728247306, 34.37447556018603, 41.146221031108965, 32.821068312441525, 55.20175326714631, 78.268327762063, 75.59082707197807, 80.33348051801744, 63.69121628762421, 79.41375293138934, 83.91940615657937, 82.34918473609656, 97.15785721929063, 110.62032928448185, 1207.3014024489328, 231.54108489966268, 236.54416251005458]

v_avg = []
u2_int = []
u2_ext = []

for i in range(len(v_peak)):
    u = 1.0 / (1.0 / u_v_mid[i] ** 2.0 + 1.0 / u_v_peak[i] ** 2.0)
    u2_int.append(u)
    v = (v_mid[i] / u_v_mid[i]**2 + v_peak[i] / u_v_peak[i]**2) * u
    v_avg.append(v)
    u_e = ((v_mid[i] - v)**2.0 / u_v_mid[i] + (v_peak[i] - v)**2.0 / u_v_peak[i]) * u
    u2_ext.append(u_e)

u_v = []
for i in range(len(u2_int)):
    u_v.append(sqrt(max(u2_int[i], u2_ext[i])))

print('Noise removal...')
for i in range(len(u_E) - 1, 0, -1):
    if u_v[i] > v_avg[i]:
        del u_v[i]
        del v_avg[i]
        del E[i]
        del u_E[i]

print('Rounding values...')
for i in range(len(u_v)):
    u_v[i] = round(u_v[i])
    v_avg[i] = ceil(v_avg[i] / 100) * 100


print('Counting trend line coeffs...')
trend, cov = np.polyfit(x=E, y=v_avg, deg=2, cov=True)

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
print(E)
print(v_avg)
print(u_v)
print(u_E)
print('=======================================')

x_string = ''
y_string = ''

for i in range(len(v_avg)):
    x_string += str(E[i]) + '&'
    y_string += '$' + str(int(str(v_avg[i]).split('.')[0])/1000.0) + '\pm' + str(u_v[i] / 1000.0)[:-1] + '$&'


print(len(v_avg))
print(len(u_v))
print(x_string)
print(y_string)

chi = 0

for i in range(len(E)):
    chi += ((v_avg[i] - (a * E[i]**2 + b * E[i] + c)) / u_v[i])**2

chi /= len(E) - 1
print(f'chi = {chi}')

plt.errorbar(E, v_avg, xerr=u_E, yerr=u_v, fmt='o')
plt.plot(trend_x_vals, trend_y_vals)
plt.ylabel('v (m / s)')
plt.xlabel('E (V / m)')
plt.show()

print('Finished.')


