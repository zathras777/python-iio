import os
from os import path


from .base import IIOBase
from .channel import IIOChannel
from .collector import IIOCollector


class IIODevice(IIOBase):
    """ A device on an IIO bus may be a device (e.g. an SDR radio) or it may
        be a sensor (e.g. 3d accelerometer). In ether case the methods of accessing
        and controlling the device are the same.

        Information about the device is found via the endpoints listed in the device
        directory under /sys/bus/iio/devices.
        Each device on an IIO bus is a collection of channels, each of which
        may be enabled to provide information via the sensor object.
        Each sensor is accessed/controlled via the endpoints in /sys/bus/iio/devices.
        Data is provided via an endpoint in the /dev directory.
    """
    def __init__(self, dev_path):
        IIOBase.__init__(self, dev_path)

        self.sys_id = path.basename(dev_path)
        self.devnum = int(self.sys_id[10:])
        self.channels = []

        self.buffering = False
        self.collector = None

        self.name = None
        self.trigger = None
        self.name = self.read_string('name')
        self.buffer_size = 0
        self.scales = {}

        self.get_channels()
        self.check_buffer()

    def __del__(self):
        if self.buffering:
            self.stop_buffer()

    @property
    def is_enabled(self):
        for ch in self.channels:
            if ch.enabled:
                return True
        return False

    def get_channels(self):
        self.buffer_size = 0
        for ch in self.read_directory('scan_elements'):
            sc, ch = ch.split('/')
            if ch.endswith('_en'):
                _ch = IIOChannel(self, ch[:-3])
                if _ch.channel_type not in self.scales:
                    self.scales[_ch.channel_type] = self.read_number(_ch.channel_type + '_scale', 1.000)
                    if self.scales[_ch.channel_type] == 0:
                        self.scales[_ch.channel_type] = 1.000
                _ch.scale = self.scales[_ch.channel_type]
                self.buffer_size += _ch.storage_sz
                self.channels.append(_ch)

    def check_buffer(self):
        self.buffering = self.read_true_false(path.join('buffer', 'enable'))

    def read_raw(self):
        vals = {}
        for ch in self.channels:
            vals[ch.name] = ch.parse_raw(self.read_string('{}_raw'.format(ch.name)))
        return vals

    def has_channel(self, name):
        """ Check if a channel containing the supplied string is available in this device.
        :param name: String to look for.
        :return: True or False
        """
        for d in self.channels:
            if name in d.name:
                return True
        return False

    def enable_channels(self):
        """ Enable all available channels. """
        for d in self.channels:
            d.enable()

    def enable_channel_by_name(self, name):
        """ Enable all channels that contain name. Case sensitive.
        :param name: Channel string.
        :return: True or False
        """
        rv = False
        for d in self.channels:
            if name in d.name:
                d.enable()
                rv = True
        return rv

    def disable_channels(self):
        """ Disable all available channels. """
        if self.buffering:
            self.stop_buffer()
        for d in self.channels:
            d.disable()

    def disable_channel_by_name(self, name):
        """ Disable all channels that contain name. Case sensitive.
        :param name: Channel string.
        :return: True or False
        """
        rv = False
        for d in self.channels:
            if name in d.name:
                d.disable()
                rv = True
        return rv

    # Buffer operations
    def start_buffer(self):
        print("START!")
        if self.buffering:
            return
        if not self.is_enabled:
            self.enable_channels()

        self.trigger = "{}-dev{}".format(self.name, self.devnum)
        self.write_string(path.join('trigger', 'current_trigger'), self.trigger)
        self.write_true_false(path.join('buffer', 'enable'), True)
        self.buffering = True

    def stop_buffer(self):
        print("STOP!")
        if self.buffering is False:
            return
        self.write_true_false(path.join('buffer', 'enable'), False)
        self.buffering = False

    def start_collecting(self):
        if not self.buffering:
            self.start_buffer()
        self.collector = IIOCollector(self)
        self.collector.start()

    def collect_data(self):
        if self.collector is None:
            return []
        return self.collector.get_data()

    def stop_collecting(self):
        self.collector.stop()
        self.stop_buffer()
        return self.collector.data

    def read_buffer(self, howmany=10):
        """ Attempt to read a variable number of values from the buffer.
            This attempts to enable the device channels, open the buffer, read some values
            then close the buffer and disable the channels. An attempt is made to not change
            the status of the channels/buffer before/after.
        :param howmany: How many values should be read?
        :return: List with between 0 and howmany values.
        """
        enabled = [c.enabled for c in self.channels]
        if not self.is_enabled:
            self.enable_channels()
        buffer = self.buffering
        if not self.buffering:
            self.start_buffer()

        dev_name = path.join("/dev", self.sys_id)
        inp = os.open(dev_name, os.O_RDONLY)

        buffer_data = []
        for n in range(0, howmany):
            iter_data = {}
            for nn in range(3):
                try:
                    data = os.read(inp, self.buffer_size)
                    pos = 0
                    for el in sorted(self.channels, key=lambda x: x.index):
                        pos += el.parse_data(data[pos:])
                        iter_data[el.name] = el.value
                    break
                except OSError:
                    pass
            if iter_data == {}:
                break
            buffer_data.append(iter_data)

        os.close(inp)

        if not buffer:
            self.stop_buffer()
        for c in range(len(self.channels)):
            if not enabled[c]:
                self.channels[c].disable()

        return buffer_data

    def status(self):
        s = " {:<2d} {:15s} ".format(self.devnum, self.name)
        for c in self.channels:
            if '\n' in s:
                s += "                    "
            s += "{:40s} {:7s} {:2d}     {}\n".format(c.name, str(c.enabled), c.index, c.type)
        return s
