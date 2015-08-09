from os import listdir, path


class IIOBase(object):
    """ Base class for IIO objects that need to access files provided by
        a
    """
    def __init__(self, dev_path):
        self.dev_path = dev_path

    def read_true_false(self, filename, default=True):
        _fn = path.join(self.dev_path, filename)
        if not path.exists(_fn):
            return default
        with open(_fn, 'r') as fh:
            return '1' in fh.read().strip()

    def read_string(self, filename, default=''):
        _fn = path.join(self.dev_path, filename)
        if not path.exists(_fn):
            return default
        with open(_fn, 'r') as fh:
            return fh.read().strip()

    def read_number(self, filename, default=0):
        _fn = path.join(self.dev_path, filename)
        if not path.exists(_fn):
            return default
        with open(_fn, 'r') as fh:
            num = fh.read().strip()
            if '.' in num:
                return float(num)
            return int(num)

    def write_true_false(self, filename, val):
        _fn = path.join(self.dev_path, filename)
        with open(_fn, 'w') as out:
            out.write("1" if val is True else "0")

    def write_string(self, filename, val):
        _fn = path.join(self.dev_path, filename)
        with open(_fn, 'w') as out:
            out.write(val)

    def read_directory(self, name=''):
        for _fn in listdir(path.join(self.dev_path, name)):
            yield path.join(name, _fn)
