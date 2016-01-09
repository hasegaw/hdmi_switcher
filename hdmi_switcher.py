#! python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import serial


class HDMISwitcher(object):

    res_1080p = 0
    res_720p = 1
    res_1080i = 2
    res_1024x768 = 3
    res_1360x768 = 4
    mode_four_channels = 0x00
    mode_main_and_sub = 0x01
    mode_single_channel = 0x02

    def add_checksum(self, cmd):
        assert len(cmd) == 12
        cmd = bytearray(cmd)
        checksum = 0x100

        for c in cmd:
            checksum = checksum - c
            if checksum < 0:
                checksum += 0x100

        cmd.append(checksum)
        return cmd

    def cmd_resolution(self, resolution):
        assert resolution >= 0
        assert resolution <= 4
        cmd = bytearray([0xa5, 0x5b, 0x08, 0x06, resolution, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.serial.write(self.add_checksum(cmd))

    def query_resolution(self):
        cmd = bytearray([0xa5, 0x5b, 0x09, 0x06, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.serial.write(self.add_checksum(cmd))
        self.serial.flushInput()
        self.serial.write(self.add_checksum(cmd))
        z = self.serial.read(13)
        resolution = int(z[4])
        return resolution

    def cmd_switch_port(self, port):
        assert port >= 1
        assert port <= 4
        cmd = bytearray([0xa5, 0x5b, 0x02, 0x03, port, 0x00,
                         0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.serial.write(self.add_checksum(cmd))

    def query_switch_port(self):
        cmd = bytearray([0xa5, 0x5b, 0x02, 0x01, 0x01, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        expected_response = bytearray([0xa5, 0x5b, 0x02, 0x01, 0x01, 0x00])
        self.serial.flushInput()
        self.serial.write(self.add_checksum(cmd))
        z = self.serial.read(13)
        port = int(z[6])
        return port

    def cmd_mode(self, mode):
        assert mode >= 0
        assert mode <= 2
        cmd = bytearray([0xa5, 0x5b, 0x08, 0x05, mode, 0x00,
                         0x01, 0x00, 0x00, 0x00, 0x00, 0x00])

        self.serial.write(self.add_checksum(cmd))

    def query_mode(self):
        cmd = bytearray([0xa5, 0x5b, 0x09, 0x05, 0x00, 0x00,
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        expected_response = bytearray([0xa5, 0x5b, 0x09, 0x05])
        self.serial.flushInput()
        self.serial.write(self.add_checksum(cmd))
        z = self.serial.read(13)
        mode = int(z[4])
        return mode

    def query_mode_str(self):
        return {
            self.mode_four_channels: 'four_channels',
            self.mode_main_and_sub: 'main_and_sub',
            self.mode_single_channel: 'single_channel',
        }[self.query_mode()]

    def __init__(self, tty_filename):
        self.serial = serial.Serial(tty_filename, 115200)

if __name__ == "__main__":
    import time
    import sys
    try:
        f = sys.argv[1]
    except:
        f = '/dev/tty.usbserial-FTZ2AKZU'

    switcher = HDMISwitcher(f)

    # test 1: MODE=0 (quad)
    switcher.cmd_mode(0)
    time.sleep(1)
    mode = switcher.query_mode()
    assert mode == 0
    time.sleep(5)

    # test 2: MODE=1 (1 + 3)
    switcher.cmd_mode(1)
    time.sleep(1)
    mode = switcher.query_mode()
    time.sleep(1)
    assert mode == 1
    for i in range(4):
        switcher.cmd_switch_port(i + 1)
        time.sleep(1)
        port = switcher.query_switch_port()
        assert port == i + 1
        time.sleep(3)

    time.sleep(5)

    # test 3: MODE=2 single input
    switcher.cmd_mode(2)
    time.sleep(1)
    mode = switcher.query_mode()
    time.sleep(1)
    assert mode == 2
    for i in range(4):
        switcher.cmd_switch_port(i + 1)
        time.sleep(1)
        port = switcher.query_switch_port()
        assert port == i + 1
        time.sleep(3)
