import tkinter as tk
import speech_recognition as sr
import threading
import queue
import asyncio
from bleak import BleakClient, BleakScanner
from datetime import datetime


#Arduino BLE settings
DEVICE_NAME = "AudioLight"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

#main window
root = tk.Tk()
root.title("Voice Controlled Lighting System")
root.geometry("850x650")
root.configure(bg="#151922")
root.resizable(False, False)

#speech recognizer
recognizer = sr.Recognizer()

# Samsung Galaxy Buds2 Pro microphone through PipeWire/PulseAudio
MICROPHONE_INDEX = 1
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

#communicate between threads
command_queue = queue.Queue()
ble_queue = queue.Queue()
outgoing_ble_queue = queue.Queue()

#device states (updated from Arduino status notifications)
hallway_on = False
bathroom_on = False
fan_on = False

system_running = True
ble_connected = False

#latest sensor reading
lux_reading = None


#update the device status
def update_status():
    if hallway_on:
        hallway_status.config(text="ON", fg="#22c55e")
    else:
        hallway_status.config(text="OFF", fg="#f87171")

    if bathroom_on:
        bathroom_status.config(text="ON", fg="#22c55e")
    else:
        bathroom_status.config(text="OFF", fg="#f87171")

    if fan_on:
        fan_status.config(text="VENT OPEN", fg="#22c55e")
    else:
        fan_status.config(text="VENT CLOSED", fg="#f87171")


#update the ambient light display
def update_lux(value):
    global lux_reading

    lux_reading = value

    if value is None:
        lux_status.config(
            text="Unavailable",
            fg="#fbbf24"
        )
    else:
        lux_status.config(
            text=f"{value:.2f} lux",
            fg="#22c55e" if value < 40 else "#fbbf24"
        )


#add a command to history
def add_history(command, result):
    current_time = datetime.now().strftime("%H:%M:%S")

    history_list.insert(
        0,
        current_time + "  |  " + command + "  |  " + result
    )


#convert Arduino status text into GUI values
def parse_arduino_status(status_text):
    status_values = {}

    for item in status_text.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            status_values[key.strip()] = value.strip()

    return status_values


#receive live status updates from Arduino
def ble_notification_handler(sender, data):
    try:
        status_text = data.decode("utf-8").strip()
        status_values = parse_arduino_status(status_text)
        ble_queue.put(("device_status", status_values))
    except Exception as error:
        print("BLE notification error:", error)


#keep one BLE connection open for commands and live sensor updates
async def ble_connection_loop():
    global ble_connected

    while system_running:
        try:
            print("Searching for Arduino...")

            device = await BleakScanner.find_device_by_name(
                DEVICE_NAME,
                timeout=10
            )

            if device is None:
                raise Exception("Arduino not found. Check that it is powered on.")

            print("Arduino found:", device.address)

            async with BleakClient(device, timeout=15) as client:
                ble_connected = True
                print("Connected to Arduino.")

                await client.start_notify(
                    CHARACTERISTIC_UUID,
                    ble_notification_handler
                )

                #Request the first complete sensor and device status.
                await client.write_gatt_char(
                    CHARACTERISTIC_UUID,
                    b"GET_STATUS",
                    response=True
                )

                ble_queue.put(("connection", "Connected to Arduino"))

                while system_running and client.is_connected:
                    try:
                        command = outgoing_ble_queue.get_nowait()
                    except queue.Empty:
                        command = None

                    if command is not None:
                        try:
                            await client.write_gatt_char(
                                CHARACTERISTIC_UUID,
                                command.encode("utf-8"),
                                response=True
                            )
                            ble_queue.put(("sent", command))
                            print("Arduino command sent:", command)
                        except Exception as error:
                            ble_queue.put(("send_error", (command, str(error))))
                            raise

                    await asyncio.sleep(0.1)

        except Exception as error:
            ble_connected = False
            print("BLE connection error:", error)
            ble_queue.put(("connection_error", str(error)))
            await asyncio.sleep(3)

    ble_connected = False


#run the persistent BLE connection in a background thread
def ble_worker():
    asyncio.run(ble_connection_loop())


