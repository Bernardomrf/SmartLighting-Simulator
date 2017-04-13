from device import *
from devices_config import *
from random_generator import *
from raw_generator import *
from mda_generator import *
import ujson as json
from threading import Thread

import os
import time
import json
import sys
import subprocess
import signal

if sys.version_info[0] < 3:
	import urllib2 as ur
	input = raw_input
else:
	import urllib.request as ur

with open(OBJECTS_SPEC_FILE) as json_file:
	OBJECTS_SPEC = json.load(json_file)

calc_latency = False
got_it = False
start_time = None

def send_event(**kwargs):
	global got_it
	global start_time
	url = WEB_ADDRESS + '/event'
	req = ur.Request(url)
	req.add_header('Content-Type', 'application/json; charset=utf-8')
	if calc_latency:
		if kwargs['device'] == 'motion123' and kwargs['value'] == 1 and not got_it:
			got_it = True
			start_time = time.time()
		if kwargs['device'] == 'light_c12' and kwargs['value'] == 1 and got_it and start_time != None:
			got_it = False
			final_time = time.time() - start_time
			start_time = None
			print('%.2f'%(final_time*1000))
	json_data = json.dumps(kwargs)
	json_data_as_bytes = json_data.encode('utf-8')
	req.add_header('Content-Length', len(json_data_as_bytes))
	try:
		response = ur.urlopen(req, json_data_as_bytes)
		status = response.read()
		if status == b'OK':
			return True
		else:
			return False
	except ur.URLError:
		return False

tmp_obj = dict()
RESOURCE_SPEC = dict()
for x in OBJECTS_SPEC:
	tmp_obj[x['id']] = x.copy()
	for y in x['resourcedefs']:
		if y['id'] not in RESOURCE_SPEC:
			RESOURCE_SPEC[y['id']] = y.copy()
OBJECTS_SPEC = tmp_obj.copy()
del tmp_obj
MANDATORY_OBJECTS = {x: OBJECTS_SPEC[x].copy() for x in OBJECTS_SPEC if OBJECTS_SPEC[x]['mandatory']}

