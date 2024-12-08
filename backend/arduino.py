import serial
import time
import requests
import os
from datetime import datetime
from pydub import AudioSegment
from pydub.utils import get_encoder_name

from ask_questions import Siri
from states_enum import State
from story_resume import story_resume

# Define the alarm time
ALARM_TIME = "18:44"
PIN_READ_INTERVAL = 1.0  # 500 ms, time interval to read pin
weight_values = []
T = 0
t = 1.3
counter_60_reads = 0


def add_to_list(value):
    weight_values.append(value)
    if len(weight_values) > 10:
        weight_values.pop(0)


def medium():
    sum = 0.0
    for i in range(0, len(weight_values)):
        sum += weight_values[i]
    return sum / 10


def evening(arduino):
    story_resume()
    siri = Siri()
    siri.clean_file("./text/answers.txt")
    siri.run()

    with open("./text/answers.txt", "r") as f:
        question = f.readline()
        answer = f.readline()
        answer = answer.strip().split()[0]
        if answer == "Yes" or answer == "yes" or answer == "Da" or answer == "da" or answer == "oui" or answer == "Oui":
            arduino.write(f"SL{len('./audio/english_story.mp3') * 10}".encode('utf-8'))
            print((f"SL{((int)(len(AudioSegment.from_file('./audio/english_story.mp3')) / 1000))}").encode('utf-8'))
            os.system("start ./audio/english_story.mp3")
        else:
            os.system("python main.py")
            # Play the audio file automatically
            print((f"SL{((int)(len(AudioSegment.from_file('./audio/english_story.mp3')) / 1000))}").encode('utf-8'))
            print("Playing the audio...")
            os.system(f"start ./audio/english_story.mp3")  # For Windows


def calculate_next_state(state, cond_t, cond_T, ALARM, hour, finished_story):
    global counter_60_reads
    if state == State.NOPE:
        if cond_T == 0 and hour >= "20:00":
            return State.NEADORMIT
        return State.NOPE
    if state == State.NEADORMIT:
        if finished_story == 1:
            return State.ADORMIT
        if cond_t == 0:
            return State.NEADORMIT
        if cond_t == 1:
            return State.WAIT30s
    if state == State.WAIT30s:
        if cond_t == 0:
            counter_60_reads = 0
            return State.NEADORMIT
        if cond_t == 1:
            counter_60_reads += 1
            if counter_60_reads == 20:
                return State.ADORMIT
            return State.WAIT30s
    if state == State.ADORMIT:
        if ALARM == False:
            return State.ADORMIT
        if ALARM == True:
            return State.TREZIRE
    if state == State.TREZIRE:
        if cond_T == 0:
            return State.NOPE
        if cond_T == 1:
            return State.TREZIRE


def main():
    stop = False
    story_started = False
    set_hour = "07:00"
    response = requests.get('http://localhost:5000/api/get-hour')
    if response.status_code == 200:
        data = response.json()
        set_hour = data.get("hour")
    alarm_flag = False
    arduino = serial.Serial(port="COM13", baudrate=9600, timeout=1)

    last_pin_read = time.time()
    current_state = State.NOPE
    counter = 0
    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            if current_time == set_hour and stop == False:
                alarm_flag = True
                os.system("python good_morning.py")
            # Read pin value every 500 ms
            if time.time() - last_pin_read >= PIN_READ_INTERVAL:
                last_pin_read = time.time()
                arduino.write(b"CMD:READ_PIN\n")
                # Read the response from Arduino
                if arduino.in_waiting > 0:
                    line = arduino.readline()
                    print(line)
                    data = None
                    try:
                        data = line.decode('utf-8').strip()
                        # data = arduino.readline().decode('utf-8').strip()
                        if data.startswith("RESP:"):
                            print(f"Arduino Response: {data[5:]}")
                        else:
                            counter += 1
                            print(f"Sensor Value: {data}")
                            if counter == 1:
                                T = float(data) / 500.0
                            elif counter > 11:
                                medium_last_10 = medium()
                                print(medium_last_10)
                                cond_T = (abs(medium_last_10 - float(data)) < T)
                                cond_t = (abs(medium_last_10 - float(data)) < t)
                                print(alarm_flag)
                                next_state = calculate_next_state(current_state, cond_t, cond_T, alarm_flag, "21:00", 0)#current time
                                if(alarm_flag == True):
                                    alarm_flag = False
                                    stop = True
                                if next_state != current_state:
                                    arduino.write(f"STATE{next_state.value}\n".encode('utf-8'))
                                    print(f"STATE {next_state.value}")
                                    current_state = next_state
                                    if current_state == State.NEADORMIT and story_started == False:
                                        story_started = True
                                        evening(arduino)
                                    if current_state == State.ADORMIT:
                                        print("ADORMIT INTRU MAICA DOMNULUI")
                                        os.system('taskkill /F /IM "Microsoft.Media.Player.exe" /T')

                                add_to_list(float(data))
                    except Exception:
                        pass
            # time.sleep(0.01)  # Slight delay to reduce CPU usage

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        arduino.close()


if __name__ == "__main__":
    main()