#listen for voice commands
def listen_for_commands():
    global system_running

    try:
        microphone = sr.Microphone(
            device_index=MICROPHONE_INDEX
        )

        with microphone as source:
            print("Calibrating Samsung Galaxy Buds2 Pro microphone...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=2
            )

            print("Microphone ready!")
            print("Energy threshold:", recognizer.energy_threshold)

        while system_running:
            try:
                command_queue.put(
                    ("status", "Listening... Speak a command.")
                )

                with microphone as source:
                    audio = recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=5
                    )

                command = recognizer.recognize_google(
                    audio
                ).lower()

                print("You said:", command)

                # hallway light commands
                if (
                    "turn on the hallway light" in command
                    or "turn on hallway light" in command
                ):
                    command_queue.put(
                        ("command", "Turn ON the Hallway Light")
                    )

                elif (
                    "turn off the hallway light" in command
                    or "turn off hallway light" in command
                ):
                    command_queue.put(
                        ("command", "Turn OFF the Hallway Light")
                    )

                # bathroom light commands
                elif (
                    "turn on the bathroom light" in command
                    or "turn on bathroom light" in command
                ):
                    command_queue.put(
                        ("command", "Turn ON the Bathroom Light")
                    )

                elif (
                    "turn off the bathroom light" in command
                    or "turn off bathroom light" in command
                ):
                    command_queue.put(
                        ("command", "Turn OFF the Bathroom Light")
                    )

                # ventilation servo commands
                elif (
                    "turn on the exhaust fan" in command
                    or "turn on exhaust fan" in command
                ):
                    command_queue.put(
                        ("command", "Turn ON the Exhaust Fan")
                    )

                elif (
                    "turn off the exhaust fan" in command
                    or "turn off exhaust fan" in command
                ):
                    command_queue.put(
                        ("command", "Turn OFF the Exhaust Fan")
                    )

                # stop command
                elif "stop system" in command:
                    command_queue.put(("stop", ""))
                    break

                else:
                    command_queue.put(
                        (
                            "status",
                            "Command not recognised. Try again."
                        )
                    )

            except sr.WaitTimeoutError:
                continue

            except sr.UnknownValueError:
                print("Speech was captured but could not be understood.")
                command_queue.put(
                    (
                        "status",
                        "Sorry, I could not understand."
                    )
                )

            except sr.RequestError as error:
                print("Speech recognition error:", error)

                command_queue.put(
                    ("status", "Recognition service error.")
                )

    except Exception as error:
        print("Microphone error:", error)
        command_queue.put(("error", str(error)))


#send recognised voice commands directly to Arduino
def handle_voice_command(command):
    command_map = {
        "Turn ON the Hallway Light": ("HALLWAY_ON", "Hallway light ON command"),
        "Turn OFF the Hallway Light": ("HALLWAY_OFF", "Hallway light OFF command"),
        "Turn ON the Bathroom Light": ("BATHROOM_ON", "Bathroom light ON command"),
        "Turn OFF the Bathroom Light": ("BATHROOM_OFF", "Bathroom light OFF command"),
        "Turn ON the Exhaust Fan": ("FAN_ON", "Ventilation open command"),
        "Turn OFF the Exhaust Fan": ("FAN_OFF", "Ventilation close command")
    }

    if command not in command_map:
        return

    ble_command, description = command_map[command]

    listening_status.config(
        text="Sending command to Arduino...",
        fg="#60a5fa"
    )

    add_history(command, "Sending")
    outgoing_ble_queue.put(ble_command)


#process microphone messages, BLE results and live Arduino status
def check_command_queue():
    global system_running
    global hallway_on, bathroom_on, fan_on, ble_connected

    try:
        #process voice recognition messages
        while not command_queue.empty():
            event_type, value = command_queue.get_nowait()

            if event_type == "status":
                listening_status.config(
                    text=value,
                    fg="#22c55e"
                )

            elif event_type == "command":
                handle_voice_command(value)

            elif event_type == "stop":
                close_application()
                return

            elif event_type == "error":
                listening_status.config(
                    text="Microphone error - check terminal",
                    fg="#f87171"
                )
                add_history("Microphone", "Error")

        #process BLE connection and device status messages
        while not ble_queue.empty():
            event_type, value = ble_queue.get_nowait()

            if event_type == "connection":
                ble_connected = True
                listening_status.config(
                    text=value,
                    fg="#22c55e"
                )

            elif event_type == "connection_error":
                ble_connected = False
                listening_status.config(
                    text="Connecting to Arduino...",
                    fg="#fbbf24"
                )

            elif event_type == "sent":
                add_history(value, "BLE command delivered")
                listening_status.config(
                    text="Command sent - waiting for device status",
                    fg="#60a5fa"
                )

            elif event_type == "send_error":
                command, error_message = value
                print("BLE send error:", error_message)
                listening_status.config(
                    text="BLE command failed - check connection",
                    fg="#f87171"
                )
                add_history(command, "Failed: BLE communication error")

            elif event_type == "device_status":
                status_values = value

                #Update the lux display from the actual BH1750 reading.
                lux_text = status_values.get("LUX", "INVALID")
                if lux_text == "INVALID":
                    update_lux(None)
                else:
                    try:
                        sensor_value = float(lux_text)
                        update_lux(sensor_value if sensor_value >= 0 else None)
                    except ValueError:
                        update_lux(None)

                #Update device cards using the actual Arduino status.
                hallway_on = status_values.get("HALLWAY") == "ON"
                bathroom_on = status_values.get("BATHROOM") == "ON"
                fan_on = status_values.get("FAN") == "ON"
                update_status()

    except tk.TclError:
        return

    if system_running:
        root.after(200, check_command_queue)


