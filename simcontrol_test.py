import asyncio
import csv
import math

import matplotlib.pyplot as plt
import cmapi
from cmapi import ApoServer, SimControlInteractive

<<<<<<< HEAD

PID = 2771420
HOST = "localhost"
RUN_NAME = "live_run_1"
=======
"""
Run with:

chmod +x 
run_simcontrol.sh

Notes:
- Requires CarMaker 14.1.1 Python API
- Requires a running CarMaker for Simulink application
- PID may need to be updated for your session
"""

PID = 2771420
HOST = "localhost"
RUN_NAME = "test_run_1"
>>>>>>> aa0d174 (add cmapi live logger)

signals = [
    ("Time", "Time [s]", lambda x: x),
    ("Car.v", "Speed [km/h]", lambda x: x * 3.6),
    ("Driver.Steer.Ang", "Steer [deg]", math.degrees),
    ("Car.ax", "ax [m/s²]", lambda x: x),
    ("Car.ay", "ay [m/s²]", lambda x: x),
    ("Car.az", "az [m/s²]", lambda x: x),
]


async def main():
<<<<<<< HEAD
    # connect to CarMaker
=======
    # connect to CarMaker (Server)
>>>>>>> aa0d174 (add cmapi live logger)
    sinfo = cmapi.ApoServerInfo(pid=PID)

    master = ApoServer()
    master.set_sinfo(sinfo)
    master.set_host(HOST)

    sim_control = await SimControlInteractive.create_with_master(master)
    await sim_control.connect()
    print("Connected.")

<<<<<<< HEAD
    # storage
=======
    # storage variables
>>>>>>> aa0d174 (add cmapi live logger)
    rows = []

    started_logging = False
    saw_old_run = False
    last_time = None
    frozen_count = 0

    time_data = []
    plot_data = [[] for _ in signals[1:]]

    # live plot
    plt.ion()
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    speed_line, = axes[0].plot([], [], label="Speed [km/h]")
    steer_line, = axes[0].plot([], [], label="Steer [deg]")

    ax_line, = axes[1].plot([], [], label="ax [m/s²]")
    ay_line, = axes[1].plot([], [], label="ay [m/s²]")
    az_line, = axes[1].plot([], [], label="az [m/s²]")

    lines = [speed_line, steer_line, ax_line, ay_line, az_line]

    axes[0].set_ylabel("Speed / Steer")
    axes[1].set_ylabel("Accelerations")
    axes[1].set_xlabel("Time [s]")

    axes[0].grid(True)
    axes[1].grid(True)

    axes[0].legend(loc="upper right")
    axes[1].legend(loc="upper right")

    while True:
        raw_time = (await sim_control.simio.dva_read_async("Time"))[0]

        if not started_logging and raw_time > 1.0:
            saw_old_run = True

        if not started_logging:
            if saw_old_run:
                if raw_time < 0.1:
                    print("Detected new run reset. Start logging.")
                    started_logging = True
                    last_time = None
                    frozen_count = 0
            else:
                if 0.0 <= raw_time < 0.1:
                    print("Starting logging from current run.")
                    started_logging = True
                    last_time = None
                    frozen_count = 0

        if started_logging:
            row = []

            for name, label, convert in signals:
                raw_value = (await sim_control.simio.dva_read_async(name))[0]
                value = convert(raw_value)
                row.append(value)

            current_time = row[0]
            rows.append(row)

            # save for plot
            time_data.append(current_time)
            for k in range(len(signals) - 1):
                plot_data[k].append(row[k + 1])
                lines[k].set_data(time_data, plot_data[k])

            # print every loop
            print(
                " | ".join(
                    f"{signals[k][1]}: {row[k]:.3f}"
                    for k in range(len(signals))
                )
            )

            # update plot every loop
            for ax in axes:
                ax.relim()
                ax.autoscale_view()

            plt.pause(0.001)

            # stop conditions
            if last_time is not None:
                if current_time < last_time:
                    print("Detected time reset. Ending current log.")
                    break

                if abs(current_time - last_time) < 1e-9:
                    frozen_count += 1
                else:
                    frozen_count = 0

            last_time = current_time

            if frozen_count > 20:
                print("Simulation time stopped advancing. Ending log.")
                break

        await asyncio.sleep(0.01)

    await sim_control.disconnect()
    print("Disconnected.")

    csv_path = f"{RUN_NAME}.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([label for _, label, _ in signals])
        writer.writerows(rows)

    print(f"Saved to {csv_path}")

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    cmapi.Task.run_main_task(main())