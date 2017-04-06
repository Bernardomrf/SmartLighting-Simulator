from threading import Thread, Event


def celsius(Fahrenheit):
    return round((Fahrenheit - 32) * 5.0 / 9.0, 2)


def getValue(raw_value, v_type):
    if v_type.lower() == 'boolean' or v_type.lower() == 'integer':
        try:
            return int(raw_value)
        except ValueError:
            return int(float(raw_value))
    elif v_type.lower() == 'float':
        return round(float(raw_value), 2)
    else:
        return raw_value


class RawGenerator(Thread):
    def __init__(self, filename, column, periodicity, resource, csv=False, convert_to_celsius=False, ignore_lines=0,
                 debug=False):
        super(RawGenerator, self).__init__()
        self._debug = debug
        self._periodicity = periodicity
        self._resource = resource
        self._r_id = self._resource.r_id
        self._r_inst = self._resource.r_inst
        self._o_id = self._resource.obj.o_id
        self._o_inst = self._resource.obj.o_inst
        self._d_id = self._resource.obj.device.device_id
        self._column = column
        self._stop_event = Event()
        self._filename = filename
        self._file = open(self._filename, 'r')
        self._csv = csv
        self._convert_to_celsius = convert_to_celsius
        self._delimiter = ',' if self._csv else ' '
        for i in range(0, ignore_lines):
            if self._debug: print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Ignoring line %d' \
                                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst, i + 1))
            next(self._file)

    def run(self):
        print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Starting...' \
              % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))

        while (not self._resource.obj.device.connected) and (not self._stop_event.is_set()):
            print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Waiting for connection...' \
                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))
            self._stop_event.wait(2)

        while not self._stop_event.is_set():
            try:
                raw_value = next(self._file).split(self._delimiter)[self._column].strip()
            except StopIteration:
                self._file.close()
                self._file = open(self._filename, 'r')
                raw_value = next(self._file).split(self._delimiter)[self._column].strip()

            if self._debug: print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## RAW VALUE: %s' \
                                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst, raw_value))
            value = getValue(raw_value, self._resource.getType())
            if self._convert_to_celsius:
                value = celsius(value)
            self._resource.set(value)
            if self._debug: print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Setting value %s' \
                                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst, str(value)))
            self._stop_event.wait(self._periodicity)
            if not self._resource.obj.device.isAlive():
                self.stop()

    def stop(self):
        if self.isAlive():
            print('%-22s Obj:(%d,%d)/Res:(%d,%d) generator ## Stopping...' \
                  % (self._d_id, self._o_id, self._o_inst, self._r_id, self._r_inst))
            self._file.close()
            self._stop_event.set()
