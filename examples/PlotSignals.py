# for reading and plot signals
import time
import math
import csv
import matplotlib.pyplot as plt
from pycarmaker import CarMaker, Quantity


cm = CarMaker("localhost", 16660)
cm.connect()

# check signal names in IPGcontrol
signals = [
    ("Car.v",            "Speed [km/h]", lambda x: x * 3.6,    0),
    ("Driver.Steer.Ang", "Steer [deg]",  math.degrees,         0),
    ("Car.Yaw",          "Yaw [deg]",    math.degrees,         1),
    ("Car.ax",           "ax [m/s²]",    lambda x: x,          2),
    ("Car.ay",           "ay [m/s²]",    lambda x: x,          2),
    ("Car.az",           "az [m/s²]",    lambda x: x,          2),
]


quantities = []
for name, label, convert, subplot in signals:
    q = Quantity(name, Quantity.FLOAT)
    cm.subscribe(q)
    quantities.append(q)

cm.read()
cm.read()


dt = 0.01
samples = 1000

time_data = []
data = [[] for _ in signals]


n_subplots = max(subplot for _, _, _, subplot in signals) + 1
fig, axes = plt.subplots(n_subplots, 1, sharex=True, figsize=(10, 8))
if n_subplots == 1:
    axes = [axes]

lines = []
for _, label, _, subplot in signals:
    line, = axes[subplot].plot([], [], label=label)
    axes[subplot].grid(True)
    axes[subplot].legend(loc="upper right")
    lines.append(line)

axes[-1].set_xlabel("Time [s]")


plt.ion()

for i in range(samples):
    cm.read()
    time_data.append(i * dt)

    for k, (name, label, convert, subplot) in enumerate(signals):
        value = convert(quantities[k].data)
        data[k].append(value)
        lines[k].set_data(time_data, data[k])

    for ax in axes:
        ax.relim()
        ax.autoscale_view()

    plt.pause(0.001)
    time.sleep(dt)
    
    # save as csv 
    with open("run_data.csv", "w", newline="") as f: # change testname if needs
        writer = csv.writer(f)
        
        writer.writerow(["time"] + [label] for _, label, _  , _ in signals)
        for i in range(len(time_data)):
            writer.writerow(([time_data[i]] + [data[k][i] for k in range(len(signals))]))
            

plt.ioff()
plt.show()

