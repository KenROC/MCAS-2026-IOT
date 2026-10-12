#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
學號: N97141459
作業: Lab 4-1
功能: 驅動 DHT11 溫濕度感測器，並持續讀取且在終端機輸出環境溫度與濕度
"""

import time
import board
import adafruit_dht

def main():
    # 初始化 DHT11 感測器，使用 GPIO4 (對應實體接腳 Pin 7)
    dht_device = adafruit_dht.DHT11(board.D4)
    print("Lab 4-1 DHT11 溫濕度感測器測試啟動 (按 Ctrl+C 可結束程式)...")

    try:
        while True:
            try:
                # 讀取攝氏溫度與濕度
                temperature_c = dht_device.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                humidity = dht_device.humidity

                # 按照投影片要求輸出格式：標明溫度 (C / F) 與濕度 (%)
                print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))

            except RuntimeError as err:
                # DHT 感測器可能偶爾發生讀取或校驗錯誤，此處捕捉並印出錯誤訊息，繼續下一輪讀取
                print(err.args[0])

            # DHT11 建議讀取間隔至少 2 秒
            time.sleep(2.0)

    except KeyboardInterrupt:
        print("\n使用者中斷程式。")

    finally:
        # 釋放感測器與 GPIO 資源
        dht_device.exit()
        print("DHT 感測器連線已關閉，程式結束。")

if __name__ == "__main__":
    main()
