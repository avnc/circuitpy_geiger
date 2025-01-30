from os import getenv
import board
import time
import countio
import digitalio
import microcontroller
from busio import SPI
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_io.adafruit_io import IO_HTTP
from adafruit_io.adafruit_io import AdafruitIO_RequestError
import adafruit_requests as requests

# Configuration
GEIGER_PIN = board.D3  # GPIO pin connected to the Geiger counter's pulse output
DEBOUNCE_TIME = 0.1  # Debounce time in seconds

# Using a Metro board with pre-defined ESP32 Pins, so gotta do this to get it all setup
esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)

spi = SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(getenv("CIRCUITPY_WIFI_SSID"), getenv("CIRCUITPY_WIFI_PASSWORD"))
    except OSError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)
print("IP address is", esp.pretty_ip(esp.ip_address))

print("connecting to Adafruit IO")
# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(getenv("AIO_USERNAME"), getenv("AIO_KEY"), requests)

# check for feeds (and create if not there)
try:
    # Get the 'radiation' feeds from Adafruit IO
    cpm_feed = io.get_feed("radiation.cpm")
    usv_feed = io.get_feed("radiation.usv-slash-h")
except AdafruitIO_RequestError:
    # If no 'radiation' feeds exists, create
    rad_feed = io.create_new_feed("radiation")
    usv_feed = io.create_new_feed("radiation.usv-slash-h")

# to get to uSv/h
CONVERSION_FACTOR = 151

# initial values
cpm = 0
sleep_time = 60

print("setting up geiger pin")
# Setup pulse counter, this will count the inputs to the our IO pin connected to the Geiger counter
pulse_counter = countio.Counter(GEIGER_PIN, edge=countio.Edge.FALL)

# Function to calculate and display CPM
def calculate_cpm():
    global cpm
    cpm = pulse_counter.count  # Get the current pulse count
    pulse_counter.reset()  # Reset the counter for the next interval

print("starting measurement, first data in 60 seconds")
print("-------------------------")
# Main loop
while True:
    try:
        # Calculate and display CPM every 60 seconds
        time.sleep(sleep_time)
        calculate_cpm()
        
        micro_sv = round(cpm / CONVERSION_FACTOR, 2)
        # reset time and count before we send data as this can take a little time
        start_time = time.monotonic()
        
        print(f"CPM is {cpm}")
        print(f"uSv/h is {micro_sv}")

        # send data to feeds
        io.send_data(cpm_feed["key"], cpm)
        io.send_data(usv_feed["key"], micro_sv)
        
        # calculate how much time sending data took and subtract from the 60 secs
        # this will make our counts per minute value more accurate
        send_time = time.monotonic() - start_time
        print(f"took {send_time}secs to send data")
        if send_time < 60:
            sleep_time = 60 - send_time
        else:
            # if it took us too long to send the data, we'll reset the pulsecounter and then do 60 secs sleep
            pulse_counter.reset()
            sleep_time = 60
        print(f"sleeping another {sleep_time} seconds")
        print("-------------------------")
    except Exception as e:
        # An error occurred, print exception
        print("Error:", e)
        time.sleep(10)

        # Perform a soft reset to restart the CircuitPython script
        microcontroller.reset()        
