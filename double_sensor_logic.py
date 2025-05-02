"""
    Double Sensor Logic
    ~~~~~~~~~~~~~~~~~~~

- The two sensors will be mounted on the same plane and facing perpendicular to the entry/exit path
of the store and make use of a two-step sequence to accurately count the people that enter and leave the store 

- There are two distance points from the sensors that are important to measure in order to create the traffic 
distance threshold (TDT): the two distances from the sensor that make up the perimiter of the pathway (aka the two 
ends of the doorframe's frame). For someone/something to enter or leave the store they would have to be within 
the TDT

- A baseline_distance value is necessary to determine whether an object has walked into the sensor's line of 
sight. This value is the distance measured by the sensor without any obstruction in front of it--just the normal
store laytout (furniture, decor, etc.)

- Two-Step Logic Sequence
	- 1. determine the direction of the object in motion by noting which sensor is "activated" (breaks the 
    baseline distance) first 
	- 2. determine if the object has entered or left based on their movement in the TDT
		- The reason for this logic is due to the space between the doorway and the sensors in which people 
        can stand in. If someone steps in this area and steps out of it, then the sensor could mark them as 
        an entry/exit, when in reality they haven't exited the store. The "hotzone" defined by the TDT  
        allows for the sensors to combine both a clear activation zone and a direction of movement to accurately 
        determine whether someone has entered or exited the store.

- Entry:
    If the sensor closest to the door, entry_sensor, detects an object within the TDT, 
    and then second sensor detects one, then it can be assumed that a person has walked into the store. 

- Exit:
    If the sensor furthest from the door, exit_sensor, detects an object within the TDT before the entry_sensor 
    detects one, then it can be assumed that a person is walking out of the store.

Note: it's important to realize that the sensor will only make a decision when the object has left the TDT.

- The reset time after detecting movement will have to be tested after deployment, so a group of people can
be accurately counted.
    - If it resets too soon, then someone's second leg could be counted as a second person, but if too late, 
    then the person walking behind them might not be counted as an entry.

- A CSV will keep track of the entries and exits and the time they happened by adding a new row with a 1 on 
the 'entry' or 'exit' column--depending on the walking direction determined by the meter. The CSV will be 
created at the start of the day (12:00am) and saved either at the end of the day (11:59pm) or at a specified 
time by the client. The CSV will be emailed to the client, as requested, once it's ready.
They will be used to store daily foot traffic data that can then be analyzed through a local database.

"""

import time, csv, os, json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import board, busio, digitalio
from adafruit_vl53l0x import VL53L0X 
import argparse
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv

# Set up debug functions
DEBUG = False
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug output'
    )
    return parser.parse_args()

def debug_print(*args, **kwargs):
    # Print only when DEBUG is True
    if DEBUG:
        print(*args, **kwargs)

# Path to JSON config (assuming default dir)
config_file = os.path.join(os.path.dirname(__file__), 'sensor_config.json')

def load_config():
    """
        Loading JSON Config file (sensor_config.json)
    """
    with open(config_file, 'r') as f:
        return json.load(f)
    
def save_config(cfg):
    with open(config_file, 'w') as f:
        json.dump(cfg, f, indent=2)

def prompt_config_values(cfg, key, cast_fn):
    """
        Prompting Users to Configure Parameters (if they'd like)
    """
    default = cfg[key]
    user_reply = input(f'Current {key} value is {default}. Would you like to change this? (y/n)\n').strip().lower()
    while user_reply not in ['y', 'yes', 'n', 'no']:
        user_reply = input('Please enter y or n. Press Ctrl+C to exit.\n').strip().lower()
    if user_reply in ['y', 'yes']:
        user_input = input(f'Enter new value for {key}: ').strip()
        cfg[key] = cast_fn(user_input)
    elif user_reply in ['n', 'no']:
        print(f'Keeping {default} value for {key}.')

def real_time_config(cfg):
    """
        Configuring Non-Calibration Settings Through prompt_config_values
    """
    # Settings below don't require calibration
    prompt_config_values(cfg, 'entry_sensor_address', str)
    prompt_config_values(cfg, 'exit_sensor_address', str)
    prompt_config_values(cfg, 'poll_interval', float)
    prompt_config_values(cfg, 'event_timeout', float)
    prompt_config_values(cfg, 'reset_time', float)
    prompt_config_values(cfg, 'logs_dir', str)
    prompt_config_values(cfg, 'file_name_format', str)
    save_config(cfg)
    print('Settings saved.')

