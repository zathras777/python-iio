from os import listdir, path

from .device import IIODevice


class IIO(object):
    """ The IIO object provides access to all the available sensors/devices
        available via the IIO bus.
        Individual sensors/devices are found and IIODevice objects instantiated
        when the class is created.
    """
    IIO_PATH = '/sys/bus/iio/devices'

    def __init__(self):
        """ Create the object and find available devices.
        :return:
        """
        self.devices = []
        self.enabled = 0

        for dev in listdir(self.IIO_PATH):
            # The device directory lists triggers and devices, but we're only
            # interested in devices, so skip over triggers.
            if 'trigger' in dev:
                continue
            _dev = IIODevice(path.join(self.IIO_PATH, dev))
            if _dev.is_enabled:
                self.enabled += 1
            self.devices.append(_dev)

    def __len__(self):
        """
        :return: Number of devices available.
        """
        return len(self.devices)

    @property
    def sensor_list(self):
        return list(set([d.name for d in self.devices]))

    def enable(self):
        for dev in self.devices:
            dev.enable_channels()

    def enable_device(self, dev_name):
        for dev in self.devices:
            if dev_name == dev.name:
                dev.enable_channels()

    def enable_device_and_channel(self, dev_name, chan_name):
        for dev in self.devices:
            if dev.name == dev_name:
                return dev.enable_channel_by_name(chan_name)

    def disable(self):
        """ Disable all sensors. """
        for d in self.devices:
            d.disable_channels()

    def disable_device(self, dev_name):
        for dev in self.devices:
            if dev_name == dev.name:
                dev.disable_channels()

    def disable_device_and_channel(self, dev_name, chan_name):
        for dev in self.devices:
            if dev.name == dev_name:
                return dev.disable_channel_by_name(chan_name)

    def read_sensor(self, name, n=1):
        devs_to_read = []
        for dev in self.devices:
            if name in dev.name:
                devs_to_read.append(dev)
        if len(devs_to_read) == 0:
            return {}
        vals = {}
        for dev in devs_to_read:
            dev.enable_channels()
            dev.start_buffer()

        for _iter in range(n):
            for dev in devs_to_read:
                vals.setdefault(dev.name, []).append(dev.read_buffer())

        for dev in devs_to_read:
            dev.stop_buffer()
            dev.disable_channels()
        return vals

    def status_string(self):
        ss = "Dev Sensor          Channel                                  Enabled? Index Format\n"
        ss += "--- --------------  ---------------------------------------  -------- ----- ------\n"
        for d in self.devices:
            ss += d.status()
        return ss
