# STM32通信用マイクロビットのプログラムです。

# マイクロビット通信やUARTの設定
from microbit import *
import radio
radio.config(group=23)
radio.on()
m = radio.receive()
uart.init(baudrate=115200, bits=8, parity=None, stop=1, tx=pin0, rx=pin1)
cheak = 0

# この関数の最後uart.writeでSTM32へ


def send_uart(head, status, value):
    uart_status = 0
    uart_value = 0
    global cheak
    if(head == "b"):
        uart_status = ord(status)
        uart_value = ord(value)
        cheak = 0
        if(uart_value > 20):
            cheak = 1
            display.show("c")
            uart_status = chr(uart_status)
            uart_value = chr(uart_value)
            uart.write(uart_status + uart_value)
    if(head == "a" and cheak != 1):
        uart_status = ord(status)
        uart_value = ord(value)
        if(uart_value > 250):
            display.show("a")
        else:
            display.show("b")
        uart_status = chr(uart_status)
        uart_value = chr(uart_value)
        uart.write(uart_status + uart_value)
    if(head == "!" or head == "#"):
        uart_status = ord(status)
        uart_value = ord(value)
        uart_status = chr(uart_status)
        uart_value = chr(uart_value)
        uart.write(uart_status + uart_value)


def receive_uart():
    if uart.any():
        read = uart.read(1)
        push = str(read)
        radio.send(push)


# ここがメイン
while True:
    # メッセージにデータがたまり3ビット連続で送信されるので分解し引数へ
    message = radio.receive()
    message = str(message)
    head = message[0:1]
    status = message[1:2]
    value = message[2:3]
    send_uart(head, status, value)