def set_tdt_values(entry_sensor, exit_sensor):
    """
        Calibrating TDT values
        ~~~~~~~~~~~~~~~~~~~~~~

    - The traffic distance threshold is the range of distances that make up the area where people walk 
    in and out of the store from; in order words, the entry/exit pathway.
    """
    print('Sensors are about to calibrate their TDT values. Please clear any obstructions from the sensor\'s line of sight.')
    print('Once started, the min_tdt value will be created first. Please place an obstruction at the edge of the entry pathway closest to the sensors (aka minimum traffic distance threshold).')
    while True:
        ready = input('Press Enter to start.')
        if ready == '':
            break
    
    # Random values just to start the calibration sequence
    min_tdt = 8000
    max_tdt = 8000
    
    # Calibrating min TDT 
    start_time = datetime.now()
    stop_time = start_time + timedelta(seconds=3)
    try:
        # Min TDT calibration loop stopping in 3 seconds
        while datetime.now() < stop_time:
            entry_sensor_reading = entry_sensor.range
            exit_sensor_reading = exit_sensor.range
            print(f'Entry sensor reading: {entry_sensor_reading}mm\nExit sensor reading: {exit_sensor_reading}mm', flush=True)
            if entry_sensor_reading < min_tdt:
                min_tdt = entry_sensor_reading
            if exit_sensor_reading < min_tdt:
                min_tdt = exit_sensor_reading
            time.sleep(0.01) # calibration poll interval in seconds
    except KeyboardInterrupt:
        print('Calibration interrupted by user.')
    
    print('Now the max_tdt value will be calibrated. Please place an obstruction at the edge of the entry pathway furthest from the sensors (aka maximum traffic distance threshold).')
    while True:
        ready = input('Press Enter to start.')
        if ready == '':
            break
    
    # Calibrating max TDT 
    start_time = datetime.now()
    stop_time = start_time + timedelta(seconds=3)
    try:
        # Max TDT calibration loop stopping in 3 seconds
        while datetime.now() < stop_time:
            entry_sensor_reading = entry_sensor.range
            exit_sensor_reading = exit_sensor.range
            print(f'Entry sensor reading: {entry_sensor_reading}mm\nExit sensor reading: {exit_sensor_reading}mm', flush=True)
            if entry_sensor_reading < max_tdt:
                max_tdt = entry_sensor_reading
            if exit_sensor_reading < max_tdt:
                max_tdt = exit_sensor_reading
            time.sleep(0.01) # calibration poll interval in seconds
    except KeyboardInterrupt:
        print('Calibration interrupted by user.')

    print(f'\tTDT range:\nmin = {min_tdt}mm\nmax = {max_tdt}mm') 
    
    return min_tdt, max_tdt

def set_baseline_values(entry_sensor, exit_sensor):
    """
        Calibrating Sensor Baselines
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    - Due to the variation in ToF distance measurements, the baseline distance cannot be a set value.
    The distance might vary by +/- 20mm (in most extreme cases) despite the sensor or the target being static.
    To get the most accurate baseline, and subsequent trigger event, a calibration must take place where the
    sensor keeps track of the lowest measured distance in the span of 3 seconds with a poll interval of 
    .01 seconds for each sensor.
    """
    print('Sensors are about to calibrate their baselines. Please clear any obstructions from the sensor\'s line of sight.')
    while True:
        ready = input('Press Enter to start.')
        if ready == '':
            break
    
    # Initialize baselines
    entry_sensor_baseline = entry_sensor.range
    exit_sensor_baseline = exit_sensor.range

    # Calibrating entry sensor baseline
    start_time = datetime.now()
    stop_time = start_time + timedelta(seconds=3)
    try:
        # Entry sensor calibration loop stopping in 3 seconds
        while datetime.now() < stop_time:
            # Entry sensor calibration
            entry_sensor_reading = entry_sensor.range
            print(f'Entry sensor reading: {entry_sensor_reading}mm', flush=True)
            if entry_sensor_reading < entry_sensor_baseline:
                entry_sensor_baseline = entry_sensor_reading
            time.sleep(0.01) # calibration poll interval in seconds
    except KeyboardInterrupt:
        print('Calibration interrupted by user.')

    # Calibrating exit sensor baseline
    start_time = datetime.now()
    stop_time = start_time + timedelta(seconds=3) 
    try:
        # Exit sensor calibration loop stopping in 3 seconds
        while datetime.now() < stop_time:
            # Exit sensor calibartion
            exit_sensor_reading = exit_sensor.range
            print(f'Exit sensor reading: {exit_sensor_reading}mm', flush=True)
            if exit_sensor_reading < exit_sensor_baseline:
                exit_sensor_baseline = exit_sensor_reading
            time.sleep(0.01) # calibration poll interval in seconds
    except KeyboardInterrupt:
        print('Calibration interrupted by user.')

    print(f'\tBaseline distances:\nEntrySensor = {entry_sensor_baseline}mm\nExitSensor = {exit_sensor_baseline}mm')
    return entry_sensor_baseline, exit_sensor_baseline

