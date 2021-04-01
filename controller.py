# コントローラー用マイクロビットのプログラムです。
# ※マイクロビットには専用のコントローラーキットを装着して使用しています
# URL https://www.switch-science.com/catalog/5308/


# マイクロパイソン同士の通信の設定、マス関数のインポート
from microbit import *
import math
import radio
radio.config(group=23)
radio.on()

# 右のジョイスティック(旋回or前後進みながら曲がる)


def rite_joy():

    move = 0  # 全体の送信する1ビット

    # 各ビットの役割ごとに定義された変数。上からリードミーの1ビット目の順番で定義されている
    status = 0
    do = 0
    fab = 0
    ral = 0
    curve = 0
    # 左右のアナログスティックの選定、アナログスティックの横と縦を入れる変数。
    pin2.write_digital(1)
    data_hig = pin1.read_analog()
    data_wid = pin0.read_analog()

    # ここ2つで3,4ビット目の決定
    if(data_hig < 502):
        fab = 1
    else:
        fab = 0

    if(data_wid < 491):
        ral = 1
    else:
        ral = 0
    # ゼロ合わせ
    data_hig -= 502
    data_wid -= 491
    # 正の整数化ここで9ビットとなる
    data_hig = abs(data_hig)
    data_wid = abs(data_wid)
    # アナログスティックの移動範囲を見て2ビット目の決定
    if(data_hig < 10 and data_wid < 10):
        do = 0
    else:
        do = 1
    # 旋回or前後の決定6,5ビット目の決定
    if(data_hig < 25):
        status = 3
    else:
        status = 0
    # 曲がり具合下位2ビットの決定
    if(data_wid < 120):
        curve = 0
    elif(data_wid > 120 and data_wid < 250):
        curve = 1
    elif(data_wid > 250 and data_wid < 380):
        curve = 2
    elif(data_wid > 380):
        curve = 3
    # 速度の決定
    range = int(math.sqrt(data_hig**2+data_wid**2))
    if(range > 512):
        range = 511
    # 9ビットのデータを8ビットへ
    range = range >> 1
    # データの合成
    move = do << 6
    move |= status << 4
    move |= fab << 3
    move |= ral << 2
    move |= curve
    # マイクロビット2へ送信（ヘッダ+データ2バイト）
    uart_move = chr(move)
    uart_push = chr(range)
    radio.send('b' + uart_move + uart_push)


# 左のジョイスティック(いつもの前後左右斜め8方向動作)なかは右とあまり変わらないため各自で解読して
def left_joy():
    pin2.write_digital(0)
    data_hig = pin1.read_analog()
    data_wid = pin0.read_analog()

    if(data_hig < 510):
        fab = 1
    else:
        fab = 0

    if(data_wid < 511):
        ral = 1
    else:
        ral = 0

    data_hig -= 510
    data_wid -= 511

    data_hig = abs(data_hig)
    data_wid = abs(data_wid)

    if(data_hig < 10 and data_wid < 10):
        do = 0
    else:
        do = 1

    if(data_hig > data_wid):
        status = 0
        difference = data_hig - data_wid
    else:
        status = 1
        difference = data_wid - data_hig

    range = int(math.sqrt(data_hig**2+data_wid**2))

    if(difference < (range >> 2)):
        status = 2

    range = range >> 1

    if(range > 255):
        range = 255

    move = do << 6
    move |= status << 4
    move |= fab << 3
    move |= ral << 2

    uart_move = chr(move)
    uart_push = chr(range)
    radio.send('a' + uart_move + uart_push)


show = 3
message = 2
# ここがメインのプログラム
while True:
    left_joy()
    rite_joy()

    if radio.receive():
        read = radio.receive()
        read = str(read)
        display.show(read)
    # ボタンを押すと特殊コマンドが送信される（スピードMax値の切り替え）
    if button_a.was_pressed():
        radio.send('!' + '!' + '!')
        show += 1
    if button_b.was_pressed():
        radio.send('#' + '#' + '#')
        show -= 1