if __name__ == '__main__':
	if len(sys.argv) > 1:
		if len(sys.argv) == 2:
			if sys.argv[1] == 'latency':
				calc_latency = True

	devices = []
	generators = []

	for device_id, info in DEVICES_CONFIG.items():
		objs = dict()
		for obj in info['objects']:
			obj_spec = dict(OBJECTS_SPEC[obj['object_id']])
			ress = dict()
			for res in obj_spec['resourcedefs']:
				if 'resources' in obj:
					l = [x for x in obj['resources'] if x['resource_id'] == res['id']]
					if l != []:
						for r in l:
							ress[r['resource_id'], r['resource_inst']] = dict(RESOURCE_SPEC[r['resource_id']])
					elif res['mandatory']:
						ress[res['id'], 0] = dict(RESOURCE_SPEC[res['id']])
				elif res['mandatory']:
					ress[res['id'], 0] = dict(RESOURCE_SPEC[res['id']])

			objs[obj['object_id'], obj['object_inst']] = dict(obj_spec)
			objs[obj['object_id'], obj['object_inst']]['resourcedefs'] = dict(ress)

		for m_obj in MANDATORY_OBJECTS:
			obj = dict(MANDATORY_OBJECTS[m_obj])
			if obj['id'] not in [x['object_id'] for x in info['objects']]:
				ress = dict()
				for res in obj['resourcedefs']:
					if res['mandatory']:
						ress[res['id'], 0] = RESOURCE_SPEC[res['id']]
				objs[obj['id'], 0] = OBJECTS_SPEC[obj['id']]
				objs[obj['id'], 0]['resourcedefs'] = ress

		device = Device(device_id, objs, DEVICES_TOPIC, CONFIG_TOPIC, MQTT_TENANT, BROKER_ADDRESS, BROKER_PORT, USERNAME, PASSWORD, DEBUG)

		if 'generators' in info:
			for g_info in info['generators']:
				if g_info['type'] == 'random':
					periodicity = g_info['periodicity']
					min_value = g_info['min'] if 'min' in g_info else None
					max_value = g_info['max'] if 'max' in g_info else None
					obj, obj_inst = (g_info['object_id'], g_info['object_inst'])
					res, res_inst = (g_info['resource_id'], g_info['resource_inst'])
					resource = device.getObject(obj, obj_inst).getResource(res, res_inst)
					#generators.append(RandomGenerator(periodicity, min_value, max_value, resource, DEBUG))

				if g_info['type'] == 'raw':
					periodicity = g_info['periodicity']
					min_value = g_info['min'] if 'min' in g_info else None
					max_value = g_info['max'] if 'max' in g_info else None
					obj, obj_inst = (g_info['object_id'], g_info['object_inst'])
					res, res_inst = (g_info['resource_id'], g_info['resource_inst'])
					resource = device.getObject(obj, obj_inst).getResource(res, res_inst)
					file = g_info['args']['file']
					column = g_info['args']['column']
					cvt_celsius = g_info['args']['convert_to_celsius'] if 'convert_to_celsius' in g_info['args'] else False
					skiplines = g_info['args']['skiplines'] if 'skiplines' in g_info['args'] else 0
					csv = False
					#generators.append(RawGenerator(file, column, periodicity, resource, csv, cvt_celsius, skiplines, DEBUG))

				if g_info['type'] == 'csv':
					periodicity = g_info['periodicity']
					min_value = g_info['min'] if 'min' in g_info else None
					max_value = g_info['max'] if 'max' in g_info else None
					obj, obj_inst = (g_info['object_id'], g_info['object_inst'])
					res, res_inst = (g_info['resource_id'], g_info['resource_inst'])
					resource = device.getObject(obj, obj_inst).getResource(res, res_inst)
					file = g_info['args']['file']
					column = g_info['args']['column']
					cvt_celsius = g_info['args']['convert_to_celsius'] if 'convert_to_celsius' in g_info['args'] else False
					skiplines = g_info['args']['skiplines'] if 'skiplines' in g_info['args'] else 0
					csv = True
					#generators.append(RawGenerator(file, column, periodicity, resource, csv, cvt_celsius, skiplines, DEBUG))

				if g_info['type'] == 'mda':
					obj, obj_inst = (g_info['object_id'], g_info['object_inst'])
					res, res_inst = (g_info['resource_id'], g_info['resource_inst'])
					resource = device.getObject(obj, obj_inst).getResource(res, res_inst)
					file = g_info['args']['file']
					#generators.append(MDAGenerator(file, resource, DEBUG))

		if ENABLE_SIMULATOR and 'web_info' in info:
			for w_info in info['web_info']:
				obj, obj_inst = (w_info['object_id'], w_info['object_inst'])
				res, res_inst = (w_info['resource_id'], w_info['resource_inst'])
				resource = device.getObject(obj, obj_inst).getResource(res, res_inst)
				resource.setEventCall(device_id, send_event)

		devices.append(device)

	print('\n\n\n\t\t### Press Enter or Ctrl+C To Exit ###\n\n\n')

	if ENABLE_SIMULATOR:    # Use python2 while gevent is not stable in python3
		FNULL = open(os.devnull, 'w')
		p = subprocess.Popen(['python','webserver.py'], stdout=FNULL, stderr=subprocess.STDOUT)

	for device in devices:
		device.start()

	time.sleep(1)

	for generator in generators:
		generator.start()

	def exit():
		for generator in generators:
			generator.stop()

		for device in devices:
			device.stop()

		if ENABLE_SIMULATOR:
			p.terminate()
			p.wait()

	def signal_handler(signal, frame):
		exit()
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)

	input()
	exit()