# Load env vars
load_dotenv()
def send_email(daily_log_path):
    # Load email credentials from environment
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    username = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    to_address = os.getenv('EMAIL_TO', username)
    from_address = os.getenv('EMAIL_FROM', username)
    if not all((smtp_server, username, password, to_address)):
        print('Email credentials not fully set, skipping email.')
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = f'Foot Traffic Log for {datetime.now():%Y-%m-%d}'
        msg['From'] = from_address
        msg['To'] = to_address
        msg.set_content('Attached is the foot traffic CSV for the previous day.')

        with open(daily_log_path, 'rb') as f:
            data = f.read()
        msg.add_attachment(data,
                           maintype='text',
                           subtype='csv',
                           filename=os.path.basename(daily_log_path))

        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        print(f'Email sent: {os.path.basename(daily_log_path)}')
    except Exception as e:
        print(f'Error sending email: {e}')

def main():
    # Check if in DEBUG mode
    global DEBUG
    args = parse_args()
    DEBUG = args.debug
    debug_print('Launched in debug mode.')

    # Set timezone
    ny_tz = ZoneInfo('America/New_York')  # we want to specify eastern time for data logging

    # Load parameters from config file and prompt user to change any if needed
    cfg = load_config()
    real_time_config(cfg)

    # Reload config file and load parameters in case user changed any
    cfg = load_config()
    poll_interval          = cfg['poll_interval']
    event_timeout          = cfg['event_timeout']
    reset_time             = cfg['reset_time']
    entry_sensor_address   = cfg['entry_sensor_address']
    exit_sensor_address    = cfg['exit_sensor_address']
    logs_dir               = cfg['logs_dir']
    file_name_format       = cfg['file_name_format']

    # Initialize sensors SXHUT pins
    sh1 = digitalio.DigitalInOut(board.D4)
    sh2 = digitalio.DigitalInOut(board.D5)
    sh1.direction = sh2.direction = digitalio.Direction.OUTPUT

    # Turn both XSHUT pins off
    sh1.value = False
    sh2.value = False
    time.sleep(0.1) # 100ms delay allows for pin firmware to catch up

    
    # Boot up sensor 1, entry sensor, set to address specified
    sh1.value = True
    time.sleep(0.1)
    # Initializing I2C Bus
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    entry_sensor = VL53L0X(i2c_bus)
    entry_sensor.set_address(entry_sensor_address)
    print(f'Entry sensor now at address {entry_sensor_address}')

    # Boot up sensor 2, exit sensor, set to address specified
    sh2.value = True
    time.sleep(0.1)
    exit_sensor = VL53L0X(i2c_bus)
    exit_sensor.set_address(exit_sensor_address)
    print(f'Exit sensor now at address {exit_sensor_address}')

    # Optional sensor calibration for baselines and TDT values
    print(
        f'''
            Current sensor values:
            min_tdt = {cfg['min_tdt']}
            max_tdt = {cfg['max_tdt']}
            entry_sensor_baseline = {cfg['entry_sensor_baseline']}
            exit_sensor_baseline = {cfg['exit_sensor_baseline']}
        '''
    )
    user_reply = input(f'Would you like to calibrate the sensors? (y/n)\n').strip().lower()
    while user_reply not in ['y', 'yes', 'n', 'no']:
        user_reply = input('Please enter y or n. Press Ctrl+C to exit.\n').strip().lower()
    if user_reply in ['y', 'yes']:
        min_tdt, max_tdt = set_tdt_values(entry_sensor=entry_sensor, exit_sensor=exit_sensor)
        entry_sensor_baseline, exit_sensor_baseline = set_baseline_values(entry_sensor=entry_sensor, exit_sensor=exit_sensor)
        
        # update config json
        cfg['min_tdt'] = min_tdt
        cfg['max_tdt'] = max_tdt
        cfg['entry_sensor_baseline'] = entry_sensor_baseline
        cfg['exit_sensor_baseline'] = exit_sensor_baseline
        save_config(cfg)
        cfg = load_config()
        print('Sensors calibrated.')

    elif user_reply in ['n', 'no']:
        print('Sensor calibration skipped.')

    # Load TDT and baseline values from config file
    min_tdt = cfg['min_tdt']
    max_tdt = cfg['max_tdt']
    entry_sensor_baseline = cfg['entry_sensor_baseline']
    exit_sensor_baseline = cfg['exit_sensor_baseline']

    # Initialize state
    state = 'idle'
    date_bookmark = datetime.now(ny_tz).strftime('%B_%d_%Y')
    # Create logs directory if it doesn't already exist
    os.makedirs(logs_dir, exist_ok=True)

    print('Starting trafficmeter. Press Ctrl+C to stop.')

    """
        Main Loop
    """
    try:
        while True:
            # Detecting day rollover
            current_date = datetime.now(ny_tz).strftime('%B_%d_%Y') # ex: April_30_2025 in unified Eastern Time
            # If in a new day, then email the daily logs
            if current_date != date_bookmark:
                # Email yesterday's log
                send_email(daily_log_path)
            # Check if the daily log already exists, if not, create one with headers
            file_name = file_name_format.format(date=current_date)
            daily_log_path = os.path.join(logs_dir, file_name)
            file_exists = os.path.isfile(daily_log_path)
            # Create new log if it doesn't already exist
            if not file_exists:
                csv_writer = csv.writer(daily_log_file)
                with open(daily_log_path, 'a', newline='') as daily_log_file:
                    csv_writer.writerow(['date', 'time', 'entry_count', 'exit_count'])

            # Initialize sensor readings            
            entry_sensor_reading = entry_sensor.range
            debug_print('Entry reading: ', entry_sensor_reading)
            exit_sensor_reading = exit_sensor.range
            debug_print('Exit reading: ', exit_sensor_reading)

            # Get current time
            current_time = datetime.now().strftime('%H:%M:%S')

            # Determines which sensor was activated first
            if state == 'idle':
                if (min_tdt <= entry_sensor_reading <= max_tdt):
                    state = 'maybe_entry'
                    debug_print('Entered "maybe_entry" state. entry_sensor_reading: ', entry_sensor_reading, ' at ', current_time)
                    timeout_time = datetime.now() + timedelta(seconds=event_timeout)
                    debug_print('Time out time is ', timeout_time)
                elif (min_tdt <= exit_sensor_reading <= max_tdt):
                    state = 'maybe_exit'
                    debug_print('Entered "maybe_exit" state. entry_sensor_reading: ', exit_sensor_reading, ' at ', current_time)
                    timeout_time = datetime.now() + timedelta(seconds=event_timeout)
                    debug_print('Time out time is ', timeout_time)

            if state == 'maybe_entry':
                while state == 'maybe_entry': 
                    # if someone has entered, poll sensors until they walk thru the second sensor
                    entry_sensor_reading = entry_sensor.range
                    exit_sensor_reading = exit_sensor.range
                    # if they walk thru the second sensor, then we're sure they've entered the store
                    if (min_tdt <= exit_sensor_reading <= max_tdt):
                        debug_print('In maybe_entry state, exit_sensor detected something in TDT reading: ', exit_sensor_reading)
                        with open(daily_log_path, 'a', newline='') as daily_log_file:
                            csv_writer = csv.writer(daily_log_file)
                            csv_writer.writerow([current_date, current_time, 1, 0])
                        print('Entry detected.')
                        time.sleep(reset_time)
                        state = 'idle'

                    # if the sensors timedout and there's nothing in front of them, then reset to idle
                    if (datetime.now() >= timeout_time):
                        debug_print('Time is ', datetime.now())
                        if entry_sensor_reading > max_tdt and exit_sensor_reading > max_tdt:
                            # they've changed their minds and walked out
                            debug_print('Event timed out.')
                            state = 'idle'

            elif state == 'maybe_exit':
                while state == 'maybe_exit':
                    # if someone is exiting, poll sensors until they walk thru the entry sensor
                    entry_sensor_reading = entry_sensor.range
                    exit_sensor_reading = exit_sensor.range
                    # if they walk thru the entry sensor, then we're sure they've walked out the store
                    if (min_tdt <= entry_sensor_reading <= max_tdt):
                        debug_print('In maybe_exit state, entry_sensor detected something in TDT reading: ', entry_sensor_reading)
                        with open(daily_log_path, 'a', newline='') as daily_log_file:
                            csv_writer = csv.writer(daily_log_file)
                            csv_writer.writerow([current_date, current_time, 0, 1])
                        print('Exit detected.')
                        time.sleep(reset_time)
                        state = 'idle'

                    # if the sensors timedout and there's nothing in front of them, then reset to idle
                    if (datetime.now() >= timeout_time):
                        debug_print('Time is ', datetime.now())
                        if entry_sensor_reading > max_tdt and exit_sensor_reading > max_tdt:
                            # they've changed their minds and walked out
                            debug_print('Event timed out.')
                            state = 'idle'

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print('\nLogger stopped by user')

if __name__ == '__main__':
    main()