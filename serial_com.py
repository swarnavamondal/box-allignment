# Python Serial Communicator Script
# This script takes user input and sends it directly to the Teensy.
# The Teensy will print this message on its own serial monitor.

import serial
import time
import sys

# --- Configuration ---
# NOTE: Replace with your actual Teensy port (e.g., 'COM3' or '/dev/ttyACM0')
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200
# ---------------------

def connect_serial():
    """Initializes and returns the serial connection object."""
    try:
        # Create a Serial object
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=1  # Timeout in seconds
        )
        time.sleep(2) # Wait for the connection to fully establish
        print(f"--- Successfully connected to {ser.name} at {BAUD_RATE} baud. ---")
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to serial port {SERIAL_PORT}: {e}")
        print("Please check the port name and ensure the Teensy is plugged in and running the sketch.")
        sys.exit(1)

def send_message(ser, message):
    """Sends a message string to the Teensy without waiting for a reply."""
    # Ensure the message ends with a newline character, which the Teensy is expecting
    message_to_send = (message + '\n').encode('utf-8')
    
    print(f"Sending: '{message}'")
    ser.write(message_to_send)
    # The Teensy will print this on its monitor. No response is expected here.


def main():
    """Main function to handle the communication loop."""
    ser = connect_serial()
    
    print("\nEnter messages to send to the Teensy.")
    print("Type 'QUIT' or 'CTRL+C' to exit.")

    while True:
        try:
            # Get raw input message (allows spaces and mixed case)
            user_input = input("Message to Teensy: ").strip()
            
            if user_input.upper() == "QUIT":
                print("Exiting communicator.")
                break
            
            if user_input:
                # Send the user input as a message
                send_message(ser, user_input)
            
        except KeyboardInterrupt:
            print("\nExiting communicator.")
            break
        except EOFError:
            print("\nExiting communicator.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    ser.close()
    print("Serial connection closed.")

if __name__ == "__main__":
    # Ensure pyserial is installed: pip install pyserial
    main()