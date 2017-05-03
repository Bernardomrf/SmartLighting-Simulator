from threading import Thread, Event
#from paho.mqtt.client import Client
from mqtt_common_client import MQTTVirtualClient as Client
import json
import time

class Resource:
	def __init__(self, obj, res, inst, callback, debug=False):
		self.r_id = res['id']
		self.r_inst = inst
		self.obj = obj

		self._debug = debug
		self._res = res
		self._value = None
		self._callback = callback
		self._name = res['name']
		self._access = res['operations']
		self._instancetype = res['instancetype']
		self._mandatory = res['mandatory']
		self._r_type = res['type']
		self._range = res['range']
		self._units = res['units']
		self._description = res['description']
		self._web_ID = None
		self._web_event_call = None

	def getType(self):
		return self._r_type

	def canRead(self):
		return 'R' in self._access

	def canWrite(self):
		return 'W' in self._access

	def set(self, value):
		old = self._value
		self._value = value
		if self._callback and old != value:
			self._callback(self.obj.o_id, self.obj.o_inst, self.r_id, self.r_inst, self._value)
		if self._debug and self.canWrite():
			print(str(self.obj.device.device_id) + ' ## ' + 'Resource ' + str(self.r_id) + ' changed value to ' + str(
				value))
		if self._web_event_call:
			self._web_event_call(device=self._web_ID, value=self._value, resource=self.r_id)

	def setEventCall(self, webID, callback):
		self._web_ID = webID
		self._web_event_call = callback

	def get(self):
		return self._value

	def describe(self):
		return self._res


class DeviceObject:
	def __init__(self, device, obj, inst, callback, debug=False):
		self.o_id = obj['id']
		self.o_inst = inst
		self.device = device

		self._debug = debug
		self._obj = obj
		self._res_pool = dict()
		self._callback = callback
		self._name = obj['name']
		self._instancetype = obj['instancetype']
		self._mandatory = obj['mandatory']
		self._description = obj['description']
		self._res_pool = dict(obj['resourcedefs'])
		for resource in self._res_pool:
			self._res_pool[resource] = Resource(self, self._res_pool[resource], resource[1], self._callback,
												self._debug)

	def get(self, r_id, r_inst):
		if (r_id, r_inst) in self._res_pool:
			if self._res_pool[r_id, r_inst].canRead():
				return self._res_pool[r_id, r_inst].get()
			else:
				print(str(self.device.device_id) + ' ## Error: ' + 'Resource ' + str(r_id) + ' is not readable.')

	def getResource(self, r_id, r_inst):
		if (r_id, r_inst) in self._res_pool:
			return self._res_pool[r_id, r_inst]
		return None

	def set(self, r_id, r_inst, value):
		if (r_id, r_inst) in self._res_pool:
			if self._res_pool[r_id, r_inst].canWrite():
				self._res_pool[r_id, r_inst].set(value)
			else:
				print(str(self.device.device_id) + ' ## Error: ' + 'Resource ' + str(r_id) + ' is not writable.')

	def getIDlist(self):
		return list(self._res_pool.keys())

	def describe(self):
		return self._obj


