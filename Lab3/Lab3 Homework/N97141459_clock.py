#!/usr/bin/env python3

from datetime import datetime
from time import sleep

import tm1637


CLK = 23
DIO = 24
BRIGHTNESS = 7


def main():
    display = tm1637.TM1637(clk=CLK, dio=DIO, brightness=BRIGHTNESS)
    colon = False

    try:
        while True:
            current_time = datetime.now()
            colon = not colon
            display.numbers(
                current_time.hour,
                current_time.minute,
                colon=colon,
            )
            sleep(1)
    except KeyboardInterrupt:
        display.write([0, 0, 0, 0])
    finally:
        del display


if __name__ == "__main__":
    main()