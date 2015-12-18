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

    def cmd_switch_port(self, port):
        assert port >= 1
        assert port <= 4
        cmd = bytearray([0xa5, 0x5b, 0x02, 0x03, port, 0x00,
                         0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.serial.write(self.add_checksum(cmd))

    def cmd_mode(self, mode):
        assert mode >= 0
        assert mode <= 2
        cmd = bytearray([0xa5, 0x5b, 0x08, 0x05, mode, 0x00,
                         0x01, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.serial.write(self.add_checksum(cmd))

    def __init__(self, tty_filename):
        self.serial = serial.Serial(tty_filename, 115200)

if __name__ == "__main__":
    import time

    switcher = HDMISwitcher('/dev/ttyUSB0')

    # test 1: MODE=0 (quad)
    switcher.cmd_mode(0)
    time.sleep(5)

    # test 2: MODE=1 (1 + 3)
    switcher.cmd_mode(1)
    for i in range(4):
        switcher.cmd_switch_port(i + 1)
        time.sleep(3)

    time.sleep(5)

    # test 3: MODE=2 single input
    switcher.cmd_mode(2)
    for i in range(4):
        switcher.cmd_switch_port(i + 1)
        time.sleep(3)
