# STM32のプログラム

import pyb
from pyb import LED
from pyb import UART
uart = UART(6, 115200)
uart.init(115200, bits=8, parity=None, stop=1)
led = LED(1)
pull = 0
speed_1 = 0
speed_2 = 0
speed_3 = 0
speed_4 = 0

dir1 = pyb.Pin('PB3', pyb.Pin.OUT_PP)
dir2 = pyb.Pin('PB5', pyb.Pin.OUT_PP)
dir3 = pyb.Pin('PA8', pyb.Pin.OUT_PP)
dir4 = pyb.Pin('PA10', pyb.Pin.OUT_PP)

tim2 = pyb.Timer(2, freq=20000)
tim3 = pyb.Timer(3, freq=20000)
tim4 = pyb.Timer(4, freq=20000)

leg1 = tim3.channel(1, pyb.Timer.PWM, pin=pyb.Pin('PB4'))
leg2 = tim2.channel(3, pyb.Timer.PWM, pin=pyb.Pin('PB10'))
leg3 = tim3.channel(2, pyb.Timer.PWM, pin=pyb.Pin('PA7'))
leg4 = tim4.channel(1, pyb.Timer.PWM, pin=pyb.Pin('PB6'))

dir1.high()
dir2.high()
dir3.low()
dir4.low()

range = 3


def advance():
    dir1.low()
    dir2.low()
    dir3.high()
    dir4.high()


def recession():
    dir1.high()
    dir2.high()
    dir3.low()
    dir4.low()


def go_right():
    dir1.low()
    dir2.high()
    dir3.high()
    dir4.low()


def go_left():
    dir1.high()
    dir2.low()
    dir3.low()
    dir4.high()


def turn_right():
    dir1.low()
    dir2.high()
    dir3.low()
    dir4.high()


def turn_left():
    dir1.high()
    dir2.low()
    dir3.high()
    dir4.low()


check = 0
while True:
    if uart.any():
        read = uart.read(2)

        if (len(read) == 2):
            b_status = read[0:1]
            b_value = read[1:2]
            sv_status = b_status
            value = int.from_bytes(b_value, 'big')
            b_status = int.from_bytes(b_status, 'big')

            # ここの1行でスピードMax値の切り替えを行っている
            value = value >> range

            delay_s = value >> 3
            delay_m = value >> 2
            delay_b = value >> 1
            speed_1 = value
            speed_2 = value
            speed_3 = value
            speed_4 = value

            curve = b_status & 3
            b_status = b_status >> 2
            ral = b_status & 1
            b_status = b_status >> 1
            fab = b_status & 1
            b_status = b_status >> 1
            status = b_status & 3
            b_status = b_status >> 2
            do = b_status & 1

            # 特殊コマンドが送信されるとrangeが切り替わり、Maxのスピード値が変化するようになっている
            # 上から100％、50％、25％、17.5％、8.75％
            if (sv_status == b'!' and b_value == b'!' and range < 5):
                range += 1
            if (sv_status == b'#' and b_value == b'#' and range > 1):
                range -= 1

            range
            # push = str(range)
            # uart.write(range)

            if (do == 0):
                speed_1 = 0
                speed_2 = 0
                speed_3 = 0
                speed_4 = 0

            if (curve == 0):
                pull = 0
            elif(curve == 1):
                pull = delay_s
            elif(curve == 2):
                pull = delay_m
            elif(curve == 3):
                pull = delay_b

            if (status == 0):
                if (fab == 0):
                    advance()
                else:
                    recession()

                if (ral == 0):
                    speed_2 = speed_2 - pull
                    speed_3 = speed_3 - pull
                else:
                    speed_1 = speed_2 - pull
                    speed_4 = speed_3 - pull

            elif (status == 1):
                if (ral == 0):
                    go_right()
                else:
                    go_left()
            elif (status == 2):
                if (ral == 0):
                    go_right()
                    if (fab == 0):
                        speed_2 = 0
                        speed_4 = 0
                    else:
                        speed_1 = 0
                        speed_3 = 0
                else:
                    go_left()
                    if (fab == 0):
                        speed_1 = 0
                        speed_3 = 0
                    else:
                        speed_2 = 0
                        speed_4 = 0
            elif (status == 3):
                if (ral == 0):
                    turn_right()
                else:
                    turn_left()

    leg1.pulse_width_percent(speed_1)
    leg2.pulse_width_percent(speed_2)
    leg3.pulse_width_percent(speed_3)
    leg4.pulse_width_percent(speed_4)
