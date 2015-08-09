from os import path
import re
from struct import unpack, calcsize

from .base import IIOBase


class IIOChannel(IIOBase):
    def __init__(self, device, name):
        IIOBase.__init__(self, path.join(device.dev_path, 'scan_elements'))
        self.name = name
        self.channel_type = '_'.join(name.split('_')[:2])
        self.enabled = False
        self.scale = 1.000
        self.data_fmt = self.data_sz = None
        self.storage_sz = self.n_vals = None
        self.shift = 0
        self.value = None

        self.index = self.read_number("{}_index".format(self.name))
        self.type = self.read_string("{}_type".format(self.name), None)
        if self.type is not None:
            self._parse_type()

        self.get_status()

    def __repr__(self):
        return self.name

    def get_status(self):
        self.enabled = self.read_true_false("{}_en".format(self.name), False)

    def parse_raw(self, val):
        """ Parse the raw data from a _raw endpoint. This allows the multiple value
            case to be easily handled.
        :return: Value or list of values.
        """
        num_ = lambda x: int(x) if '.' not in x else float(x)
        if self.n_vals == 1:
            return num_(val)
        return [num_(x) for x in val.split(' ')]

    def parse_data(self, data):
        """ Parse packed data read from /dev endpoint. Stored values will be available as
            .value
        :param data: Bytes from /dev
        :return: Number of bytes read.
        """
        # todo handle shift
        unpacked = unpack(self.data_fmt, data[:self.data_sz])
        if self.n_vals == 1:
            self.value = unpacked[0] * self.scale
        else:
            self.value = [x * self.scale for x in unpacked[:self.n_vals]]
        return self.storage_sz

    def enable(self):
        if self.enabled:
            return
        self.write_true_false("{}_en".format(self.name), True)
        self.get_status()

    def disable(self):
        if not self.enabled:
            return
        self.write_true_false("{}_en".format(self.name), False)
        self.get_status()

    # Private functions below!
    def _parse_type(self):
        """
        Form is [be|le]:[s|u]bits/storagebits[>>shift].
        """
        ck = re.match("^(be|le):(s|u)(\d+)\/(\d+)(X\d+)?>>(\d+)$", self.type)
        if ck is None:
            return

        fmt = "<" if ck.group(1) == 'le' else ">"

        self.n_vals = 1 if ck.group(5) is None else int(ck.group(5)[1:])
        if self.n_vals > 1:
            fmt += "{}".format(self.n_vals)
            self.value = [None for n in range(self.n_vals)]
        else:
            self.value = None

        if ck.group(3) == '32':
            fmt += "i" if ck.group(2) == 's' else "I"
        elif ck.group(3) == '16':
            fmt += "h" if ck.group(2) == 's' else "H"

        self.storage_sz = (int(ck.group(4)) / 8) * self.n_vals
        self.data_fmt = fmt
        self.data_sz = calcsize(fmt)
        self.shift = ck.group(5)
