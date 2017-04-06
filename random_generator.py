from threading import Thread, Event
import random, time


def random_value(v_type, v_min=0, v_max=100):
    if v_type.lower() == 'boolean':
        return random.randint(0, 1)
    elif v_type.lower() == 'integer':
        return random.randint(v_min, v_max)
    elif v_type.lower() == 'float':
        return round(random.uniform(v_min, v_max), 2)
    else:
        return None


class RandomGenerator(Thread):
    def __init__(self, periodicity, min_val, max_val, resource, debug=False):
        super(RandomGenerator, self).__init__()
        self._periodicity = periodicity
        self._min_val = min_val
        self._max_val = max_val
        self._resource = resource
        self._r_id = self._resource.r_id
        self._r_inst = self._resource.r_inst
        self._o_id = self._resource.obj.o_id
        self._o_inst = self._resource.obj.o_inst
        self._d_id = self._resource.obj.device.device_id
        self._stop_event = Event()

    def run(self):
        print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Starting...' \
              % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))

        while (not self._resource.obj.device.connected) and (not self._stop_event.is_set()):
            print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Waiting for connection...'
                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))
            self._stop_event.wait(2)

        while not self._stop_event.is_set():
            r = random_value(self._resource.getType(), self._min_val, self._max_val)
            if self._resource.getType().lower() == 'boolean':
                if r == 1:
                    self._resource.set(r)
            else:
                self._resource.set(r)
            if r == 1 and self._resource.getType().lower() == 'boolean':    ## Only usefull to reset motion sensors
                time.sleep(1)
                self._resource.set(0)
            self._stop_event.wait(self._periodicity)
            if not self._resource.obj.device.isAlive():
                self.stop()

    def stop(self):
        if self.isAlive():
            print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Stopping...' \
                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))
            self._stop_event.set()
