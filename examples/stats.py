#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display basic system information.

Needs psutil (+ dependencies) installed::

  $ sudo apt-get install python-dev
  $ sudo -H pip install psutil
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from socket import AddressFamily


if os.name != 'posix':
    sys.exit('{} platform not supported'.format(os.name))

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

try:
    import psutil
except ImportError:
    print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
    sys.exit()


# TODO: custom font bitmaps for up/down arrows
# TODO: Load histogram


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n

def ip_addr():
    addrs = psutil.net_if_addrs()
    for name, data in addrs.items():
        if name == 'lo':
            continue
        for e in data:
            if e.family == AddressFamily.AF_INET:
                return 'IP: ' + e.address
    return 'IP: not found'


def cpu_percent():
    cpu = psutil.cpu_percent()
    temp = next(iter(psutil.sensors_temperatures().values()))[0].current
    return "CPU: %.0f%%  %.0f°C" % (cpu, temp)


def mem_usage():
    usage = psutil.virtual_memory()
    return "RAM: %s %.0f%%" \
        % (bytes2human(usage.used), 100 - usage.percent)


def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD: %s %.0f%%" \
        % (bytes2human(usage.used), usage.used/usage.total * 100)


def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx %s Rx %s" % \
           (iface, bytes2human(stat.bytes_sent), bytes2human(stat.bytes_recv))



def stats(device):
    global row
    # use custom font
#     font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'C&C Red Alert [INET].ttf'))
#     font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'code2000.ttf'))
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'FreePixel.ttf'))
    font2 = ImageFont.truetype(font_path, 12)
    row = 0
    
    def draw_text(text):
        global row
        draw.text((0, row), text, font=font2, fill="white")
        row += (font2.size - 2)
    
    with canvas(device) as draw:
        draw_text(datetime.now().strftime("%b %d %H:%M:%S"))
        draw_text(ip_addr())
        draw_text(cpu_percent())
        if device.height >= 32:
            draw_text(mem_usage())
        if device.height >= 64:
            draw_text(disk_usage('/'))
            try:
                draw_text(network('wlan0'))
            except KeyError:
                #print("no wifi enabled/available")
                pass
            try:
                draw_text(network('eth0'))
            except KeyError:
                #print("no lan enabled/available")
                pass
        draw.text((0, row), str(row))

def main():
    while True:
        stats(device)
        time.sleep(5)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
