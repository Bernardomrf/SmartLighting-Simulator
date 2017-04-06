from threading import Thread, Event
import datetime
import time

class MDAGenerator(Thread):
    def __init__(self, filename, resource, debug=False):
        super(MDAGenerator, self).__init__()
        self._debug = debug
        self._resource = resource
        self._r_id = self._resource.r_id
        self._r_inst = self._resource.r_inst
        self._o_id = self._resource.obj.o_id
        self._o_inst = self._resource.obj.o_inst
        self._d_id = self._resource.obj.device.device_id
        self._stop_event = Event()
        self._filename = filename
        self._file = reversed(open(self._filename, "r").readlines())
        self._last = None

    def run(self):
        print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Starting...' \
              % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))

        while (not self._resource.obj.device.connected) and (not self._stop_event.is_set()):
            print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Waiting for connection...' \
                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))
            self._stop_event.wait(2)

        while not self._stop_event.is_set():
            raw_value = ''
            while raw_value == '':
                try:
                    raw_value = next(self._file).strip()
                    if self._last is None and raw_value != '':
                        self._last = datetime.datetime.strptime(raw_value.split(',')[0], "%b %d %H:%M:%S") \
                            .replace(year=datetime.datetime.now().year)
                        raw_value = ''
                except StopIteration:
                    self._last = None
                    self._file = reversed(open(self._filename, "r").readlines())

            current = datetime.datetime.strptime(raw_value.split(',')[0], "%b %d %H:%M:%S") \
                .replace(year=datetime.datetime.now().year)

            t = (current - self._last).seconds
            self._last = current

            self._resource.set(1)
            if self._debug: print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Setting value %s' \
                                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst, str(1)))
            time.sleep(1)
            self._resource.set(0)
            if self._debug: print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Setting value %s' \
                                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst, str(0)))

            if self._debug: print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Next event in %d seconds' \
                                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst, t))

            self._stop_event.wait(t)
            if not self._resource.obj.device.isAlive():
                self.stop()

    def stop(self):
        if self.isAlive():
            print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Stopping...' \
                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))
            self._stop_event.set()
