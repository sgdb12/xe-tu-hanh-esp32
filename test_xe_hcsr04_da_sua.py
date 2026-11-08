from machine import Pin, PWM, time_pulse_us
from time import sleep_ms, sleep_us

# =========================================
# XE TU HANH ESP32-S3 N16R8
# TEST MOTOR + SERVO + HC-SR04  (BAN DA SUA)
# =========================================
# LUU Y PHAN CUNG:
#  - HC-SR04 ban thuong can VCC = 5V (cap 3.3V thuong do loi / khong co xung).
#  - Chan ECHO ra 5V -> PHAI qua cau phan ap truoc khi vao GPIO9:
#        ECHO --[1k]--+--> GPIO9
#                     |
#                   [2k]
#                     |
#                    GND        (5V * 2/3 = 3.3V)
#  - GND cua HC-SR04, ESP32-S3, L298N, servo phai NOI CHUNG.
#  - Servo MG995/996 nen cap nguon rieng (LM2596), khong lay chung 5V
#    voi HC-SR04, neu khong servo/motor keo sut ap lam cam bien do loi.

# ===== 1. KHAI BAO MOTOR =====
A = Pin(4, Pin.OUT, value=0)
B = Pin(5, Pin.OUT, value=0)
C = Pin(6, Pin.OUT, value=0)
D = Pin(7, Pin.OUT, value=0)

# ===== 2. KHAI BAO HC-SR04 =====
TRIG = Pin(8, Pin.OUT, value=0)
# PULL_DOWN: neu day ECHO long/hong, chan khong bi tha noi doc so ngau nhien
ECHO = Pin(9, Pin.IN, Pin.PULL_DOWN)

# ===== 3. KHAI BAO SERVO =====
servo = PWM(Pin(10), freq=50, duty_u16=0)

# ===== 4. CAU HINH =====
# HC-SR04 chi do tin cay tu ~2 cm tro len, nen nguong phai > 2 cm.
# (Ban cu dat 1.0 cm nhung lai loai bo moi gia tri < 2 cm
#  -> dieu kien kc < 1 KHONG BAO GIO dung -> banh khong bao gio chay.)
NGUONG_CHAY_CM = 10.0

KC_MIN_CM = 2.0
KC_MAX_CM = 400.0
TIMEOUT_US = 30000          # ~5 m, du cho 400 cm

SERVO_TRAI = 1200
SERVO_GIUA = 1500
SERVO_PHAI = 1800

DAO_TRAI = False
DAO_PHAI = False

trang_thai = "DUNG"

# =========================================
# 5. DIEU KHIEN MOTOR
# =========================================

def dung():
    global trang_thai
    A.value(0)
    B.value(0)
    C.value(0)
    D.value(0)
    if trang_thai != "DUNG":
        print(">>> XE DUNG")
    trang_thai = "DUNG"


def tien():
    global trang_thai
    if trang_thai == "TIEN":
        return

    dung()
    sleep_ms(100)

    if DAO_TRAI:
        A.value(0); B.value(1)
    else:
        A.value(1); B.value(0)

    if DAO_PHAI:
        C.value(0); D.value(1)
    else:
        C.value(1); D.value(0)

    trang_thai = "TIEN"
    print(">>> HAI BANH CHAY TIEN")

# =========================================
# 6. DIEU KHIEN SERVO
# =========================================

def quay_servo(xung_us):
    servo.duty_ns(xung_us * 1000)
    sleep_ms(700)


def test_servo():
    print("\n===== TEST SERVO =====")
    dung()
    for ten, x in (("GIUA", SERVO_GIUA), ("TRAI", SERVO_TRAI),
                   ("GIUA", SERVO_GIUA), ("PHAI", SERVO_PHAI),
                   ("GIUA", SERVO_GIUA)):
        print("QUAY", ten)
        quay_servo(x)
    print("===== SERVO TEST XONG =====")

# =========================================
# 7. DO KHOANG CACH
# =========================================
# Ma trang thai tra ve (de biet chinh xac loi o dau):
#   "OK"        : do duoc, kc hop le
#   "QUA_GAN"   : co xung nhung < 2 cm (vat qua sat) -> KHONG phai loi cam bien
#   "QUA_XA"    : > 400 cm
#   "KHONG_ECHO": time_pulse_us = -2 -> ECHO khong bao gio len muc 1
#                 => kiem tra day, nguon 5V, GND chung, cau phan ap, chan TRIG/ECHO
#   "ECHO_KET"  : time_pulse_us = -1 -> ECHO len 1 nhung qua lau khong xuong
#                 => khong co vat phan xa / mat cam bien chui vao vat mem / nhieu nguon

def do_mot_lan():
    TRIG.value(0)
    sleep_us(5)
    TRIG.value(1)
    sleep_us(10)
    TRIG.value(0)

    t = time_pulse_us(ECHO, 1, TIMEOUT_US)

    if t == -2:
        return None, "KHONG_ECHO", t
    if t < 0:
        return None, "ECHO_KET", t

    kc = t * 0.0343 / 2

    if kc < KC_MIN_CM:
        return kc, "QUA_GAN", t
    if kc > KC_MAX_CM:
        return None, "QUA_XA", t
    return kc, "OK", t


def do_on_dinh(so_lan=3):
    """Do nhieu lan, lay trung vi cac lan OK. Tra ve (kc, trang_thai, chi_tiet)."""
    ds = []
    so_qua_gan = 0
    chi_tiet = []

    for _ in range(so_lan):
        kc, tt, xung = do_mot_lan()
        chi_tiet.append("%s(%d)" % (tt, xung))
        if tt == "OK":
            ds.append(kc)
        elif tt == "QUA_GAN":
            so_qua_gan += 1
        sleep_ms(70)             # HC-SR04 can >= 60 ms giua 2 lan do

    if len(ds) >= 2:
        ds.sort()
        return ds[len(ds) // 2], "OK", chi_tiet

    if so_qua_gan >= 2:
        return 0.0, "QUA_GAN", chi_tiet

    return None, "LOI", chi_tiet

# =========================================
# 8. CHUONG TRINH CHINH
# =========================================

try:
    dung()
    print("==============================")
    print("TEST TOAN BO XE ESP32-S3")
    print("==============================")
    print("Nang hai banh khoi mat dat")
    print("Nguong chay: <", NGUONG_CHAY_CM, "cm")
    input("Nhan Enter de bat dau: ")

    test_servo()
    # Tat xung servo khi do de giam nhieu (servo giu goc nho ma sat banh rang)
    servo.duty_u16(0)

    print("\n===== BAT DAU DO KHOANG CACH =====")
    lan = 0

    while True:
        lan += 1
        kc, tt, chi_tiet = do_on_dinh()

        if tt == "OK":
            print("LAN %d | KHOANG CACH: %.1f cm" % (lan, kc))
            if kc < NGUONG_CHAY_CM:
                tien()
            else:
                dung()

        elif tt == "QUA_GAN":
            print("LAN %d | VAT QUA GAN (< 2 cm)" % lan)
            tien()               # vat sat cam bien cung tinh la "gan"

        else:
            dung()
            print("LAN %d | LOI CAM BIEN | %s" % (lan, " ".join(chi_tiet)))

        sleep_ms(150)

except KeyboardInterrupt:
    print("\nDA DUNG CHUONG TRINH")

except Exception as e:
    print("LOI:", e)

finally:
    dung()
    TRIG.value(0)
    servo.deinit()
    print("DA DUNG TOAN BO XE")
