#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
學號: N97141459
作業: Lab 4-3
功能: 透過 UART 串列埠互相傳輸數字或字元（支援自己迴圈傳輸或雙機互傳），
      並將接收到的數字或字元顯示於 LED（依據接收到的數字閃爍對應次數，或依字元開關 LED）。
"""

import time
import serial
import RPi.GPIO as GPIO

# ==================== 硬體腳位與通訊設定 ====================
# LED 腳位設定 (使用 BCM 編號，GPIO 17 對應實體腳位 Pin 11)
LED_PIN = 17

# 設定 UART 連接埠與參數 (預設使用 /dev/serial0)
# 對應樹莓派 GPIO 14 (TXD, Pin 8) 與 GPIO 15 (RXD, Pin 10)
SERIAL_PORT = '/dev/serial0'
BAUDRATE = 9600
TIMEOUT = 1

# 初始化 GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# 初始化 Serial 物件
ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    timeout=TIMEOUT
)


# ==================== 通訊與 LED 控制函式 ====================
def send_data(data):
    """傳送字串資料 (自動加上換行符)"""
    if ser.is_open:
        payload = f"{data}\n"
        ser.write(payload.encode('utf-8'))
        print(f"已傳送 : {data}")


def receive_data():
    """接收字串資料並去除首尾空白與換行"""
    if ser.is_open:
        incoming = ser.readline().decode('utf-8', errors='ignore').strip()
        if incoming:
            print(f"收到資料 : {incoming}")
        return incoming
    return ""


def display_on_led(message):
    """
    根據接收到的資料控制 LED：
    1. 若為整數 1~9：LED 閃爍對應次數
    2. 若為 '0' 或 'OFF'：熄滅 LED
    3. 若為 'ON'：點亮 LED
    4. 其餘字元：LED 快速閃爍 1 次表示收到訊號
    """
    if not message:
        return

    # 情況 1: 判斷是否為數字
    if message.isdigit():
        count = int(message)
        if count == 0:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("-> LED 狀態: 保持熄滅")
        else:
            print(f"-> LED 動作: 閃爍 {count} 次")
            for i in range(count):
                GPIO.output(LED_PIN, GPIO.HIGH)
                time.sleep(0.3)
                GPIO.output(LED_PIN, GPIO.LOW)
                time.sleep(0.3)

    # 情況 2: 收到特定控制字元
    elif message.upper() in ["ON", "HIGH", "H"]:
        GPIO.output(LED_PIN, GPIO.HIGH)
        print("-> LED 狀態: 點亮")
    elif message.upper() in ["OFF", "LOW", "L"]:
        GPIO.output(LED_PIN, GPIO.LOW)
        print("-> LED 狀態: 熄滅")

    # 情況 3: 其他字元，快閃 1 次提示
    else:
        print(f"-> 收到字元 [{message}]，LED 提示快閃 1 次")
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(LED_PIN, GPIO.LOW)


# ==================== 主程式 ====================
def main():
    print("=" * 50)
    print("Lab 4-3 UART 傳輸與 LED 顯示程式啟動")
    print(f"串列埠: {SERIAL_PORT}, 波特率: {BAUDRATE}")
    print(f"LED 接腳: GPIO {LED_PIN} (BCM)")
    print("接線說明:")
    print("  1. 自己傳給自己測試 (Loopback): 將 Pin 8 (TXD) 與 Pin 10 (RXD) 用杜邦線對接")
    print("  2. 雙機互傳: A機 TXD 接 B機 RXD、A機 RXD 接 B機 TXD、兩機 GND 共地")
    print("按 Ctrl+C 可停止程式")
    print("=" * 50)

    # 測試傳輸序列 (數字 1~5 依序示範)
    test_sequence = ["1", "2", "3", "ON", "OFF", "5"]
    seq_index = 0

    try:
        while True:
            # 依序取出欲傳送的資料 (數字或字元)
            msg_to_send = test_sequence[seq_index]
            seq_index = (seq_index + 1) % len(test_sequence)

            # 傳送資料
            send_data(msg_to_send)
            time.sleep(0.5)

            # 接收資料
            received = receive_data()

            # 將接收到的資料呈現於 LED
            if received:
                display_on_led(received)

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n使用者中斷程式 (Ctrl+C)")

    finally:
        # 清理並關閉資源
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("GPIO 已清理")

        if ser.is_open:
            ser.close()
            print("串列埠已關閉")

        print("程式結束。")


if __name__ == "__main__":
    main()
