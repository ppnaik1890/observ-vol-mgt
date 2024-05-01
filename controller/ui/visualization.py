from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import os
import datetime
from datetime import datetime

current_path = os.path.dirname(os.path.realpath(__file__))
flaskApp = Flask(__name__, template_folder=current_path, static_folder=f"{current_path}/temp")

time_series = {}
insights = ""


def fill_time_series(extracted_signals):
    for extracted_signal in extracted_signals:
        time_series_name = extracted_signal.metadata["__name__"]
        time_series[time_series_name] = extracted_signal.time_series


def fill_insights(the_insights):
    global insights
    insights = the_insights


@flaskApp.route('/')
def index():
    series_names = list(time_series.keys())
    return render_template('index.html', insights=insights, series_names=series_names)


@flaskApp.route('/signal_visualization', methods=['POST'])
def visualize():
    selected_series = request.form.getlist('timeSeries')
    plt.figure(figsize=(10, 6))

    # Plot selected time series
    all_timestamps = []
    for series_name in selected_series:
        if series_name in time_series:
            time_stamps, data = zip(*time_series[series_name])
            data = [float(d) for d in data]
            time_stamps, data = zip(*sorted(zip(time_stamps, data), key=lambda x: x[1]))
            all_timestamps.extend(time_stamps)
            time_values = [datetime.fromtimestamp(time_stamp) for time_stamp in time_stamps]
            plt.scatter(time_values, data, label=series_name)
        else:
            return "Error: Selected time series not found."

    # Plotting settings
    plt.title('Time Series Visualization')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.xticks(rotation=45, fontsize=6)
    plt.grid(True)
    plt.legend()

    all_timestamps.sort()  # Sort timestamps in ascending order
    num_ticks = min(10, len(all_timestamps))  # Choose minimum of 10 or the number of timestamps
    step = max(1, len(all_timestamps) // num_ticks)  # Calculate step size for selecting timestamps
    selected_timestamps = all_timestamps[::step]  # Select timestamps at specified intervals
    tick_labels = [datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') for ts in
                   selected_timestamps]  # Format tick labels
    plt.xticks([datetime.fromtimestamp(ts) for ts in selected_timestamps], tick_labels, rotation=45, fontsize=6)

    plt.savefig(f"{current_path}/temp/plot.png", dpi=120, bbox_inches='tight')  # Save the plot as an image
    plt.close()

    return render_template('signal_visualize.html')
