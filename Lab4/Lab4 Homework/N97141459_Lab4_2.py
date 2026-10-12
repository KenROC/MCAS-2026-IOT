#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
學號: N97141459
作業: Lab 4-2
功能: 模擬倒車雷達。利用 HC-SR04 超音波感測器測量距離，
      當距離小於 20 cm 時終端機顯示「注意！！！」，否則顯示「沒事」。
"""

import time
import RPi.GPIO as GPIO

# 設定使用 BCM 編號系統
GPIO.setmode(GPIO.BCM)

# 超聲波模組的 TRIG_y 與 ECHO_r 引腳設定
TRIG_y = 23  # GPIO 23 (實體腳位 Pin 16)
ECHO_r = 24  # GPIO 24 (實體腳位 Pin 18)

# 設定引腳輸出入模式
GPIO.setup(TRIG_y, GPIO.OUT)
GPIO.setup(ECHO_r, GPIO.IN)


def measure_distance():
    """測量並回傳超音波距離 (單位: cm)"""
    # 確保發射端是關閉的，並稍作延遲讓感測器穩定
    GPIO.output(TRIG_y, False)
    time.sleep(0.05)

    # 發送 10 微秒的高電位脈衝來觸發超聲波
    GPIO.output(TRIG_y, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_y, False)

    pulse_start = time.time()
    timeout_start = pulse_start
    # 等待 ECHO_r 變為高電位 (1)，並記錄起始時間 (加入 timeout 機制防止卡住)
    while GPIO.input(ECHO_r) == 0:
        pulse_start = time.time()
        if pulse_start - timeout_start > 0.04:  # 超過 40ms 視為逾時
            return None

    pulse_end = pulse_start
    timeout_end = pulse_start
    # 等待 ECHO_r 變回低電位 (0)，並記錄結束時間 (加入 timeout 機制防止卡住)
    while GPIO.input(ECHO_r) == 1:
        pulse_end = time.time()
        if pulse_end - timeout_end > 0.04:  # 超過 40ms 視為逾時
            return None

    # 計算脈衝持續時間，並根據音速轉換為距離（公分）
    # 距離 = (時間 * 聲速 34300 cm/s) / 2
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance


def main():
    try:
        print("程式啟動，按 Ctrl+C 可以停止測試...")

        while True:
            # LAB4-2: 測量距離並判斷狀態
            dist = measure_distance()

            if dist is not None:
                # 按照投影片要求輸出格式：
                # 第一行: 當前感測距離 (目前距離: XX.XX cm)
                # 第二行: 當前狀態 (沒事 或 注意！！！)
                print(f"目前距離: {dist} cm")
                if dist < 20:
                    print("注意！！！")
                else:
                    print("沒事")

            time.sleep(0.5)  # 稍微停一下，避免畫面跳太快

    except KeyboardInterrupt:
        # 按下 Ctrl+C 時執行
        print("\n停止測量中...")

    finally:
        # 清除 GPIO 設定
        GPIO.cleanup()
        print("GPIO 已清理，程式結束。")


if __name__ == "__main__":
    main()
