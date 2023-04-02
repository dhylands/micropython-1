# Collision Avoidance Demo for Cytron Maker Pi RP2040 board
# Version 3.0 with startup sounds and NeoPixel feedback

from machine import Pin,PWM
from utime import sleep
import neopixel
import ssd1306
import random
import VL53L0X
from neopixel import NeoPixel
import framebuf

# key parameters
POWER_LEVEL = 30000 # min is 20000 max is 65025
TURN_DISTANCE = 25 # distnce we decide to turn - try 20
REVERSE_TIME = .4 # how long we backup
TURN_TIME = .4 # how long we turn
MAX_DIST = 300

# The Piezo Buzzer is on GP22
buzzer=PWM(Pin(22))

# Motor Pins are A: 8,9 and B: 10,11
RIGHT_FORWARD_PIN = 8
RIGHT_REVERSE_PIN = 9
LEFT_FORWARD_PIN = 11
LEFT_REVERSE_PIN = 10
# our PWM objects
right_forward = PWM(Pin(RIGHT_FORWARD_PIN))
right_reverse = PWM(Pin(RIGHT_REVERSE_PIN))
left_forward = PWM(Pin(LEFT_FORWARD_PIN))
left_reverse = PWM(Pin(LEFT_REVERSE_PIN))

NUMBER_PIXELS = 2
STATE_MACHINE = 0
NEOPIXEL_PIN = 18

# The Neopixels on the Maker Pi RP2040 are the GRB variety, not RGB
strip = strip = NeoPixel(Pin(NEOPIXEL_PIN), NUMBER_PIXELS)

TOF_DATA_PIN = 26
TOF_CLOCK_PIN = 27

sda=machine.Pin(TOF_DATA_PIN) # row one on our standard Pico breadboard
scl=machine.Pin(TOF_CLOCK_PIN) # row two on our standard Pico breadboard
i2c=machine.I2C(1, sda=sda, scl=scl, freq=400000)

WIDTH = 128
HEIGHT = 64
SCK=Pin(2)
SDL=Pin(3)
RES = machine.Pin(4)
DC = machine.Pin(5)
CS = machine.Pin(6)
spi=machine.SPI(0,baudrate=100000,sck=SCK, mosi=SDL)
oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, DC, RES, CS)

# Create a VL53L0X object
tof = VL53L0X.VL53L0X(i2c)

