import datetime
import requests
from pprint import pprint
import time
import pytz
import config
import cPickle as pickle
import jsonrpcclient
import logging.config
import shutil
import config
from influxdb import InfluxDBClient

logging.config.dictConfig(config.LOGGING_CONF)


script_stats = {
    'new_results': 0,
    'duration': 0,
    'start_time': time.time()
}

class jeedom_api:
    def __init__(self):
        pass

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

    def getCommands(self, id=None, equipment_id=None, historized_only=False):
        if id and equipment_id:
            raise Exception("Can not have a command id and equipment_id at the same time")
        if id:
            """
                [{u'alert': [],
                 u'configuration': {u'maxValue': u'',
                                    u'minValue': u'',
                                    u'topic': u'esp_tempsalon/in{hum}'},
                 u'currentValue': 61.2329,
                 u'display': {u'invertBinary': u'1'},
                 u'eqLogic_id': u'266',
                 u'eqType': u'MQTT',
                 u'generic_type': None,
                 u'id': u'4221',
                 u'isHistorized': u'1',
                 u'isVisible': u'1',
                 u'logicalId': u'hum',
                 u'name': u'hum',
                 u'order': u'2',
                 u'subType': u'numeric',
                 u'template': [],
                 u'type': u'info',
                 u'unite': u'%',
                 u'value': None},]
            """
            r = self.request_jeedom("cmd::byId", id=id)
        elif equipment_id:
            # Retourne la liste des commandes pour un equipement
            """
                [{u'alert': [],
                 u'configuration': {u'maxValue': u'',
                                    u'minValue': u'',
                                    u'topic': u'esp_tempsalon/in{uptime}'},
                 u'currentValue': 444504,
                 u'display': {u'invertBinary': u'1'},
                 u'eqLogic_id': u'266',
                 u'eqType': u'MQTT',
                 u'generic_type': None,
                 u'id': u'4219',
                 u'isHistorized': u'0',
                 u'isVisible': u'1',
                 u'logicalId': u'uptime',
                 u'name': u'uptime',
                 u'order': u'5',
                 u'subType': u'numeric',
                 u'template': [],
                 u'type': u'info',
                 u'unite': u'',
                 u'value': None},]
            """
            r = self.request_jeedom("cmd::byEqLogicId", eqLogic_id=equipment_id)
        else:
            r = self.request_jeedom("cmd::all")
        if historized_only:
            return [e for e in r if e['isHistorized'] in ['1', 1, True, 'true']]
        else:
            return r

    def getEquipments(self, id=None, full=False, enabled_only=True):
        if not id:
            # Retourne la liste de tous les equipements
            """
                [{u'category': {u'automatism': u'0',
                               u'default': u'0',
                               u'energy': u'1',
                               u'heating': u'0',
                               u'light': u'0',
                               u'multimedia': u'0',
                               u'security': u'0'},
                 u'comment': None,
                 u'configuration': {u'1': {u'help': u'Si cette fonction est activ\xe9e, le Wall Plug sera toujours sur ON (la charge sera donc toujours activ\xe9e), ne r\xe9agira plus aux messages cadre et on ne pourra plus le d\xe9sactiver en appuyant le bouton B. La fonction always on transforme le Wall Plug en un dispositif de mesure de puissance et d\u2019\xe9nergie consomm\xe9e par la charge. La charge connect\xe9e ne se d\xe9sactivera pas lors de la r\xe9ception d\u2019une trame d\u2019alarme par un autre dispositif Z-Wave (le param\xe8tre 35 est ignor\xe9). Dans le mode de always on, la charge connect\xe9e pourra \xeatre d\xe9sactiv\xe9e lors d\u2019un d\xe9passement du seuil de puissance d\xe9fini par l\u2019utilisateur (param\xe8tre 70). Dans ce cas, la charge connect\xe9e se r\xe9activera en appuyant sur le bouton B ou en envoyant une trame de contr\xf4le.',
                                           u'list': {u'function activated': u'Fonction active',
                                                     u'function inactive': u'Fonction d\xe9sactiv\xe9e'},
                                           u'name': u'Fonction always on (toujours actif).'},
                                    u'16': {u'help': u'Ce param\xe8tre d\xe9finit le comportement du Wall Plug une fois le retour de l`alimentation.',
                                            u'list': {u'Wall Plug does not memorize its state after a power failure': u'Le Wall Plug ne m\xe9morise pas l`\xe9tat du dispositif apr\xe8s la d\xe9sactivation de l`alimentation.',
                                                      u'Wall Plug memorizes its state after a power failure': u'Le Wall Plug garde l`\xe9tat du dispositif apr\xe8s la d\xe9sactivation de l`alimentation.'},
                                            u'name': u'M\xe9morisation de l`\xe9tat du dispositif apr\xe8s une chute d`alimentation.'},
                                    u'34': {u'help': u'Ce param\xe8tre d\xe9termine \xe0 quels types d`alarme du r\xe9seau Z-Wave va r\xe9agir le Wall Plug.',
                                            u'list': {u'ALARM ALL': u'Alarme de tous type',
                                                      u'ALARM CO': u'Alarme de CO',
                                                      u'ALARM CO2': u'Alarme de CO2',
                                                      u'ALARM GENERIC': u'Alarme g\xe9n\xe9rale',
                                                      u'ALARM HEAT': u'Alarme de temp\xe9rature haute',
                                                      u'ALARM SMOKE': u'Alarme de fum\xe9e',
                                                      u'ALARM WATER': u'Alarme d`inondation'},
                                            u'name': u'R\xe9action aux alarmes'},
                                    u'35': {u'help': u'Ce param\xe8tre d\xe9termine la r\xe9ponse du Wall Plug aux alarmes (changement d`\xe9tat de la charge).',
                                            u'list': {u'Cyclically change device state, each 1second': u'Changement de l\u2019\xe9tat de la charge cycliquement, chaque seconde',
                                                      u'No reaction': u'Pas de r\xe9action',
                                                      u'Turn off connected device': u'D\xe9sactivation de la charge',
                                                      u'Turn on connected device': u'Activation de la charge'},
                                            u'name': u'Comportement du Wall Plug en cas d`alarmes'},
                                    u'39': {u'help': u'Dur\xe9e du mode alarme du Wall Plug. Si un dispositif envoie une trame d\u2019alarme dans le r\xe9seau Z-wave en d\xe9finissant une dur\xe9e de l\u2019alarme, alors la valeur de ce param\xe8tre est ignor\xe9e. Valeur pour ce param\xe8tre 1-65536s',
                                            u'name': u'Dur\xe9e de l\u2019alarme'},
                                    u'40': {u'help': u'Ce param\xe8tre d\xe9finit le pourcentage du changement de la puissance pour que la valeur soit envoy\xe9e au contr\xf4leur principal avec la priorit\xe9 maximale. La configuration par d\xe9faut forcera le Wall Plug Fibaro \xe0 envoyer l`information sur la valeur de la puissance imm\xe9diatement d\xe8s qu`elle varie d`au moins 80%. Valeurs disponibles pour ce param\xe8tre : 1-100%. 100% Rapport d\xe9sactiv\xe9',
                                            u'name': u'Rapport de puissance instantan\xe9e'},
                                    u'42': {u'help': u'Ce param\xe8tre d\xe9termine la valeur pour laquelle la puissance de la charge devra changer pour que le contr\xf4leur principal soit inform\xe9. Par d\xe9faut, le Wall Plug Fibaro enverra un rapport de puissance si la puissance de la charge change de 15%. Par de\u0301faut, le dispositif enverra 5 rapports maximum toutes les 30 secondes. Le Wall Plug peut envoyer 5 rapports pendant le temps configur\xe9 dans le param\xe8tre 43. Valeurs disponibles pour ce param\xe8tre : 1-100%. 100% Rapport d\xe9sactiv\xe9',
                                            u'name': u'Rapport standard sur la puissance de la charge.'},
                                    u'43': {u'help': u'Ce param\xe8tre d\xe9finit la fr\xe9quence d`envoi des rapports de puissance (param\xe8tre 42). Par d\xe9faut le Wall Plug Fibaro enverra 5 rapports maximum toutes les 30 secondes sur le changement de la puissance d\u2019au moins 15%. Valeurs disponibles pour ce param\xe8tre : 1-254s La valeur 255 - les rapports seront envoy\xe9s uniquement en fonction des r\xe9glages du param\xe8tre 47 ou dans le cas d\u2019une demande',
                                            u'name': u'Fr\xe9quence d`envoi des rapports de puissance'},
                                    u'45': {u'help': u'Une nouvelle valeur du rapport d\u2019\xe9nergie est calcul\xe9e en fonction de la derni\xe8re valeur du rapport. Valeurs disponibles pour ce param\xe8tre : 1-254 (0,01kWh - 2,54kWh) - Valeur 255 - les changements de consommation d\u2019\xe9nergie ne seront pas notifi\xe9s. Les rapports seront uniquement envoy\xe9s lors d\u2019une demande.',
                                            u'name': u'Rapports sur les changements de l\u2019\xe9nergie consomm\xe9e par les dispositifs contr\xf4l\xe9s'},
                                    u'47': {u'help': u'Ce param\xe8tre d\xe9finit la p\xe9riode de temps entre les rapports envoy\xe9s lorsque les changements de la puissance de la charge n\u2019ont pas \xe9t\xe9 enregistr\xe9s. Par d\xe9faut, si les changements de la puissance de la charge n\u2019ont pas \xe9t\xe9 enregistr\xe9s, alors les rapports seront envoy\xe9s chaque heure. Valeurs disponibles pour ce param\xe8tre : 1 - 65534s. La valeur 65535 - pas de rapports envoy\xe9s p\xe9riodiquement. Les rapports seront envoy\xe9s uniquement dans le cas d\u2019un changement de puissance de la charge/consommation (param\xe8tres 40, 42, 43, 45) ou dans le cas d\u2019une demande.',
                                            u'name': u'P\xe9riode de temps entre des rapports de la puissance de la charge et l\u2019\xe9nergie consomm\xe9e'},
                                    u'49': {u'help': u'Ce param\xe8tre d\xe9termine si au cours de la mesure d`\xe9nergie consomm\xe9e, la valeur consomm\xe9e par le Wall Plug Fibaro lui-m\xeame sera prise en compte. Cette puissance sera ajout\xe9e \xe0 celle consomm\xe9e par la charge.',
                                            u'list': {u'function activated': u'Fonction activ\xe9e',
                                                      u'function inactive': u'Fonction inactive'},
                                            u'name': u'Mesure de la puissance consomm\xe9e par le Wall Plug lui-m\xeame.'},
                                    u'50': {u'help': u'Seuil de puissance inf\xe9rieur - utilis\xe9 dans le param\xe8tre 52. Valeurs disponibles pour ce param\xe8tre : 0-25000 (0,0W - 2500W) - cette valeur ne pourra \xeatre sup\xe9rieure \xe0 celle d\xe9finie dans le param\xe8tre 51.',
                                            u'name': u'Valeur BASSE'},
                                    u'51': {u'help': u'Seuil de puissance sup\xe9rieur - utilis\xe9 dans le param\xe8tre 52. Valeurs disponibles pour ce param\xe8tre : 0-25000 (0,0W - 2500W) - cette valeur ne pourra \xeatre inf\xe9rieur \xe0 celle d\xe9finie dans le param\xe8tre 51.',
                                            u'name': u'Valeur HAUTE'},
                                    u'52': {u'help': u'Ce param\xe8tre d\xe9finit le mode de contr\xf4le des dispositifs associ\xe9s au deuxi\xe8me groupe d\u2019association en fonction de la puissance actuelle.',
                                            u'list': {u'1 and 4 combine': u'Combinaison des options 1 et 4.',
                                                      u'2 and 3 combined': u'Combinaison des options 2 et 3',
                                                      u'Function inactive': u'Fonction d\xe9sactiv\xe9e',
                                                      u'Turn the associated devices off,Power above UP': u'D\xe9sactiver les dispositifs associ\xe9s quand la puissance chute en dessous de la valeur HAUTE (param\xe8tre 50)',
                                                      u'Turn the associated devices off,Power below DOWN': u'D\xe9sactiver les dispositifs associ\xe9s quand la puissance chute en dessous de la valeur BASSE (param\xe8tre 50)',
                                                      u'Turn the associated devices on,Power above UP': u'Activer les dispositifs associ\xe9s quand la puissance chute en dessous de la valeur HAUTE (param\xe8tre 50)',
                                                      u'Turn the associated devices on,Power below DOWN': u'Activer les dispositifs associ\xe9s quand la puissance chute en dessous de la valeur BASSE (param\xe8tre 50)'},
                                            u'name': u'Configuration du comportement dans le cas du d\xe9passement des seuils de puissance (Param\xe8tre 50 et 51)'},
                                    u'60': {u'help': u'Cette fonction est activ\xe9e uniquement lorsque le param\xe8tre 61 est r\xe9gl\xe9 \xe0 0 ou 1. Valeurs disponibles pour ce param\xe8tre : 1000 - 32000 (100W - 3200W).',
                                            u'name': u'Valeur du seuil de la puissance instantan\xe9e qui fera clignoter l`anneau LED en violet.'},
                                    u'61': {u'help': u'',
                                            u'list': {u'Blue illumination': u'Allum\xe9 en Bleu',
                                                      u'Cyan illumination': u'Allum\xe9 en Cyan',
                                                      u'Depending on power consumption changes': u'D\xe9pends de la consommation de la charge',
                                                      u'Green illumination': u'Allum\xe9 en Vert',
                                                      u'Magenta illumination': u'Allum\xe9 en Magenta',
                                                      u'Red illumination': u'Allum\xe9 en Rouge',
                                                      u'Using full spectrum of available colorus': u'Utilise les spectre complet des couleurs disponible',
                                                      u'White illumination': u'Allum\xe9 en Blanc',
                                                      u'Yellow illumination': u'Allum\xe9 en Jaune',
                                                      u'illumination turned off completely': u'Eteinte'},
                                            u'name': u'Couleur d\u2019illumination de l\u2019anneau LED lorsque la charge est activ\xe9e.'},
                                    u'62': {u'help': u'',
                                            u'list': {u'Blue illumination': u'Allum\xe9 en Bleu',
                                                      u'Cyan illuminatio': u'Allum\xe9 en Cyan',
                                                      u'Depending on the last measured power': u'D\xe9pends de la derni\xe8re puissance instantan\xe9e mesur\xe9e',
                                                      u'Green illumination': u'Allum\xe9 en Vert',
                                                      u'Magenta illumination': u'Allum\xe9 en Magenta',
                                                      u'Red illumination': u'Allum\xe9 en Rouge',
                                                      u'White illumination': u'Allum\xe9 en Blanc',
                                                      u'Yellow illumination': u'Allum\xe9 en Jaune',
                                                      u'illumination turned off completely': u'Eteinte'},
                                            u'name': u"Couleur de l`anneau lorsqu'il n'y a pas de charge."},
                                    u'63': {u'help': u'',
                                            u'list': {u'Blue illumination': u'Allum\xe9 en Bleu',
                                                      u'Cyan illuminatio': u'Allum\xe9 en Cyan',
                                                      u'Green illumination': u'Allum\xe9 en Vert',
                                                      u'LED ring flashes red / blue / white': u'Clignotement Rouge/Bleu/Blanc (Police)',
                                                      u'Magenta illumination': u'Allum\xe9 en Magenta',
                                                      u'No change in colour': u'Pas de changement de couleur',
                                                      u'Red illumination': u'Allum\xe9 en Rouge',
                                                      u'White illumination': u'Allum\xe9 en Blanc',
                                                      u'Yellow illumination': u'Allum\xe9 en Jaune',
                                                      u'illumination turned off completely': u'Eteinte'},
                                            u'name': u"Couleur de l`anneau lors du d\xe9clenchement de l'alarme Z-Wave"},
                                    u'70': {u'help': u'Cette fonction permet de d\xe9sactiver la charge en cas de d\xe9passement de la puissance d\xe9finie. La charge se d\xe9sactivera m\xeame si la fonction Always on est activ\xe9e (param\xe8tre 1). On peut activer de nouveau la charge en appuyant sur le bouton B ou en envoyant une trame de contr\xf4le. Valeurs disponibles pour ce param\xe8tre 10 - 65535 (1W-6553,5W)',
                                            u'name': u'Fonction de l`interrupteur de surcharge'},
                                    u'commentaire': u'',
                                    u'conf_version': u'1',
                                    u'createtime': u'2015-07-07 21:34:11',
                                    u'fileconf': u'',
                                    u'manufacturer_id': 271,
                                    u'product_id': 4096,
                                    u'product_name': u'FGWPE Wall Plug',
                                    u'product_type': 1536,
                                    u'serverID': u'0',
                                    u'updatetime': u'2020-03-28 21:07:33'},
                 u'display': {u'height': u'172px',
                              u'layout::dashboard::table::cmd::229::column': 1,
                              u'layout::dashboard::table::cmd::229::line': 1,
                              u'layout::dashboard::table::cmd::230::column': 1,
                              u'layout::dashboard::table::cmd::230::line': 1,
                              u'layout::dashboard::table::cmd::231::column': 1,
                              u'layout::dashboard::table::cmd::231::line': 1,
                              u'layout::dashboard::table::cmd::232::column': 1,
                              u'layout::dashboard::table::cmd::232::line': 1,
                              u'layout::dashboard::table::cmd::233::column': 1,
                              u'layout::dashboard::table::cmd::233::line': 1,
                              u'layout::dashboard::table::parameters': {u'center': 1,
                                                                        u'styletd': u'padding:3px;'},
                              u'layout::mobile::table::cmd::229::column': 1,
                              u'layout::mobile::table::cmd::229::line': 1,
                              u'layout::mobile::table::cmd::230::column': 1,
                              u'layout::mobile::table::cmd::230::line': 1,
                              u'layout::mobile::table::cmd::231::column': 1,
                              u'layout::mobile::table::cmd::231::line': 1,
                              u'layout::mobile::table::cmd::232::column': 1,
                              u'layout::mobile::table::cmd::232::line': 1,
                              u'layout::mobile::table::cmd::233::column': 1,
                              u'layout::mobile::table::cmd::233::line': 1,
                              u'layout::mobile::table::parameters': {u'center': 1,
                                                                     u'styletd': u'padding:3px;'},
                              u'showObjectNameOndview': 1,
                              u'showObjectNameOnmview': 1,
                              u'showObjectNameOnview': 1,
                              u'width': u'432px'},
                 u'eqReal_id': None,
                 u'eqType_name': u'openzwave',
                 u'generic_type': None,
                 u'id': u'28',
                 u'isEnable': u'1',
                 u'isVisible': u'1',
                 u'logicalId': u'9',
                 u'name': u'UPS',
                 u'object_id': u'4',
                 u'order': u'7',
                 u'status': {u'danger': 0,
                             u'lastCommunication': u'2020-04-03 11:46:51',
                             u'timeout': 0,
                             u'warning': 0},
                 u'tags': None,
                 u'timeout': u'0'}, ]
            """
            r = self.request_jeedom("eqLogic::all")
        elif full:
            # Retourne un equipement et ses commandes ainsi que les etats de celles ci (pour les commandes de type info)
            """
                [{u'category': {u'automatism': u'0',
                               u'default': u'0',
                               u'energy': u'0',
                               u'heating': u'1',
                               u'light': u'0',
                               u'multimedia': u'0',
                               u'security': u'0'},
                 u'cmds': [{u'alert': [],
                            u'configuration': {u'maxValue': u'',
                                               u'minValue': u'',
                                               u'topic': u'esp_tempsalon/in{action}'},
                            u'currentValue': u'ok',
                            u'display': {u'invertBinary': u'1'},
                            u'eqLogic_id': u'266',
                            u'eqType': u'MQTT',
                            u'generic_type': None,
                            u'id': u'4220',
                            u'isHistorized': u'0',
                            u'isVisible': u'1',
                            u'logicalId': u'action',
                            u'name': u'action',
                            u'order': u'1',
                            u'subType': u'string',
                            u'template': [],
                            u'type': u'info',
                            u'unite': u'',
                            u'value': None},
                           {u'alert': [],
                            u'configuration': {u'maxValue': u'',
                                               u'minValue': u'',
                                               u'topic': u'esp_tempsalon/in{hum}'},
                            u'currentValue': 60.8041,
                            u'display': {u'invertBinary': u'1'},
                            u'eqLogic_id': u'266',
                            u'eqType': u'MQTT',
                            u'generic_type': None,
                            u'id': u'4221',
                            u'isHistorized': u'1',
                            u'isVisible': u'1',
                            u'logicalId': u'hum',
                            u'name': u'hum',
                            u'order': u'2',
                            u'subType': u'numeric',
                            u'template': [],
                            u'type': u'info',
                            u'unite': u'%',
                            u'value': None},
                           {u'alert': [],
                            u'configuration': {u'maxValue': u'',
                                               u'minValue': u'',
                                               u'topic': u'esp_tempsalon/in{temp1}'},
                            u'currentValue': 19.2214,
                            u'display': {u'invertBinary': u'1'},
                            u'eqLogic_id': u'266',
                            u'eqType': u'MQTT',
                            u'generic_type': None,
                            u'id': u'4223',
                            u'isHistorized': u'1',
                            u'isVisible': u'1',
                            u'logicalId': u'temp1',
                            u'name': u'temp1',
                            u'order': u'3',
                            u'subType': u'numeric',
                            u'template': [],
                            u'type': u'info',
                            u'unite': u'\xb0C',
                            u'value': None},
                           {u'alert': [],
                            u'configuration': {u'maxValue': u'',
                                               u'minValue': u'',
                                               u'topic': u'esp_tempsalon/in{temp2}'},
                            u'currentValue': 18.6875,
                            u'display': {u'invertBinary': u'1'},
                            u'eqLogic_id': u'266',
                            u'eqType': u'MQTT',
                            u'generic_type': None,
                            u'id': u'4222',
                            u'isHistorized': u'1',
                            u'isVisible': u'1',
                            u'logicalId': u'temp2',
                            u'name': u'temp2',
                            u'order': u'4',
                            u'subType': u'numeric',
                            u'template': [],
                            u'type': u'info',
                            u'unite': u'\xb0C',
                            u'value': None},
                           {u'alert': [],
                            u'configuration': {u'maxValue': u'',
                                               u'minValue': u'',
                                               u'topic': u'esp_tempsalon/in{uptime}'},
                            u'currentValue': 444560,
                            u'display': {u'invertBinary': u'1'},
                            u'eqLogic_id': u'266',
                            u'eqType': u'MQTT',
                            u'generic_type': None,
                            u'id': u'4219',
                            u'isHistorized': u'0',
                            u'isVisible': u'1',
                            u'logicalId': u'uptime',
                            u'name': u'uptime',
                            u'order': u'5',
                            u'subType': u'numeric',
                            u'template': [],
                            u'type': u'info',
                            u'unite': u'',
                            u'value': None}],
                 u'comment': u'',
                 u'configuration': {u'battery_danger_threshold': u'',
                                    u'battery_type': u'',
                                    u'battery_warning_threshold': u'',
                                    u'batterytime': u'',
                                    u'createtime': u'2020-03-27 20:01:15',
                                    u'icone': u'temp',
                                    u'topic': u'esp_tempsalon/in',
                                    u'type': u'json',
                                    u'updatetime': u'2020-03-31 22:07:10'},
                 u'display': {u'background-color-defaultdashboard': u'1',
                              u'background-color-defaultmobile': u'1',
                              u'background-color-defaultplan': u'1',
                              u'background-color-defaultview': u'1',
                              u'background-color-transparentdashboard': u'0',
                              u'background-color-transparentmobile': u'0',
                              u'background-color-transparentplan': u'0',
                              u'background-color-transparentview': u'0',
                              u'background-colordashboard': u'#2980b9',
                              u'background-colormobile': u'#2980b9',
                              u'background-colorplan': u'#2980b9',
                              u'background-colorview': u'#2980b9',
                              u'background-opacitydashboard': u'',
                              u'background-opacitymobile': u'',
                              u'background-opacityplan': u'',
                              u'background-opacityview': u'',
                              u'border-defaultdashboard': u'1',
                              u'border-defaultmobile': u'1',
                              u'border-defaultplan': u'1',
                              u'border-defaultview': u'1',
                              u'border-radius-defaultdashboard': u'1',
                              u'border-radius-defaultmobile': u'1',
                              u'border-radius-defaultplan': u'1',
                              u'border-radius-defaultview': u'1',
                              u'border-radiusdashboard': u'',
                              u'border-radiusmobile': u'',
                              u'border-radiusplan': u'',
                              u'border-radiusview': u'',
                              u'borderdashboard': u'',
                              u'bordermobile': u'',
                              u'borderplan': u'',
                              u'borderview': u'',
                              u'color-defaultdashboard': u'1',
                              u'color-defaultmobile': u'1',
                              u'color-defaultplan': u'1',
                              u'color-defaultview': u'1',
                              u'colordashboard': u'#ffffff',
                              u'colormobile': u'#ffffff',
                              u'colorplan': u'#ffffff',
                              u'colorview': u'#ffffff',
                              u'height': u'172px',
                              u'layout::dashboard': u'default',
                              u'layout::dashboard::table::cmd::4219::column': 1,
                              u'layout::dashboard::table::cmd::4219::line': 1,
                              u'layout::dashboard::table::cmd::4220::column': 1,
                              u'layout::dashboard::table::cmd::4220::line': 1,
                              u'layout::dashboard::table::cmd::4221::column': 1,
                              u'layout::dashboard::table::cmd::4221::line': 1,
                              u'layout::dashboard::table::cmd::4222::column': 1,
                              u'layout::dashboard::table::cmd::4222::line': 1,
                              u'layout::dashboard::table::cmd::4223::column': 1,
                              u'layout::dashboard::table::cmd::4223::line': 1,
                              u'layout::dashboard::table::nbColumn': u'',
                              u'layout::dashboard::table::nbLine': u'',
                              u'layout::dashboard::table::parameters': {u'center': u'1',
                                                                        u'style::td::1::1': u'',
                                                                        u'styletable': u'',
                                                                        u'styletd': u'padding:3px;',
                                                                        u'text::td::1::1': u''},
                              u'layout::mobile::table::cmd::4219::column': 1,
                              u'layout::mobile::table::cmd::4219::line': 1,
                              u'layout::mobile::table::cmd::4220::column': 1,
                              u'layout::mobile::table::cmd::4220::line': 1,
                              u'layout::mobile::table::cmd::4221::column': 1,
                              u'layout::mobile::table::cmd::4221::line': 1,
                              u'layout::mobile::table::cmd::4222::column': 1,
                              u'layout::mobile::table::cmd::4222::line': 1,
                              u'layout::mobile::table::cmd::4223::column': 1,
                              u'layout::mobile::table::cmd::4223::line': 1,
                              u'layout::mobile::table::parameters': {u'center': 1,
                                                                     u'styletd': u'padding:3px;'},
                              u'parameters': [],
                              u'showNameOndashboard': u'1',
                              u'showNameOnmobile': u'1',
                              u'showNameOnplan': u'1',
                              u'showNameOnview': u'1',
                              u'showObjectNameOndashboard': u'0',
                              u'showObjectNameOndview': 1,
                              u'showObjectNameOnmobile': u'0',
                              u'showObjectNameOnmview': 1,
                              u'showObjectNameOnplan': u'0',
                              u'showObjectNameOnview': u'1',
                              u'width': u'512px'},
                 u'eqReal_id': None,
                 u'eqType_name': u'MQTT',
                 u'generic_type': None,
                 u'id': u'266',
                 u'isEnable': u'1',
                 u'isVisible': u'1',
                 u'logicalId': u'esp_tempsalon/in',
                 u'name': u'esp_tempsalonin',
                 u'object_id': u'1',
                 u'order': u'6',
                 u'status': {u'danger': 0,
                             u'lastCommunication': u'2020-04-03 11:50:49',
                             u'timeout': 0,
                             u'warning': 0},
                 u'tags': u'',
                 u'timeout': u'120'},]
            """
            r = self.request_jeedom("eqLogic::fullById", id=id)
        else:
            r = self.request_jeedom("eqLogic::byId", id=id)
        if enabled_only:
            return [e for e in r if e['isEnable'] in ['1', 1, True, 'true', 'True']]
        else:
            return r

    def getChanges(self, since_epoch):
        # Retourne la liste des changements depuis le datetime passe en parametre (doit etre en microsecondes).
        # Vous aurez aussi dans la reponse le datetime courant de Jeedom (e reutiliser pour l interrogation suivante)
        """
        {u'datetime': 1585907805.2603,
         u'result': [{u'datetime': 1585907703.5036,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2531',
                                  u'collectDate': u'2020-04-03 11:55:03',
                                  u'display_value': u'De 11h55 \xe0 12h55 : Pas de pr\xe9cipitations',
                                  u'value': u'De 11h55 \xe0 12h55 : Pas de pr\xe9cipitations',
                                  u'valueDate': u'2020-04-03 11:55:03'}},
                     {u'datetime': 1585907703.5433,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2532',
                                  u'collectDate': u'2020-04-03 11:55:03',
                                  u'display_value': u'11h40',
                                  u'value': u'11h40',
                                  u'valueDate': u'2020-04-03 11:55:03'}},
                     {u'datetime': 1585907703.6753,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2534',
                                  u'collectDate': u'2020-04-03 11:55:03',
                                  u'display_value': 0,
                                  u'value': u'',
                                  u'valueDate': u'2020-04-03 11:55:03'}},
                     {u'datetime': 1585907703.6946,
                      u'name': u'eqLogic::update',
                      u'option': {u'eqLogic_id': u'136'}},
                     {u'datetime': 1585907703.7086,
                      u'name': u'eqLogic::update',
                      u'option': {u'eqLogic_id': u'137'}},
                     {u'datetime': 1585907703.7331,
                      u'name': u'eqLogic::update',
                      u'option': {u'eqLogic_id': u'140'}},
                     {u'datetime': 1585907703.7447,
                      u'name': u'eqLogic::update',
                      u'option': {u'eqLogic_id': u'138'}},
                     {u'datetime': 1585907704.1511,
                      u'name': u'scenario::update',
                      u'option': {u'lastLaunch': u'2020-04-03 11:55:04',
                                  u'scenario_id': u'32',
                                  u'state': u'stop'}},
                     {u'datetime': 1585907705.1606,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'228',
                                  u'collectDate': u'2020-04-03 11:55:05',
                                  u'display_value': 10.1802,
                                  u'value': 10.1802,
                                  u'valueDate': u'2020-04-03 11:55:05'}},
                     {u'datetime': 1585907705.1662,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'222',
                                  u'collectDate': u'2020-04-03 11:55:05',
                                  u'display_value': 48.2,
                                  u'value': 48.2,
                                  u'valueDate': u'2020-04-03 11:55:05'}},
                     {u'datetime': 1585907753.2674,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4247',
                                  u'collectDate': u'2020-04-03 11:55:53',
                                  u'display_value': 61.1,
                                  u'value': 61.1,
                                  u'valueDate': u'2020-04-03 11:55:53'}},
                     {u'datetime': 1585907753.2717,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4221',
                                  u'collectDate': u'2020-04-03 11:55:53',
                                  u'display_value': 61.091,
                                  u'value': 61.091,
                                  u'valueDate': u'2020-04-03 11:55:53'}},
                     {u'datetime': 1585907753.2798,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4219',
                                  u'collectDate': u'2020-04-03 11:55:53',
                                  u'display_value': 444841,
                                  u'value': 444841,
                                  u'valueDate': u'2020-04-03 11:55:53'}},
                     {u'datetime': 1585907753.2875,
                      u'name': u'cmd::update',
                      u'option': {u'cmd_id': u'4246',
                                  u'collectDate': u'2020-04-03 11:55:53',
                                  u'display_value': 19.3,
                                  u'value': 19.3,
                                  u'valueDate': u'2020-04-03 11:54:52'}},
                     {u'datetime': 1585907753.2912,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4223',
                                  u'collectDate': u'2020-04-03 11:55:53',
                                  u'display_value': 19.2775,
                                  u'value': 19.2775,
                                  u'valueDate': u'2020-04-03 11:55:53'}},
                     {u'datetime': 1585907755.2188,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'223',
                                  u'collectDate': u'2020-04-03 11:55:55',
                                  u'display_value': 2.6271,
                                  u'value': 2.6271,
                                  u'valueDate': u'2020-04-03 11:55:55'}},
                     {u'datetime': 1585907755.2248,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'217',
                                  u'collectDate': u'2020-04-03 11:55:55',
                                  u'display_value': 12.5,
                                  u'value': 12.5,
                                  u'valueDate': u'2020-04-03 11:55:55'}},
                     {u'datetime': 1585907758.6681,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'danger',
                                  u'cmd_id': u'3186',
                                  u'collectDate': u'2020-04-03 11:55:58',
                                  u'display_value': u'daemon_died',
                                  u'value': u'daemon_died',
                                  u'valueDate': u'2020-03-17 02:37:21'}},
                     {u'datetime': 1585907759.8066,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2579',
                                  u'collectDate': u'2020-04-03 11:55:59',
                                  u'display_value': 7,
                                  u'value': 7,
                                  u'valueDate': u'2020-04-03 11:52:51'}},
                     {u'datetime': 1585907759.8132,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3237',
                                  u'collectDate': u'2020-04-03 11:55:59',
                                  u'display_value': u'21880629',
                                  u'value': u'21880629',
                                  u'valueDate': u'2020-04-03 11:55:59'}},
                     {u'datetime': 1585907759.8222,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4248',
                                  u'collectDate': u'2020-04-03 11:55:59',
                                  u'display_value': 12.3,
                                  u'value': 12.3,
                                  u'valueDate': u'2020-04-03 11:55:59'}},
                     {u'datetime': 1585907759.8272,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4215',
                                  u'collectDate': u'2020-04-03 11:55:59',
                                  u'display_value': 12.25,
                                  u'value': 12.25,
                                  u'valueDate': u'2020-04-03 11:55:59'}},
                     {u'datetime': 1585907759.834,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2584',
                                  u'collectDate': u'2020-04-03 11:55:59',
                                  u'display_value': u'success',
                                  u'value': u'success',
                                  u'valueDate': u'2020-03-27 19:13:21'}},
                     {u'datetime': 1585907759.8403,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2580',
                                  u'collectDate': u'2020-04-03 11:55:59',
                                  u'display_value': 21880648,
                                  u'value': 21880648,
                                  u'valueDate': u'2020-04-03 11:55:59'}},
                     {u'datetime': 1585907760.2573,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4217',
                                  u'collectDate': u'2020-04-03 11:56:00',
                                  u'display_value': u'21880648',
                                  u'value': u'21880648',
                                  u'valueDate': u'2020-04-03 11:56:00'}},
                     {u'datetime': 1585907760.2646,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2590',
                                  u'collectDate': u'2020-04-03 11:56:00',
                                  u'display_value': 1085,
                                  u'value': 1085,
                                  u'valueDate': u'2020-04-03 11:56:00'}},
                     {u'datetime': 1585907760.2701,
                      u'name': u'jeeObject::summary::update',
                      u'option': {u'keys': {u'power': {u'value': 1085}},
                                  u'object_id': u'8'}},
                     {u'datetime': 1585907760.2769,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4218',
                                  u'collectDate': u'2020-04-03 11:56:00',
                                  u'display_value': 1560,
                                  u'value': 1560,
                                  u'valueDate': u'2020-04-03 11:56:00'}},
                     {u'datetime': 1585907760.2848,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3231',
                                  u'collectDate': u'2020-04-03 11:56:00',
                                  u'display_value': 19,
                                  u'value': 19,
                                  u'valueDate': u'2020-04-03 11:56:00'}},
                     {u'datetime': 1585907760.292,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3232',
                                  u'collectDate': u'2020-04-03 11:56:00',
                                  u'display_value': u'63',
                                  u'value': u'63',
                                  u'valueDate': u'2020-04-03 11:56:00'}},
                     {u'datetime': 1585907760.2989,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'2589',
                                  u'collectDate': u'2020-04-03 11:56:00',
                                  u'display_value': 483323,
                                  u'value': 483323,
                                  u'valueDate': u'2020-04-03 11:56:00'}},
                     {u'datetime': 1585907798.5189,
                      u'name': u'cmd::update',
                      u'option': {u'cmd_id': u'4282',
                                  u'collectDate': u'2020-04-03 11:56:38',
                                  u'display_value': 0.046,
                                  u'value': 0.046,
                                  u'valueDate': u'2020-04-03 11:40:28'}},
                     {u'datetime': 1585907798.5253,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'4281',
                                  u'collectDate': u'2020-04-03 11:56:38',
                                  u'display_value': 0.527,
                                  u'value': 0.527,
                                  u'valueDate': u'2020-04-03 11:56:38'}},
                     {u'datetime': 1585907803.8913,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3209',
                                  u'collectDate': u'2020-04-03 11:56:43',
                                  u'display_value': u'',
                                  u'value': u'',
                                  u'valueDate': u'2020-04-03 11:56:43'}},
                     {u'datetime': 1585907803.8976,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3210',
                                  u'collectDate': u'2020-04-03 11:56:43',
                                  u'display_value': u'1119540',
                                  u'value': u'1119540',
                                  u'valueDate': u'2020-04-03 11:56:43'}},
                     {u'datetime': 1585907803.9061,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3213',
                                  u'collectDate': u'2020-04-03 11:56:43',
                                  u'display_value': 403,
                                  u'value': 403,
                                  u'valueDate': u'2020-04-03 11:56:43'}},
                     {u'datetime': 1585907803.9195,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'3214',
                                  u'collectDate': u'2020-04-03 11:56:43',
                                  u'display_value': u'ping',
                                  u'value': u'ping',
                                  u'valueDate': u'2020-04-03 08:49:29'}},
                     {u'datetime': 1585907804.065,
                      u'name': u'scenario::update',
                      u'option': {u'lastLaunch': u'2020-04-03 11:56:44',
                                  u'scenario_id': u'33',
                                  u'state': u'stop'}},
                     {u'datetime': 1585907805.2545,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'218',
                                  u'collectDate': u'2020-04-03 11:56:45',
                                  u'display_value': 9.1,
                                  u'value': 9.1,
                                  u'valueDate': u'2020-04-03 11:56:45'}},
                     {u'datetime': 1585907805.2603,
                      u'name': u'cmd::update',
                      u'option': {u'alertLevel': u'none',
                                  u'cmd_id': u'224',
                                  u'collectDate': u'2020-04-03 11:56:45',
                                  u'display_value': 1.8473,
                                  u'value': 1.8473,
                                  u'valueDate': u'2020-04-03 11:56:45'}}]}
        """
        return self.request_jeedom("event::changes", datetime=since_epoch)

    def getTendance(self, id, start_time, end_time=None, allow_future_end_time=False):
        #-0.023455287955182
        return self._getWithStartEndTime('cmd::getTendance', id, start_time, end_time, allow_future_end_time)

    def getStatistique(self, id, start_time, end_time=None, allow_future_end_time=False):
        """
            {u'avg': u'19.918857',
             u'count': u'35',
             u'last': u'19.215455',
             u'max': u'27.13',
             u'min': u'18.49',
             u'std': u'1.776727',
             u'sum': u'697.16',
             u'variance': u'3.156759'}
        """
        return self._getWithStartEndTime('cmd::getStatistique', id, start_time, end_time, allow_future_end_time)

    def getHistory(self, id, start_time, end_time=None, allow_future_end_time=False):
        # [{u'cmd_id': u'4222', u'datetime': u'2020-04-03 13:20:00', u'value': u'18.875'},]
        return self._getWithStartEndTime('cmd::getHistory', id, start_time, end_time, allow_future_end_time)

    def _getWithStartEndTime(self, cmd, id, start_time, end_time, allow_future_end_time):
        now = self.getTime()
        if end_time and start_time > now:
            raise Exception("Start time is in the future")
        if end_time and not allow_future_end_time and end_time > now:
            raise Exception("End time is in the future")
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        if not end_time:
            end_time = self.getTime() - datetime.timedelta(seconds=1)
        end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        return self.request_jeedom(cmd, id=id, startTime=start_time, endTime=end_time)


