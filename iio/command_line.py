import argparse
from pprint import pprint
import sys
from time import time, sleep
from iio import IIO


def main():
    parser = argparse.ArgumentParser(description='IIO Device Client')
    parser.add_argument('--show-devices', action='store_true',
                        help='Scan and report for devices')
    parser.add_argument('--read-raw', type=int, nargs='?',  help='Read raw values for devices')
    parser.add_argument('--read', type=int, help='Number of records to read')
    parser.add_argument('--enable', help='Enable a device/channel. Format is device:channel')
    parser.add_argument('--disable', help='Disable a device/channel. Format is device:channel')
    parser.add_argument('sensor', nargs='?', help="Sensor to use")

    parser.add_argument('--start-buffer', help='Start buffering for devices named')
    parser.add_argument('--stop-buffer', help='Start buffering for devices named')

    parser.add_argument('--read-data', help='Read data from buffer')
    parser.add_argument('--read-time', default=5, help='How long to red data for')

    args = parser.parse_args()
    print(args)

    iios = IIO()

    if args.show_devices:
        print(iios.status_string())
        sys.exit(0)

    if args.read_raw is not None:
        print("For every device I will\n  - enable all channels\n  - read {} values\n  - disable all channels\n".
              format(args.read_raw))
        print("NB. values are RAW and unscaled")
        for dev in iios.devices:
            dev.enable_channels()
            print(dev.name)
            vals = [dev.read_raw() for x in range(args.read_raw)]
            pprint(vals)
            dev.disable_channels()
        sys.exit(0)

    if args.enable is not None:
        if ':' in args.enable:
            dev_name, chan = args.enable.split(':')
            for dev in iios.devices:
                if dev.name == dev_name:
                    if dev.enable_channel_by_name(chan):
                        print("Channel(s) {} enabled for {}".format(chan, dev.name))
                    else:
                        print("Failed to enable any channel(s) {} for {}".format(chan, dev.name))
        else:
            for dev in iios.devices:
                if dev.name == args.enable:
                    dev.enable_channels()
                    print("Channels enabled for {}".format(dev.name))
        sys.exit(0)

    if args.disable is not None:
        if ':' in args.disable:
            dev_name, chan = args.disable.split(':')
            if iios.disable_device_and_channel(dev_name, chan):
                print("Channel(s) {} disabled for {}".format(chan, dev_name))
            else:
                print("Failed to disable any channel(s) {} for {}".format(chan, dev_name))
        else:
            iios.disable_device(args.disable)
            print("Channels disabled for {}".format(args.disable))
        sys.exit(0)

    if args.start_buffer is not None or args.read_data is not None:
        dev_name = args.start_buffer or args.read_data
        for dev in iios.devices:
            if dev.name == dev_name:
                dev.start_buffer()
                print("Buffering started for {}".format(dev.name))

    if args.read_data is not None:
        data = {}
        for dev in iios.devices:
            if dev.name == args.read_data:
                dev.start_collecting()
        sleep(float(args.read_time))
        for dev in iios.devices:
            if dev.name == args.read_data:
                data[dev.name] = dev.stop_collecting()
                dev.disable_channels()
        pprint(data)


    if args.stop_buffer is not None or args.read_data is not None:
        dev_name = args.start_buffer or args.read_data
        for dev in iios.devices:
            if dev.name == dev_name:
                dev.stop_buffer()
                print("Buffering stopped for {}".format(dev.name))