red = (255, 0, 0)
orange = (255, 60, 0) # Gamma corrected from G=128 to be less like yellow
yellow = (255, 150, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (75, 0, 130) # purple?
purple = (75, 0, 130)
violet = (138, 43, 226) # mostly pink
cyan = (0, 255, 255)
lightgreen = (100, 255, 100)
white = (128, 128, 128) # not too bright
pink = (255, 128, 128)
color_names = ('red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'cyan', 'lightgreen', 'white')
num_colors = len(color_names)
colors = (red, orange, yellow, green, blue, indigo, violet, cyan, lightgreen, white, pink)

# 64, 64, framebuf.MONO_VLSB
coderdojo_logo_byte_array = bytearray(
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x04\x00\x00\x02\x00\x00\x80\xc1\xc1\xc0\xc0\xc0'
    b'\xc0\xc0\xc1\x81\x01\x01\x02\x02\x06\x0e\x0c\x1c\x38\xf8\xf8\xf0\xe0\xe0\xc0\x80\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x40\x00\x00\x04\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00'
    b'\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x1f\xff\xff\xff\xff\xff\xff\xfe\xfc\xf8\xe0\xc0\x00\x00\x00\x00\x00'
    b'\x00\x80\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x1f\x38\x10\x10\x10'
    b'\x10\x30\x1f\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xf8\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xf8\xc0\x00'
    b'\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x80\x80\x80\xc0\xe0\xe0\xf0\xf8\xfc\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc'
    b'\x38\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xc0\xe0\xf0\xf8\xfc\xfc\xfe\xfe\xfe\xff\xff\xff\xff'
    b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x3f'
    b'\x00\x03\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf9\xf9\xf9\xf1'
    b'\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x1f\x03\x00'
    b'\x00\x00\x00\x00\x00\x02\x00\x10\x20\x40\x80\x00\x00\x00\x00\x00\x0f\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x3f\x3f\x3f\x2f'
    b'\x00\x3f\x3f\x03\x03\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x3f\x1f\x0f\x03\x01\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x04\x00\x00\x10\x01\x23\x07\x0f\x5f\x3f\x3f\x7f\xff\xff\xff\xff\xff\xff'
    b'\xff\xff\xff\xff\xff\xff\x7f\x7f\x7f\x7f\x3f\x3f\x3f\x1f\x1f\x0f\x0f\x07\x03\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
fbi = framebuf.FrameBuffer(coderdojo_logo_byte_array, 64, 64, framebuf.MONO_VLSB)

def turn_motor_on(pwm):
   pwm.duty_u16(POWER_LEVEL)

def turn_motor_off(pwm):
   pwm.duty_u16(0)

def forward():
    turn_motor_on(right_forward)
    turn_motor_on(left_forward)
    turn_motor_off(right_reverse)
    turn_motor_off(left_reverse)
    strip[0] = green
    strip[1] = green
    strip.write()

def reverse():
    turn_motor_on(right_reverse)
    turn_motor_on(left_reverse)
    turn_motor_off(right_forward)
    turn_motor_off(left_forward)
    strip[0] = purple
    strip[1] = purple
    strip.write()

def turn_right():
    turn_motor_on(right_forward)
    turn_motor_on(left_reverse)
    turn_motor_off(right_reverse)
    turn_motor_off(left_forward)
    strip[0] = red
    strip[1] = red
    strip.write()
    play_turn_right()
    
def turn_left():
    turn_motor_on(right_reverse)
    turn_motor_on(left_forward)
    turn_motor_off(right_forward)
    turn_motor_off(left_reverse)
    strip[0] = blue
    strip[1] = blue
    strip.write()
    play_turn_left()

def stop():
    turn_motor_off(right_forward)
    turn_motor_off(right_reverse)
    turn_motor_off(left_forward)
    turn_motor_off(left_reverse)
    strip[0] = yellow
    strip[1] = yellow
    strip.write()

def sound_off():
    buzzer.duty_u16(0)
    
# play a frequence for a given time and go off
def playnote(frequency, time):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)
    # time.sleep(time)
    sleep(0.1)
    sound_off() # always turn off sound after note
    
def play_no_signal():
    playnote(100, 0.1)

def play_turn():
    playnote(500, .1)
 
def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)
   
def rest(time):
    sound_off()
    sleep(time)
    
def play_startup():
    playnote(600, 0.2)
    rest(0.05)
    playnote(600, 0.2)
    rest(.05)
    playnote(600, 0.2)
    rest(0.1)
    playnote(800, 0.4)
    
def play_no_signal():
    playnote(300, 0.1)

def play_turn_right():
    playnote(500, 0.1)
    
def play_turn_left():
    playnote(700, 0.1)

delay = .05

# time of flight calibration parameters
zero_dist = 65 # distance measure when an object is about 1/2 cm away
max_dist = 350 # max distance we are able to read
scale_factor = .2

# create a list of the ports
#for i in range(number_leds):
#   led_ports.append(machine.Pin(blue_led_pins[i], machine.Pin.OUT))

# Create a VL53L0X object
tof = VL53L0X.VL53L0X(i2c)
tof.start()

# get the normalized time-of-flight distance
def get_distance():
    global zero_dist, scale_factor
    tof_distance = tof.read()
    if tof_distance > max_dist:
        return tof_distance
    # if our current time-of-flight distance is lower than our zero distance then reset the zero distance
    if tof_distance < zero_dist:
        zero_dist = tof_distance
    return  int((tof_distance - zero_dist) * scale_factor)

def led_show_dist(in_distance):
    global number_leds, distance_per_led 
    for led_index in range(0, number_leds):
        val = TURN_DISTANCE + led_index * distance_per_led
        if in_distance > val:
            led_ports[led_index].high()
        else:
            led_ports[led_index].low()

LED_DELAY = .08
def run_lights():
    for i in range(0, number_leds):
        led_ports[i].high()
        strip.set_pixel(0, colors[i])
        strip.set_pixel(1, colors[i])
        strip.show()
        sleep(LED_DELAY)
        led_ports[i].low()
    # blue down
    for i in range(number_leds - 1, 0, -1):
        led_ports[i].high()
        strip.set_pixel(0, colors[i])
        strip.set_pixel(1, colors[i])
        strip.show()
        sleep(LED_DELAY)
        led_ports[i].low()
# start our time-of-flight sensor


def update_splash(distance):
    oled.fill(0)
    oled.blit(fbi, 64, 0)
    oled.text("CoderDojo", 0, 0)
    oled.text("Robots", 0, 10)
    oled.text("Standby", 0, 44)
    if distance < MAX_DIST:
        oled.text("Dist:", 0, 54)
        oled.text(str(distance), 40, 54)
    else:
        oled.text("No Signal", 0, 54)
    oled.show()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

color_cycle = 0
def cycle_neopixels():
    global color_cycle
    for i in range(0, NUMBER_PIXELS):
        # print(wheel(counter))
        strip[i] = wheel(color_cycle)
    strip.write()
    color_cycle += 5
    color_cycle = color_cycle % 255


HALF_HEIGHT = HEIGHT >> 1
QUARTER_HEIGHT = HALF_HEIGHT >> 1
HALF_WIDTH = WIDTH >> 1
QUARTER_WIDTH = HALF_WIDTH >> 1
ONE_THIRD_HEIGHT = int(HEIGHT/3)

# draw readability
ON = 1
OFF = 0
NO_FILL = 0
FILL = 1
phm = 18 # pupal horizontal movement range 
eye_dist_from_top = 21
eyeWidth = 27
eyeHeight = 10
mouth_vpos = 45
mouth_width = 40

x = 0
def update_distance_chart(distance):
    global x
    print(x, distance)
    if distance > 63:
        distance = 63
    oled.pixel(x,HEIGHT - int(distance) - 1, 1)
    if x > WIDTH - 3:
        oled.scroll(-1,0)
    else:
        x += 1
    # oled.text(str(distance),0,53)
    oled.show()
    
def update_distance(i):
    oled.fill(0)

    # left eye
    oled.ellipse(32, eye_dist_from_top, eyeWidth, eyeHeight, ON, FILL)
    oled.ellipse(32+i, eye_dist_from_top, 5, 5, OFF, FILL)

    # right eye
    oled.ellipse(94, eye_dist_from_top, eyeWidth, eyeHeight, ON, FILL)
    oled.ellipse(94+i, eye_dist_from_top, 5, 5, OFF, FILL)

    # draw mouth
    # draw bottom half by doing a bitwise and of 8 and 4
    oled.ellipse(HALF_WIDTH, mouth_vpos, mouth_width, 10, ON, NO_FILL, 12)
    oled.text(str(i),0,53)
    oled.show()

def no_signal_face():
    oled.fill(0)

    # left eye
    oled.ellipse(32, eye_dist_from_top, eyeWidth, eyeHeight, ON, FILL)
    oled.ellipse(32, eye_dist_from_top, 5, 5, OFF, FILL)

    # right eye
    oled.ellipse(94, eye_dist_from_top, eyeWidth, eyeHeight, ON, FILL)
    oled.ellipse(94, eye_dist_from_top, 5, 5, OFF, FILL)

    # draw mouth
    # draw bottom half by doing a bitwise and of 8 and 4
    oled.ellipse(HALF_WIDTH, mouth_vpos, mouth_width, 10, ON, NO_FILL, 12)
    oled.show()

mode = 0
# loop forever
def main():
    global valid_distance, mode
    while True:
        distance = get_distance()
        # standby splash until distance is under 3
        if mode == 0:
            update_distance_chart(distance)
            cycle_neopixels()
            # wave your hand in front of the sensor to start driving
            if distance < 3: mode = 1
        elif mode == 1:
            update_distance(0)
            if distance > MAX_DIST:
                print('no signal')
                no_signal_face()
                # play_no_signal()
            # we have a valid distance
            else:
                # print(distance)
                if distance < TURN_DISTANCE:    
                    # back up for a bit
                    reverse()
                    sleep(REVERSE_TIME)
                    stop()
                    sleep(REVERSE_TIME)
                    
                    # turn in a random direction
                    if random.random() > .5:
                        print('turning right')
                        update_distance(-10)
                        sleep(1)
                        turn_right()
                    else:
                        print('turning left')
                        update_distance(10)
                        sleep(1)
                        turn_left()
                    sleep(TURN_TIME)
                    # continue going forward
                    forward()
                else:
                    # print('forward')
                    forward()
                valid_distance = 1
            #led_show_dist(distance)

#play_startup()
valid_distance = 1

# This allows us to stop the sound by doing a Stop or Control-C which is a keyboard intrrupt
print('Running Collision Avoidence with Time-of-Flight Sensor Version 3.0')

try:
    main()
except KeyboardInterrupt:
    print('Got ctrl-c')
finally:
    # Optional cleanup code
    print('turning off sound')
    sound_off()
    print('turning off motors')
    stop()
    tof.stop()