#close the application
def close_application():
    global system_running

    system_running = False
    root.destroy()


#create the header
tk.Label(
    root,
    text="VOICE CONTROL SYSTEM",
    font=("Arial", 23, "bold"),
    fg="white",
    bg="#151922"
).pack(pady=(18, 5))

tk.Label(
    root,
    text="Smart Lighting and Ventilation Management",
    font=("Arial", 11),
    fg="#9ca3af",
    bg="#151922"
).pack(pady=(0, 15))


#system status panel
status_frame = tk.Frame(
    root,
    bg="#202735",
    padx=20,
    pady=12
)
status_frame.pack(fill="x", padx=30)

tk.Label(
    status_frame,
    text="SYSTEM STATUS",
    font=("Arial", 11, "bold"),
    fg="#9ca3af",
    bg="#202735"
).pack(anchor="w")

listening_status = tk.Label(
    status_frame,
    text="Starting microphone...",
    font=("Arial", 12, "bold"),
    fg="#22c55e",
    bg="#202735"
)
listening_status.pack(anchor="w", pady=(6, 0))


#ambient light sensor panel
lux_frame = tk.Frame(
    root,
    bg="#202735",
    padx=20,
    pady=10
)
lux_frame.pack(fill="x", padx=30, pady=(10, 0))

tk.Label(
    lux_frame,
    text="AMBIENT LIGHT LEVEL",
    font=("Arial", 10, "bold"),
    fg="#9ca3af",
    bg="#202735"
).pack(side="left")

lux_status = tk.Label(
    lux_frame,
    text="Waiting for Arduino...",
    font=("Arial", 11, "bold"),
    fg="#fbbf24",
    bg="#202735"
)
lux_status.pack(side="right")


#device status cards
device_frame = tk.Frame(
    root,
    bg="#151922"
)
device_frame.pack(fill="x", padx=30, pady=15)


#hallway light card
hallway_card = tk.Frame(
    device_frame,
    bg="#202735",
    padx=12,
    pady=14
)
hallway_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 6)
)

tk.Label(
    hallway_card,
    text="HALLWAY LIGHT",
    font=("Arial", 11, "bold"),
    fg="white",
    bg="#202735"
).pack()

hallway_status = tk.Label(
    hallway_card,
    text="OFF",
    font=("Arial", 18, "bold"),
    fg="#f87171",
    bg="#202735"
)
hallway_status.pack(pady=8)


# bathroom light card
bathroom_card = tk.Frame(
    device_frame,
    bg="#202735",
    padx=12,
    pady=14
)
bathroom_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=6
)

tk.Label(
    bathroom_card,
    text="BATHROOM LIGHT",
    font=("Arial", 11, "bold"),
    fg="white",
    bg="#202735"
).pack()

bathroom_status = tk.Label(
    bathroom_card,
    text="OFF",
    font=("Arial", 18, "bold"),
    fg="#f87171",
    bg="#202735"
)
bathroom_status.pack(pady=8)


# ventilation servo card
fan_card = tk.Frame(
    device_frame,
    bg="#202735",
    padx=12,
    pady=14
)
fan_card.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(6, 0)
)

tk.Label(
    fan_card,
    text="VENTILATION",
    font=("Arial", 11, "bold"),
    fg="white",
    bg="#202735"
).pack()

fan_status = tk.Label(
    fan_card,
    text="VENT CLOSED",
    font=("Arial", 15, "bold"),
    fg="#f87171",
    bg="#202735"
)
fan_status.pack(pady=8)


# recent commands section
tk.Label(
    root,
    text="RECENT COMMANDS",
    font=("Arial", 12, "bold"),
    fg="white",
    bg="#151922"
).pack(anchor="w", padx=30)

history_frame = tk.Frame(
    root,
    bg="#202735"
)
history_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(8, 12)
)

history_list = tk.Listbox(
    history_frame,
    bg="#202735",
    fg="#d1d5db",
    font=("Arial", 10),
    borderwidth=0,
    highlightthickness=0,
    selectbackground="#374151"
)
history_list.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

add_history("System started", "Ready")


# start Bluetooth communication
bluetooth_thread = threading.Thread(
    target=ble_worker,
    daemon=True
)
bluetooth_thread.start()

# start voice recognition
microphone_thread = threading.Thread(
    target=listen_for_commands,
    daemon=True
)
microphone_thread.start()

root.after(200, check_command_queue)
root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()

