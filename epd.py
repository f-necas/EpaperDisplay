import spidev  # SPI library
import time
import RPi.GPIO as GPIO  # GPIO library

# GPIO SETUP
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# GPIO.setup(7,GPIO.IN) #pin 7
# GPIO.add_event_detect(7,GPIO.RISING,callback=shutdown,bouncetime=200)
GPIO.setup(16, GPIO.IN)  # output from display to pi /TC_BUSY (if 0=busy  if 1=ready to receive new commands)
'''
GPIO.setup(12,GPIO.OUT) # /TC_EN (1=disabled 0=enabled)
GPIO.output(12,GPIO.HIGH)
GPIO.output(12,GPIO.LOW) #to enable /TC_EN
time.sleep(0.01) # for setup and initialization of TCON
# button setup
'''
# SPI SETUP
spi = spidev.SpiDev()
spi.open(0, 0)  # device 0 (SPI_CE0_N)
spi.max_speed_hz = 3000000  # bit rate 3Mhz
spi.mode = 0b11  # polarity CPOL=1 CPHA=1
spi.bits_per_word = 8
# Commands
reset_data_pointer = [0x20, 0x0D, 0x00]  # resets data pointer to initial position
update_display = [0x24, 0x01, 0x00]  # updates display
upload_header_command = [0x20, 0x01, 0x00, 0x0F]  # packet size is 16 bytes
upload_image_data_command = [0x20, 0x01, 0x00, 0xFA]  # packet size is 250 bytes
image_header = [0x3A, 0x01, 0xE0, 0x03, 0x20, 0x01, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00]  # 16-byte image header


def send_commands(values_to_write):
    resp = spi.xfer2(values_to_write)
    while (GPIO.input(16) == GPIO.LOW):  # wait for processing
        pass


def upload_image(image_data):
    resp = spi.xfer2(upload_header_command + image_header)
    while (GPIO.input(16) == GPIO.LOW):  # wait for processing
        pass
    for x in range(0, 48000, 250):
        resp = spi.xfer2(upload_image_data_command + image_data[x:x + 250])
        while (GPIO.input(16) == GPIO.LOW):  # wait for processing
            pass


def toIntArrayAndGrayScale(img):
    picdata = [0] * 384000
    c = 0
    for x in range(0, 800):
        for y in range(0, 480):
            rgb, alpha = img[y, x]
            # picdata[c], alpha = img[y, x]
            picdata[c] = 255 if rgb <= 127 else 0
            c += 1

    newPicData = [0] * (len(picdata) / 8)
    row = 30
    s = 1
    for i in range(0, len(picdata), 16):
        newPicData[row - s] = (
                ((picdata[i + 6] << 7) & 0x80) |
                ((picdata[i + 14] << 6) & 0x40) |
                ((picdata[i + 4] << 5) & 0x20) |
                ((picdata[i + 12] << 4) & 0x10) |
                ((picdata[i + 2] << 3) & 0x08) |
                ((picdata[i + 10] << 2) & 0x04) |
                ((picdata[i + 0] << 1) & 0x02) |
                ((picdata[i + 8] << 0) & 0x01))

        newPicData[row + 30 - s] = (
                ((picdata[i + 1] << 7) & 0x80) |
                ((picdata[i + 9] << 6) & 0x40) |
                ((picdata[i + 3] << 5) & 0x20) |
                ((picdata[i + 11] << 4) & 0x10) |
                ((picdata[i + 5] << 3) & 0x08) |
                ((picdata[i + 13] << 2) & 0x04) |
                ((picdata[i + 7] << 1) & 0x02) |
                ((picdata[i + 15] << 0) & 0x01))

        s = s + 1
        if s == 31:
            s = 1
            row = row + 60
    return newPicData


def update_screen(img):
    img = img.convert('LA')
    img = img.load()
    rawBytePixelData = toIntArrayAndGrayScale(img)  # good
    upload_image(rawBytePixelData)
    send_commands(update_display)
