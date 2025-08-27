import serial
import json
import time

# Update with your Pico’s actual port
SERIAL_PORT = "/dev/tty.usbmodem1401"
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port {SERIAL_PORT}: {e}")
    exit(1)

print("Reading Pico telemetry...\n")

while True:
    try:
        line = ser.readline()
        if not line:
            continue  # no data yet
        line = line.decode("utf-8").strip()
        try:
            data = json.loads(line)
            print(f"Temperature: {data['temperature']:.2f} °C | "
                  f"Accel X:{data['accel']['x']:.2f}, "
                  f"Y:{data['accel']['y']:.2f}, "
                  f"Z:{data['accel']['z']:.2f}")
        except (json.JSONDecodeError, KeyError) as e:
            print("Bad data:", line)
    except UnicodeDecodeError:
        # skip lines that can't be decoded
        continue
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print("Unexpected error:", e)
        break
