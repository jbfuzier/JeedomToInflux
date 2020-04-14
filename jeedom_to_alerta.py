import datetime

import config
import jsonrpcclient
import requests
import logging
import logging.config
import pickle
import shutil
logging.config.dictConfig(config.LOGGING_CONF)


class jeedom_api:
    def __init__(self):
        self._load_db()

    def request_jeedom(self, command, **kwargs):
        try:
            response = jsonrpcclient.request(config.JEEDOM_API_URL, command, apikey=config.API_KEY, **kwargs)
            return response
        except Exception as e:
            raise e
            logging.exception(e)
        return None

    def getTime(self):
        epoch = self.request_jeedom('datetime')
        return datetime.datetime.fromtimestamp(epoch)

    def isOk(self):
        return self.request_jeedom("jeedom::isOk")

    def getMessages(self):
        return self.request_jeedom("message::all")


    def _load_db(self):
        self.db = {
            'last_timestamp': None
        }
        try:
            with open(config.JEEDOM_ALERTA_DB_PATH) as f:
                self.db = pickle.load(f)
        except IOError:
            logging.warning("No db found at %s"%config.DB_PATH)

    def save_db(self):
        with open(config.JEEDOM_ALERTA_DB_PATH + '.tmp', 'wb') as f:
            pickle.dump(self.db, f)
        shutil.move(config.JEEDOM_ALERTA_DB_PATH + '.tmp', config.JEEDOM_ALERTA_DB_PATH)

j = jeedom_api()
messages = j.getMessages()

last_timestamp = j.db['last_timestamp']
if last_timestamp is None:
    last_timestamp = datetime.datetime.fromtimestamp(0)
new_last_timestamp = last_timestamp
"""
resource	string	Required resource under alarm
event	string	Required event name
environment	string	environment, used to namespace the resource
severity	string	see severity_table table
correlate	list	list of related event names
status	string	see status_table table
service	list	list of effected services
group	string	used to group events of similar type
value	string	event value
text	string	freeform text description
tags	set	set of tags
attributes	dict	dictionary of key-value pairs
origin	string	monitoring component that generated the alert
type	string	event type
createTime	datetime	time alert was generated at the origin
timeout	integer	seconds before alert is considered stale
rawData	string	unprocessed raw data
"""
for m in messages:
    if m['plugin'] == 'update':
        continue
    timestamp_dt = datetime.datetime.strptime(m['date'], '%Y-%m-%d %H:%M:%S')
    if timestamp_dt < last_timestamp:
        logging.debug("Ignoring old message %s"%m)
        continue
    payload = {
          "environment": "Production",
          "event": m['message'],
          "resource": "jeedom."+m['plugin'],
          "timeout": 365 * 24 * 3600,
          "service": [
            m['plugin']
          ],
          "severity": "major",
          "text": m['message'],
    }
    r = requests.post(config.ALERTA_API_URL, json=payload)
    if not 200 <= r.status_code <300:
        logging.error("Got error while creating alert in alerta : %s"%r.text)
    if timestamp_dt > new_last_timestamp:
        new_last_timestamp = timestamp_dt
j.db['last_timestamp'] = new_last_timestamp
j.save_db()