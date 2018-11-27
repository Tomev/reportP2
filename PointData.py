from enum import IntEnum


class LineParts(IntEnum):
    TIME = 0
    CHAN_A = 1
    CHAN_B = 2


class P2Point:

    time = 0
    chan = 0

    def __init__(self, line, channel):
        line_parts = line.split('\t')
        self.time = line_parts[LineParts.TIME]
        self.chan = line_parts[channel]