def localdatetime_to_epoch(d):
    paris_tz = pytz.timezone('Europe/Paris')
    d=paris_tz.localize(d)
    d = d.astimezone(pytz.UTC)
    return int((d - datetime.datetime(1970,1,1,tzinfo=pytz.utc)).total_seconds())


class jeedom_to_influx:
    def __init__(self):
        self._load_db()
        self.influx_client = InfluxDBClient(host=config.INFLUXDB_HOST, port=8086)
        self.jeedom = jeedom_api()

    def _load_db(self):
        self.db = {
            'last_timestamp': datetime.datetime.now() - datetime.timedelta(hours=1)
        }
        try:
            with open(config.DB_PATH) as f:
                self.db = pickle.load(f)
        except IOError:
            logging.warning("No db found at %s"%config.DB_PATH)

    def save_db(self):
        with open(config.DB_PATH + '.tmp', 'wb') as f:
            pickle.dump(self.db, f)
        shutil.move(config.DB_PATH + '.tmp', config.DB_PATH)

    @staticmethod
    def escape_tag(tag):
        # Escape accoring to influx line protocol
        if tag is None or len(tag) == 0:
            return '?'
        if isinstance(tag, (basestring, str, unicode)):
            return tag.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")
        return tag

    @staticmethod
    def escape_measurement(tag):
        # Escape accoring to influx line protocol
        if tag=='time':
            tag = 'time_'
        if isinstance(tag, (basestring, str, unicode)):
            return tag.replace(" ", "\\ ").replace(",", "\\,")
        return tag

    @staticmethod
    def escape_value(tag):
        # Escape accoring to influx line protocol
        if isinstance(tag, (basestring, str, unicode)):
            return '"%s"' % tag.replace('"', '\\"')
        return tag

    @staticmethod
    def transtype_by_guessing(value):
        # Transtype to possible original data type
        try:
            value = int(value)
        except:
            try:
                value = float(value)
            except:
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
        return value

    def import_data(self):
        data_buffer = []
        now = self.jeedom.getTime()
        if self.db['last_timestamp'] is None:
            start_time = now - datetime.timedelta(days=config.DEFAULT_START_TIME_DAYS)
            logging.warning("No last timestamp found in db, using %s" % start_time)
        else:
            start_time = self.db['last_timestamp']
            logging.warning("Starting query at %s"%start_time)
        for eq in self.jeedom.getEquipments(enabled_only=True):
            eq_name = eq['name']
            logging.debug("Working on %s"%eq_name)
            for command in self.jeedom.getCommands(equipment_id=int(eq['id']), historized_only=True):
                command_id = int(command['id'])
                command_name = command['name']
                h = self.jeedom.getHistory(id=command_id, start_time=start_time, end_time=now)
                if h:
                    for v in h:
                        timestamp_dt = datetime.datetime.strptime(v['datetime'], "%Y-%m-%d %H:%M:%S")
                        if timestamp_dt < start_time:
                            pass
                        timestamp = int(localdatetime_to_epoch(timestamp_dt))
                        script_stats['new_results'] += 1
                        value = self.escape_value(self.transtype_by_guessing(v['value']))
                        data_buffer.append(
                            u'{eq_name},eqtype={eq_type},type={generic_type},unit=unit,cmd_id={cmd_id},eq_id={eq_id} {command_name}={value} {timestamp}'.format(
                                    eq_name=self.escape_measurement(eq_name + '.' + str(command['eqLogic_id'])), # Add id to make sure of uniqueness or the measurement
                                    eq_type=self.escape_tag(command['eqType']),
                                    eq_id=int(command['eqLogic_id']), # No need to escape int
                                    cmd_id=int(command['id']),
                                    generic_type=self.escape_tag(command['generic_type']),
                                    unit=self.escape_tag(command['unite']),
                                    value=value,
                                    command_name=self.escape_measurement(command_name),
                                    timestamp=timestamp
                            )
                        )
                    if timestamp_dt > self.db['last_timestamp']:
                        self.db['last_timestamp'] = timestamp_dt
        logging.info("Going to write to influxdb")
        self.influx_client.write_points(data_buffer, database=config.INFLUXDB_DATABASE_NAME, time_precision='s', batch_size=2000, protocol='line')
        script_stats['elapsed_time'] = time.time() - script_stats['start_time']
        self.influx_client.write_points(['jeedom_to_influxdb elapsed_time={elapsed_time},new_results={new_results}'.format(**script_stats)], database=config.INFLUXDB_DATABASE_NAME, time_precision='s', protocol='line')
        logging.info("Write to influxdb finished")

if __name__ == '__main__':
    j = jeedom_to_influx()
    j.import_data()
    j.save_db()
    logging.warning(script_stats)

