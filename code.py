from os import getenv
import board
import digitalio 
import time
from busio import SPI
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_io.adafruit_io import IO_HTTP
from adafruit_io.adafruit_io import AdafruitIO_RequestError
import adafruit_requests as requests


# Using a Metro board with pre-defined ESP32 Pins, so gotta do this to get it all setup (copied from Adafruit example code)
esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)

spi = SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(getenv('CIRCUITPY_WIFI_SSID'), getenv('CIRCUITPY_WIFI_PASSWORD'))
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(getenv('AIO_USERNAME'), getenv('AIO_KEY'), requests)

# check for feeds (and create if not there)
try:
    # Get the 'radiation' feeds from Adafruit IO
    cpm_feed = io.get_feed("radiation.cpm")
    usv_feed = io.get_feed("radiation.usv-slash-h")
except AdafruitIO_RequestError:
    # If no 'radiation' feeds exists, create
    rad_feed = io.create_new_feed("radiation.cpm")
    usv_feed = io.create_new_feed("radiation.usv-slash-h")

# setup Geiger counter pin
geiger_pin = digitalio.DigitalInOut(board.D3)  # Use the correct pin for your setup
geiger_pin.direction = digitalio.Direction.INPUT
geiger_pin.pull = digitalio.Pull.UP  # If necessary, use a pull-up or pull-down resistor

# to get to uSv/h
conversion_factor = 151
count = 0
previous_state = False

start_time = time.monotonic()

while True:
    current_state = geiger_pin.value
    if current_state and not previous_state:
        # rising edge detected
        count += 1
    previous_state = current_state
    
    # this code here could be better but works for our half-assed implementation
    if time.monotonic() - start_time >= 60:
        # a minute has passed
        cpm = count
        micro_sv = round(count/conversion_factor, 2)
        # reset time and count before we send data as this can take a little time
        start_time = time.monotonic()
        count = 0
        print(f'Counts per minute: {cpm}')
        print(f'uSv/h is {micro_sv}')
        # send data to feeds
        io.send_data(cpm_feed["key"], cpm)
        io.send_data(usv_feed["key"], micro_sv)
