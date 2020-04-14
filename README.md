# JeedomToInflux
Python script to periodicaly export jeedom metrics to influxdb




### 0. Requirements 
Python requirements (see requirements.txt) : `pip install -r requirements.txt`
The script uses Jeedom API to query all history data (command must have the history check box set)
All the metrics since the last run are fetched and send to InfluxDB
Metrics can then be graphed with Grafana for example


### 1. Quick start
Copy `config.py.sample` to `config.py` and edit it accordingly

Run the script periodically (using cron for example)
