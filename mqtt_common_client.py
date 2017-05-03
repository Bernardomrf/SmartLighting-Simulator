import uuid, time
import paho.mqtt.client as mqtt
import threading

class _Singleton(type):
	__singleton_lock = threading.Lock()
	_instances = {}
	def __call__(cls, *args, **kwargs):
		with cls.__singleton_lock:
			if (cls, args, tuple(sorted(kwargs.items()))) not in cls._instances:
				cls._instances[(cls, args, tuple(sorted(kwargs.items())))] = super(_Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[(cls, args, tuple(sorted(kwargs.items())))]

class Singleton(_Singleton('SingletonMeta', (object,), {})): pass

class MQTTCommonClient(Singleton):
	def __init__(self, *args, **kwargs):
		self.mqtt_client_id = str(uuid.uuid4())
		self.connected = False
		self.lock = threading.Lock()

		self._client = mqtt.Client(client_id=self.mqtt_client_id,
								clean_session=kwargs['clean_session'],
								protocol=kwargs['protocol'])
		if kwargs['username']:
			self._client.username_pw_set(kwargs['username'], kwargs['password'])

		self._client.on_connect = self._on_connect
		self._client.on_disconnect = self._on_disconnect
		self._client.on_message = self._on_message
		self._client.on_publish = None		# TODO
		self._client.on_subscribe = None	# TODO
		self._client.on_unsubscribe = None	# TODO
		self._client.on_log = None			# TODO

		self.topic_clients = {}

		self._client.connect(kwargs['host'],kwargs['port'],kwargs['keepalive'], kwargs['bind_address'])
		self._client.loop_start()
		for topic in self.topic_clients.keys():
			self._client.subscribe(topic)

	def _on_connect(self, client, userdata, flags, rc):
		with self.lock:
			self.connected = True
			for topic in self.topic_clients.keys():
				self._client.subscribe(topic)

	def _on_disconnect(self, client, userdata, rc):
		self.connected = False

	def _on_message(self, client, userdata, msg):		# TODO: Support '+' wildcard
		#print(msg.payload.decode("utf-8"))
		topic = msg.topic
		deliver = False
		if topic in self.topic_clients:
			deliver = True
		else:
			for t in self.topic_clients.keys():
				if t[-1] == '#':
					if topic.startswith(t[:-2]):
						topic = t
						deliver = True
		if deliver:
			for c in self.topic_clients[topic]:
				if c.on_message:
					c.on_message(c, c.userdata, msg)

	def publish(self, client, topic, payload, qos, retain):
		with self.lock:
			#self._client.publish(topic, payload, qos, retain)
			time.sleep(0.001)		# WITHOUT THIS IT WONT PUBLISH WHEN ON MULTIPLE PUBLISHES

	def subscribe(self, client, topic, qos):
		with self.lock:
			if topic not in self.topic_clients:
				self.topic_clients[topic] = []
			if client not in self.topic_clients[topic]:
				self.topic_clients[topic].append(client)
			self._client.subscribe(topic, qos)

	def unsubscribe(self, client, topic):
		with self.lock:
			if topic in self.topic_clients:
				self.topic_clients[topic].remove(client)
				self._client.unsubscribe(topic)

	def disconnectClient(self, client):
		with self.lock:
			for clients in self.topic_clients.values():
				if client in clients:
					clients.remove(client)



class MQTTVirtualClient(object):
	def __init__(self, client_id=None, clean_session=True, userdata=None, protocol=mqtt.MQTTv31):
		self.client_id = client_id if client_id else str(uuid.uuid4())
		self.clean_session = clean_session
		self.userdata = userdata
		self.protocol = protocol

		self.username = None
		self.password = None

		self._common_client = None

		self.on_connect = None
		self.on_message = None
		self.on_disconnect = None
		self.on_publish = None		# TODO
		self.on_subscribe = None	# TODO
		self.on_unsubscribe = None	# TODO
		self.on_log = None			# TODO

		self.event = threading.Event()

	def username_pw_set(self, username, password = None):
		self.username = username
		self.password = password

	def connect(self, host='sonata4.local', port=1883, keepalive=60, bind_address=""):
		self._common_client = MQTTCommonClient(host=host,
											port=port,
											keepalive=keepalive,
											bind_address=bind_address,
											clean_session=self.clean_session,
											protocol=self.protocol,
											username=self.username,
											password=self.password)
		if self.on_connect:
			self.on_connect(self, self.userdata, 1, 0)
		self.event.clear()

	def disconnect(self):
		self._common_client.disconnectClient(self)
		self._common_client = None
		if self.on_disconnect:
			self.on_disconnect(self, self.userdata, 0)
		self.event.set()

	def publish(self, topic, payload=None, qos=0, retain=False):
		if self._common_client:
			pass
			#self._common_client.publish(self, topic, payload, qos, retain)

	def loop(self, timeout=1.0):
		self.event.wait(timeout)

	def loop_forever(self):
		self.event.wait()

	def subscribe(self, topic, qos=0):
		if self._common_client:
			self._common_client.subscribe(self, topic, qos)

	def unsubscribe(self, topic):
		if self._common_client:
			self._common_client.unsubscribe(self, topic)
