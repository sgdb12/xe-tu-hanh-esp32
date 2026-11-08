# Xe tự hành ESP32-S3 – Test motor + servo + HC-SR04

Code MicroPython kiểm tra toàn bộ xe: 2 motor qua L298N, servo MG995/996, cảm biến siêu âm HC-SR04.

## Sơ đồ chân

| Thiết bị | Chân ESP32-S3 |
|---|---|
| L298N IN1–IN4 | GPIO4, 5, 6, 7 |
| HC-SR04 TRIG | GPIO8 |
| HC-SR04 ECHO (qua cầu phân áp 1k/2k) | GPIO9 |
| Servo | GPIO10 |

## Cách chạy

1. Nạp `test_xe_hcsr04_da_sua.py` lên ESP32-S3 (Thonny hoặc mpremote).
2. Nâng hai bánh khỏi mặt đất, nhấn Enter để bắt đầu.
3. Xe test servo, rồi đo khoảng cách liên tục: vật < 10 cm thì bánh quay tiến, xa hơn thì dừng.

## Lưu ý phần cứng

- HC-SR04 cấp 5V; chân ECHO phải qua cầu phân áp xuống 3.3V.
- GND của ESP32, L298N, HC-SR04, servo nối chung.
- Servo nên cấp nguồn riêng (LM2596).
