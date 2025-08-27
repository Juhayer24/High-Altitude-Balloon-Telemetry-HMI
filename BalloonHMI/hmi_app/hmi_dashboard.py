import streamlit as st
import serial
import json
import time
import atexit

# Configure serial
import glob

def find_serial_port():
    # List all potential serial ports
    ports = glob.glob('/dev/tty.usbmodem1401') + glob.glob('/dev/tty.usbmodem1401')
    # Look for Pico's port
    for port in ports:
        if 'usbmodem' in port:
            return port
    return None

SERIAL_PORT = find_serial_port()
BAUD_RATE = 115200

if not SERIAL_PORT:
    st.error("❌ No USB device found! Please check your connection.")
    st.stop()

# Initialize serial connection with error handling
ser = None

def connect_serial():
    global ser
    try:
        if ser is not None:
            ser.close()
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        return True
    except serial.SerialException as e:
        st.error(f"Failed to connect to {SERIAL_PORT}: {str(e)}")
        return False

def cleanup():
    if ser is not None:
        ser.close()

# Register cleanup function
atexit.register(cleanup)

# Try to connect
if not connect_serial():
    st.warning("🔄 Attempting to reconnect every 5 seconds...")

# Streamlit Page Config
st.set_page_config(page_title="Balloon Telemetry HMI", layout="wide")
st.title("🎈 High-Altitude Balloon Telemetry HMI")

# Placeholders
temp_display = st.metric("Temperature (°C)", "0.0")
accel_chart = st.line_chart({"X": [], "Y": [], "Z": []})
event_log = st.empty()

data_buffer = {"X": [], "Y": [], "Z": []}

while True:
    # Check if we need to reconnect
    if ser is None or not ser.is_open:
        if connect_serial():
            st.success("✅ Connected to serial port!")
        else:
            time.sleep(5)  # Wait before retrying
            continue

    try:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue

        data = json.loads(line)

        # Update Temperature
        temp_display.metric("Temperature (°C)", f"{data['temperature']:.2f}")

        # Update Chart
        data_buffer["X"].append(data["accel"]["x"])
        data_buffer["Y"].append(data["accel"]["y"])
        data_buffer["Z"].append(data["accel"]["z"])
        accel_chart.add_rows(data_buffer)

        # Log events
        if abs(data["accel"]["x"]) > 2:  # Example: shake detected
            event_log.write("⚠️ High X acceleration detected!")

    except serial.SerialException as e:
        st.error(f"Serial connection error: {str(e)}")
        ser.close()
        ser = None
        time.sleep(1)
    except json.JSONDecodeError as e:
        st.warning(f"Invalid data received: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
    
    time.sleep(0.5)