class Device(Thread):
	def __init__(self, device_id, \
					objs_def, devices_topic, config_topic, \
					mqtt_tenant, \
					host='sonata4.local', \
					port=1883, \
					username=None, \
					password=None, \
					debug=False):

		super(Device, self).__init__()
		self.device_id = device_id

		self.mqtt_tenant = mqtt_tenant
		self.devices_topic = mqtt_tenant + devices_topic
		self.config_topic = mqtt_tenant + config_topic
		self.main_topic = mqtt_tenant + devices_topic + '/'+ str(device_id)

		self._subscribed_topics = []
		self._publish_topics = []

		self.connected = False
		self._debug = debug
		self._client = Client(client_id=device_id)
		self._client.on_connect = self._on_connect
		self._client.on_message = self._on_message
		if username:
			self._client.username_pw_set(username, password)

		self._stop_event = Event()
		self._host = host
		self._port = port
		self._qos = 0
		self._objs = dict(objs_def)
		for obj in self._objs:
			self._objs[obj] = DeviceObject(self, self._objs[obj], obj[1], self.event_callback, self._debug)

	def getDescription(self):
		answer = dict()
		answer['device'] = dict()
		answer['device']['device_id'] = self.device_id
		answer['objects'] = []
		for obj_id, obj_inst in self._objs:
			o = dict()
			o['object_id'] = obj_id
			o['object_instance'] = obj_inst
			o['resources'] = []
			for res_id, res_inst in self.getObject(obj_id, obj_inst).getIDlist():
				r = dict()
				r['resource_id'] = res_id
				r['resource_instance'] = res_inst
				o['resources'].append(r)
			answer['objects'].append(o)
		return answer

	def _on_connect(self, client, userdata, flags, rc):
		print('%-58s ## Connected' % (self.device_id,))
		self.connected = True
		client.subscribe(self.devices_topic, 1)
		client.subscribe(self.main_topic, 1)
		print('Topic: ' + self.config_topic)
		print('Message: ' + json.dumps(self.getDescription()))
		#self._client.publish(self.config_topic, payload=json.dumps(self.getDescription()), qos=self._qos)

	def _on_message(self, client, userdata, msg):
		topic = msg.topic
		data = json.loads(msg.payload.decode("utf-8"))
		if 'operation' in data:
			self.handle_operation(data['operation'])
		elif 'event' in data:
			self.handle_event(data['event'], topic)

	def handle_operation(self, operation):
		if 'metaData' in operation:
			metadata = operation['metaData']
			if 'payloadData' in operation:
				payload = operation['payloadData']

			if 'operation' in metadata:
				op = metadata['operation']

				if op == 'subscribe_topic':
					if 'value' in payload:
						topics = payload['value'].split(';')
						for topic in topics:
							self._client.subscribe(topic)
							if topic not in self._subscribed_topics:
								self._subscribed_topics.append(topic)

				elif op == 'unsubscribe_topic':
					if 'value' in payload:
						topics = payload['value'].split(';')
						for topic in topics:
							self._client.unsubscribe(topic)
							if topic in self._subscribed_topics:
								self._subscribed_topics.remove(topic)

				elif op == 'add_publish_topic':
					if 'value' in payload:
						topics = payload['value'].split(';')
						for topic in topics:
							if topic not in self._publish_topics:
								self._publish_topics.append(topic)

				elif op == 'remove_publish_topic':
					if 'value' in payload:
						topics = payload['value'].split(';')
						for topic in topics:
							if topic in self._publish_topics:
								self._publish_topics.remove(topic)

				elif op == 'report_device_info':
					if 'publish_on' in payload:
						print('Topic: ' + payload['publish_on'])
						print('Message: ' + json.dumps(self.getDescription()))
						#self._client.publish(payload['publish_on'], payload=json.dumps(self.getDescription()), qos=self._qos)

				elif op == 'unsubscribe_all':
					for topic in self._subscribed_topics:
						self._client.unsubscribe(topic)
					self._subscribed_topics = []

				elif op == 'remove_publish_all':
					self._publish_topics = []

	def handle_event(self, event, topic):
		if 'metaData' not in event:
			return None
		metadata = event['metaData']
		payload = event['payloadData']

		if 'correlationData' in event:
			correlation = event['correlationData']
			obj_id = correlation['object']
			obj_inst = correlation['object_instance']
			res_id = correlation['resource']
			res_inst = correlation['resource_instance']

		else:
			try:
				dtopic = topic.split('/')[-4:]
				if len(dtopic) != 4:
					return None
				data = []
				for n in dtopic:
					if n != 'all':
						data.append(int(n))
					else:
						data.append(-1)
				obj_id = data[0]
				obj_inst = data[1]
				res_id = data[2]
				res_inst = data[3]
			except Exception:
				return None

		if 'operation' in metadata:
			op = metadata['operation']

			if obj_id != -1 and obj_inst != -1:
				objects = [(obj_id, obj_inst)] if (obj_id, obj_inst) in self._objs else []
			elif obj_id != -1 and obj_inst == -1:
				objects = [(x,y) for (x,y) in list(self._objs.keys()) if x == obj_id]
			elif obj_id == -1 and obj_inst != -1:
				objects = [(x,y) for (x,y) in list(self._objs.keys()) if y == obj_inst]
			else:
				objects = list(self._objs.keys())

			for (obj,i) in objects:
				o = self.getObject(obj, i)
				if not o:
					continue
				if res_id != -1 and res_inst != -1:
					resources = [(res_id, res_inst)]
				elif res_id != -1 and res_inst == -1:
					resources = [(x,y) for (x,y) in o.getIDlist() if x == res_id]
				elif res_id == -1 and res_inst != -1:
					resources = [(x,y) for (x,y) in o.getIDlist() if y == res_inst]
				else:
					resources = o.getIDlist()

				for (resource, j) in resources:
					if op == 'set':
						if 'value' in payload:
							o.set(resource, j, payload['value'])
					elif op == 'get':
						self.event_callback(obj, i, resource, j, o.get(resource, j))

	def event_callback(self, obj_id, obj_inst, r_id, r_inst, value):
		message = dict()
		message['event'] = dict()
		message['event']['payloadData'] = {
			'device': self.device_id,
			'object': obj_id,
			'object_instance': obj_inst,
			'resource': r_id,
			'resource_instance': r_inst,
			'value': value
		}
		for topic in self._publish_topics:
			#self._client.publish(topic+'/'+'/'.join([str(obj_id),str(obj_inst),str(r_id),str(r_inst)]), payload=json.dumps(message), qos=self._qos)
			if self._debug: print('%-58s ## Sending %s to %s' % (
				self.device_id, json.dumps(message), topic))

	def run(self):
		try:
			self._client.connect(host=self._host, port=self._port)

			while not self._stop_event.is_set():
			 	self._client.loop()
			#self._client.loop_forever()

			print('%-58s ## Disconnecting...' % (self.device_id,))
			self._client.disconnect()
			time.sleep(0.5)

		except ConnectionRefusedError:
			print('%-58s ## Could not connect. Maybe server is down?' % (self.device_id,))

	def stop(self):
		self._stop_event.set()
	#self._client.disconnect()

	def getObject(self, o_id, o_inst):
		if (o_id,o_inst) in self._objs:
			return self._objs[o_id, o_inst]
		return None
