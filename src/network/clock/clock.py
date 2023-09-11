import ntptime, network
from machine import RTC
from utime import sleep, sleep_ms, time, localtime, mktime
import config

# US Central
timeZone = -6
# try one of these
ntptime.host = 'us.pool.ntp.org' #'time.nist.gov' #'pool.ntp.org'
ntptime.timeout = 10

def wifiConnect():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.config(pm = 0xa11140) # disables wifi sleep mode
    if not wifi.isconnected():
        wifi.connect(config.wifi_ssid, config.wifi_pass)
        print('Connecting..', end='')
        max_wait = 10
        while max_wait > 0:
            if wifi.status() < 0 or wifi.status() >= 3: break
            sleep_ms(1000)
            print('.', end='')
            max_wait -= 1
        print()
        if wifi.status() != 3: print('Could not connect to wifi!')
    # print('Connected: ',wifi.isconnected(),'\nIP: ',wifi.ifconfig()[0])
    sleep_ms(100)
    return wifi

# daylight savings time
def dst():
    year, weekday = localtime()[0], localtime()[6]
    dst_start = mktime((year, 3, (8 - weekday) % 7 + 8, 2, 0, 0, 0, 0))
    dst_end = mktime((year, 11, (1 - weekday) % 7 + 1, 2, 0, 0, 0, 0))
    return dst_start <= time() < dst_end

def setRTC():
    timeset = False
    timetries = 0
    maxtries = 5
    while not timeset and timetries < maxtries:
        timetries += 1
        try:
            ntptime.settime() # update time from ntp server
            timeset = True
        except:
            print(f'NTP update attempt # {timetries} of {maxtries} failed!', 'Retrying in 15 seconds..' if timetries < maxtries else 'Check connection/config.')
            if timetries < maxtries: sleep_ms(15000)
        if timeset:
            sleep_ms(200)
            rtc = RTC()
            tz_offset = (timeZone + 1) * 3600 if dst() else timeZone * 3600
            #tz_offset = timeZone * 3600 # without daylight savings
            myt = localtime(time() + tz_offset)
            rtc.datetime((myt[0], myt[1], myt[2], myt[6], myt[3], myt[4], myt[5], 0))
            sleep_ms(200)
            dtime = rtc.datetime()
            timestr = '%2d:%02d%s' %(12 if dtime[4] == 0 else dtime[4] if dtime[4] < 13 else dtime[4] - 12, dtime[5], 'am' if dtime[4] < 12 else 'pm')
            datestr = f'{dtime[1]}/{dtime[2]}/{dtime[0] % 100}'
            # print('Time set to:', timestr, datestr)
            print(timestr, datestr)
            return True
    print('ERROR! Unable to update time from server!')
    return False

def update():
    success = False
    wifi = wifiConnect()
    sleep_ms(100)
    if wifi.isconnected():
        success = setRTC()
        sleep_ms(100)
    return wifi, success

if __name__ == '__main__':
    while True:
        update()
        sleep(60)
