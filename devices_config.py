# Enable Debug Mode
DEBUG = False

# DM Objects Specification file
OBJECTS_SPEC_FILE = 'objects-spec.json'

# MQTT Settings
#BROKER_ADDRESS = 'io.atnog.org'
#BROKER_PORT = 1883
#MQTT_TENANT = 'BFqlrzwkZODRaeY9KOGZNO/TDmh2Fiq48eOXpoX1TO3dH/MPksiwmKSMKricAvUuQX3C/9X3YMfwjsoJ3syAKeXe2mKWyXGNUDWli'
#DEVICES_TOPIC = '/devices'
#CONFIG_TOPIC = '/devconfig'
#USERNAME = '3TQz4fkWoF22YnOQMPSKjqlkMQvlbMGz'
#PASSWORD = '3TQz4fkWoF22YnOQMPSKjqlkMQvlbMGz'

BROKER_ADDRESS = 'sonata4.local'
BROKER_PORT = 1883
MQTT_TENANT = '/SM'
DEVICES_TOPIC = '/devices'
CONFIG_TOPIC = '/devconfig'
USERNAME = None
PASSWORD = None


# WebSimulator # TO BE REMOVED
ENABLE_SIMULATOR = True
WEB_ADDRESS = 'http://localhost:8080'


DEVICES_CONFIG = dict()

'''for i in range(1,46):
	DEVICES_CONFIG['ac%d'%i] = {
		'objects': [
			{
				'object_id': 1101,
				'object_inst': 0,
			}
		],
		'web_info': [
			{
				'object_id': 1101,
				'object_inst': 0,
				'resource_id': 11011,
				'resource_inst': 0,
			}
		],
	}
'''
'''
for i in range(1,50):
	DEVICES_CONFIG['tmp%d'%i] = {
		'objects': [
			{
				'object_id': 3303,
				'object_inst': 0,
			}
		],
		'generators': [
			{
				'object_id': 3303,
				'object_inst': 0,
				'resource_id': 5700,
				'resource_inst': 0,
				'periodicity': 8,
				'type': 'raw',
				'args': {
					'file': 'datasets/office_data/LANGEVIN_DATA.txt',
					'column': 5,
				}

			}
		],
		'web_info': [
			{
				'object_id': 3303,
				'object_inst': 0,
				'resource_id': 5700,
				'resource_inst': 0,
			}
		],
	}

for i in range(1,50):
	DEVICES_CONFIG['hum%d'%i] = {
		'objects': [
			{
				'object_id': 3304,
				'object_inst': 0,
			}
		],
		'generators': [
			{
				'object_id': 3304,
				'object_inst': 0,
				'resource_id': 5700,
				'resource_inst': 0,
				'periodicity': 10,
				'type': 'raw',
				'args': {
					'file': 'datasets/office_data/LANGEVIN_DATA.txt',
					'column': 6,
				}

			}
		],
		'web_info': [
			{
				'object_id': 3304,
				'object_inst': 0,
				'resource_id': 5700,
				'resource_inst': 0,
			}
		],
	}

for i in range(1,157):
	DEVICES_CONFIG['lux%d'%i] = {
		'objects': [
			{
				'object_id': 3301,              # Luminosity Sensor
				'object_inst': 0
			},
		],
		'generators': [
			{
				'object_id': 3301,
				'object_inst': 0,
				'resource_id': 5700,
				'resource_inst': 0,
				'periodicity': 5,
				'min': 0,
				'max': 40,
				'type': 'random'
			},
		],
		'web_info': [
			{
				'object_id': 3301,
				'object_inst': 0,
				'resource_id': 5700,
				'resource_inst': 0,
			},
		],
	}

import random
for i in range(1,165):

	DEVICES_CONFIG['motion%d'%i] = {
		'objects': [
			{
				'object_id': 3302,              # Motion Sensor
				'object_inst': 0,
				'resource_id': 5500,
				'resource_inst': 0
			},
		],
		'web_info': [
			{
				'object_id': 3302,
				'object_inst': 0,
				'resource_id': 5500,
				'resource_inst': 0,
			},
		],
	}

for i in range(1,109):
	DEVICES_CONFIG['light%d'%i] = {
		'objects': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resources': [
					{
						'resource_id': 15011,    # ON/OFF
						'resource_inst': 0
					},
					{
						'resource_id': 15012,    # Dimming
						'resource_inst': 0
					},
				]
			},
		],
		'web_info': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15011,
				'resource_inst': 0,
			},
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15012,
				'resource_inst': 0,
			},
		],
	}

DEVICES_CONFIG['light_c0'] = DEVICES_CONFIG.pop('light5')

for i in range(1,34):
	DEVICES_CONFIG['light_b%d'%i] = {
		'objects': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resources': [
					{
						'resource_id': 15011,    # ON/OFF
						'resource_inst': 0
					},
					{
						'resource_id': 15012,    # Dimming
						'resource_inst': 0
					},
				]
			},
		],
		'web_info': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15011,
				'resource_inst': 0,
			},
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15012,
				'resource_inst': 0,
			},
		],
	}

for i in range(1,10):
	DEVICES_CONFIG['light_s%d'%i] = {
		'objects': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resources': [
					{
						'resource_id': 15011,    # ON/OFF
						'resource_inst': 0
					},
					{
						'resource_id': 15012,    # Dimming
						'resource_inst': 0
					},
				]
			},
		],
		'web_info': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15011,
				'resource_inst': 0,
			},
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15012,
				'resource_inst': 0,
			},
		],
	}
'''
for i in range(1,77):
	DEVICES_CONFIG['light_c%d'%i] = {
		'objects': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resources': [
					{
						'resource_id': 15011,    # ON/OFF
						'resource_inst': 0
					},
					{
						'resource_id': 15012,    # Dimming
						'resource_inst': 0
					},
				]
			},
		],
		'web_info': [
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15011,
				'resource_inst': 0,
			},
			{
				'object_id': 1501,
				'object_inst': 0,
				'resource_id': 15012,
				'resource_inst': 0,
			},
		],
	}
