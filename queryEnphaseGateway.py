import io
import threading
from flask import Flask, render_template_string, send_file
from dotenv import load_dotenv
from matplotlib.ticker import MaxNLocator
from TokenManager import TokenManager
from RequestStorage import RequestStorage
from datetime import datetime
from tzlocal import get_localzone
import os
import warnings
import requests
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import matplotlib.animation as animation
import time

# Use the Agg backend for Matplotlib
matplotlib.use('Agg')

# Initialize Flask app
app = Flask(__name__)

# Get the local timezone
local_tz = get_localzone()

# Suppress InsecureRequestWarning - these requests are made to your local IQ Gateway, presumably you trust it
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Load the variables from the .env file
load_dotenv()

# Instantiate token manager and retrieve it
token_manager = TokenManager(expiration_time=3600)

# KEEPING here during dev so I can explore API data directly
# Sample data request from all inverters
# data_req_headers = {
#     'Accept': 'application/json',
#     'Authorization': f'Bearer {token}'
# }
# resp = requests.get(
#     os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/api/v1/production/inverters', # Works
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/meters/reports/consumption', # Works
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/meters/reports/production', # Works
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/meters/reports/', # Works
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/meters/readings', # Works
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/production.json', # Works
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/livedata/status', # Works
#     # More info on why this route is not working in README
#     # May need to register token here (https://envoy.local/home#auth)
#     # os.getenv('ENPHASE_IQ_GATEWAY_IP') + '/ivp/pdm/energy', # AUTH REQUIRED err
#     headers=data_req_headers,
#     verify=False
# )
# print(resp)
# response_data = json.loads(resp.text)
# print(response_data)
# quit()

# This contains all API data w/ epochs as keys and watts as values
chartData = {}
# Max axis points, can later base on cumulative time
maxPoints = 96
# How often to query for new data (in seconds)
queryInterval = 60 * 15
# Reference to png image of last updated state of chart (Shown in browser)
img = None

# Track historical api requests in this class to help fill out chart on first load
request_storage = RequestStorage(reqPullLimit=maxPoints)
with request_storage as rs:
    prevSavedChartData = rs.get_saved_req()

# If we have previously saved chart data utilize it
if len(prevSavedChartData) > 0:
    chartData = prevSavedChartData

def fetch_data(endpoint):

    with token_manager as tm:
        token = tm.get_token()

    data_req_headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(
        os.getenv('ENPHASE_IQ_GATEWAY_IP') + endpoint,
        headers=data_req_headers,
        verify=False
    )
    response.raise_for_status()
    return response.json()

def process_data(prod_cons_data):
    prod, net_con, tot_con = prod_cons_data
    epoch = prod['createdAt']

    # Check if epoch is already in chartData (can happen for low poll intervals)
    if epoch in chartData:
        return

    # For debugging visual display of the graph and getting styling right
    # for i in range(0, 96):
    #     chartData[epoch-i] = [
    #         prod['cumulative']['currW'],
    #         net_con['cumulative']['currW'],
    #         tot_con['cumulative']['currW']
    #     ]

    # Save in Database for future reference
    with request_storage as rs:
        rs.save_req(
            epoch,
            prod['cumulative'],
            net_con['cumulative'],
            tot_con['cumulative']
        )

    # "whDlvdCum" or "whRcvdCum" may be more applicable here instead of "currW"
    chartData[epoch] = [
        prod['cumulative']['currW'],
        net_con['cumulative']['currW'],
        tot_con['cumulative']['currW']
    ]

    # For now only store N amount of entries
    # print(json.dumps(chartData))
    if len(chartData) > maxPoints:
        oldest_epoch = min(chartData.keys())
        del chartData[oldest_epoch]

def plot_data():
    global img
    # Build out from global data just appended to
    epochs = sorted(chartData.keys())
    production, net_consumption, tot_consumption = zip(*[chartData[epoch] for epoch in epochs])
    times = [datetime.fromtimestamp(epoch, local_tz) for epoch in epochs]

    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(times, production, label='Production (W)', marker='o')
    ax.plot(times, net_consumption, label='Net Consumption (W)', marker='o')
    ax.plot(times, tot_consumption, label='Tot Consumption (W)', marker='o')
    ax.set_xlabel('Time')
    ax.set_ylabel('Watts')
    ax.set_title('Solar Panel Production and Consumption')
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.4)

    # Use AutoDateLocator and DateFormatter to handle time-based data
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    # Use MaxNLocator to limit the number of x-axis labels
    ax.xaxis.set_major_locator(MaxNLocator(nbins='auto', prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins='auto', prune='both'))

    # Set y-axis limits manually to avoid outliers
    ax.set_ylim([
        min(min(production), min(net_consumption), min(tot_consumption)) * 1.1,
        max(max(production), max(net_consumption), max(tot_consumption)) * 1.1
    ])

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

def update_plot():
    while True:
        # Get new data
        prod_cons_data = fetch_data('/ivp/meters/reports/')
        process_data(prod_cons_data)
        plot_data()
        time.sleep(queryInterval)

@app.route('/')
def index():
    return render_template_string('''
        <html>
            <head><title>Solar Panel Production and Consumption</title></head>
            <body>
                <h1>Solar Panel Production and Consumption</h1>
                <img src="/plot.png" alt="Solar Panel Production and Consumption">
            </body>
        </html>
    ''')

@app.route('/plot.png')
def plot_png():
    return send_file(io.BytesIO(img.getvalue()), mimetype='image/png')

if __name__ == "__main__":
    # Start the background thread to update the plot
    threading.Thread(target=update_plot, daemon=True).start()
    app.run(host='0.0.0.0', port=5001)
