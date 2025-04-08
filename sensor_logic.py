import time
import csv
from datetime import datetime
import board
import busio
import adafruit_vl53l0x
import os
from zoneinfo import ZoneInfo

"""
    Sensor Logic
    ~~~~~~~~~~~~

- The sensor will be mounted on the door frame (inside the shop) about 2 ft off the ground 
and at an angle, so it's pointing toward the opposite corner of the doorframe. The angled 
sensor should pick up when people walk in or out of the store. Adjust the angle if it's 
having trouble differentiating between entry/exit.

- The people that walk in will appear from "afar" and get closer to the sensor before 
vanishing (walking past the sensor and into the store).

- The people that walk out of the store will suddenly appear in front of the sensor before 
slowly walking away--opposite to those walking in.

- The person walking in will increase the "foot_traffic" count by 1, and the person walking out 
will increase the "person_leaves" count by 1.
    - We will keep track of the number of people that walk out and use it for troubleshooting 
    purposes, and/or data validation.

- Special cases:
    - two people walk in at once, like mother and child
    - inanimate objects, how to differentiate between a wheelchair or slow scooter and 
    two or more people walking in in quick succession

"""

# Baseline distance (with no one in front of the sensor), in milimeters.
# Sensor reads 805mm - 830mm with no obstructions, so we'll go with 800mm
baseline_distance = 1200

# Distance below which an object is considered “detected”
obstruction_size = 200 # distance in mm between the baseline and obstruction
trigger_distance = baseline_distance - obstruction_size

# Distance near baseline to indicate that the object left the sensor’s field
reset_distance = baseline_distance - (obstruction_size/2)

# entry and exit count
foot_traffic = 0
person_leaves = 0


"""
    CSV logging
"""
def get_log_filename():
    # returns a daily log file
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    return f"{today}_foot_traffic_log.csv"

def log_event(foot_traffic, person_leaves):
    # appends a new entry to the daily log
    filename = get_log_filename()
    NY_TZ = ZoneInfo("America/New_York") # we want to specify eastern time for data logging
    current_datetime = datetime.now(NY_TZ)  # This is the unified datetime in Eastern Time.
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")
    # 'a': open for writing, appending to the end of file it it exists
    # newline='': no translation takes place when writing output to stream
    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # If the file doesn't exist, write the header row first
        if not os.path.isfile(filename):
            csv_writer.writerow(['date', 'time', 'foot_traffic', 'person_leaves'])
        csv_writer.writerow([current_date, current_time, foot_traffic, person_leaves])
    print(f"Logged: {current_date} {current_time} | Foot Traffic: {foot_traffic} | Exits: {person_leaves}")


"""
    Sensor interface
"""
# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the sensor
sensor = adafruit_vl53l0x.VL53L0X(i2c)

def read_distance():
    distance = sensor.range
    print("Distance: {} mm".format(distance))
    return distance


"""
    Movement logic
"""
def evaluate_movement(readings):
    """
    - Given a list of (timestamp, distance) tuples collected during a trigger event,
    evaluate the movement pattern.

    - If the baseline reading drops significantly (more than 'obstruction_size')
    and then returns near baseline, we assume an "entry" pattern.
    - Otherwise, it is treated as an "exit."

    - More sophisticated algorithms should use the rate of change and additional time-based slopes.

    """

    # Extract only the distance values from the timestamped readings.
    distances = [round(reading[1]/10) for reading in readings] # dividing by 10 and rounding to turn mm into cm
    approach_count = 0
    departure_count = 0
    
    # Evaluate consecutive differences.
    for i in range(1, len(distances)-1):
        delta = distances[i] - distances[i - 1] # difference between logged distance and the one previously logged
        if delta < 0: # if logged distance is less than the previous distance, then it's approaching
            approach_count += 1
        elif delta > 0: # if logged distance is more than the previous distance, then it's retreating
            departure_count += 1
        print(f'{distances[i]} - {distances[i - 1]} = {delta}. ')
        print(f'approach_count = {approach_count} | departure_count = {departure_count}')

    # Determine whether entry or exit based on movement trend
    if approach_count > departure_count:
        return "entry"
    elif departure_count > approach_count:
        return "exit"
    else:
        return None


"""
    Main loop
"""
def main():
    global foot_traffic, person_leaves

    # The sensor state can be either "idle" (waiting for detection) or "tracking" (collecting data)
    state = "idle"
    readings = []  # This list will hold (timestamp, distance) tuples during an event

    poll_interval = 0.01  # Time between sensor polls (in seconds)

    print("Starting sensor monitoring. Press cmd+z to exit...")
    try:
        while True:
            current_distance = read_distance()
            current_time = time.time()

            if state == "idle":
                # Begin tracking if an object is detected
                if current_distance < trigger_distance:
                    state = "tracking"
                    readings = [(current_time, current_distance)]
                    print("Object detected. Tracking started...")
            
            elif state == "tracking":
                # Keep appending readings while tracking
                readings.append((current_time, current_distance))
                
                # TODO: 
                # 1. if the distance is far and suddenly just to being in front of the sensor we can 
                #   assume a second person has walked in front of the sensor
                # 2. get rid of reset_distance altogether; a properly calibrated baseline_distance
                #   should be enough

                # When the reading returns to near-baseline, assume the object has moved out of view
                if current_distance > reset_distance:
                    direction = evaluate_movement(readings)
                    if direction == "entry":
                        foot_traffic += 1
                        print("Entry detected!")
                    else:
                        person_leaves += 1
                        print("Exit detected!")
                    
                    log_event(foot_traffic, person_leaves)
                    # Reset state for the next event
                    readings = []
                    state = "idle"

                # Timeout: if tracking lasts too long (e.g., more than 5 seconds) without returning to baseline,
                # assume the event is over and reset.
                if readings and (current_time - readings[0][0]) > 5:
                    print("Tracking timeout. Resetting state.")
                    readings = []
                    state = "idle"

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\nSensor monitoring stopped.")

if __name__ == "__main__":
    main()