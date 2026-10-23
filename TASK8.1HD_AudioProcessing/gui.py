import tkinter as tk
import speech_recognition as sr
import threading
import queue
import asyncio
from bleak import BleakClient, BleakScanner
from datetime import datetime


# Arduino BLE settings
DEVICE_NAME = "AudioLight"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

# create the main window
root = tk.Tk()
root.title("Voice Controlled Lighting System")
root.geometry("850x650")
root.configure(bg="#151922")
root.resizable(False, False)

# create the speech recognizer
recognizer = sr.Recognizer()
MICROPHONE_INDEX = 1

# communicate between threads
command_queue = queue.Queue()
ble_queue = queue.Queue()

# device states
hallway_on = False
bathroom_on = False
fan_on = False

system_running = True
confirmation_open = False
ble_connected = False

# latest sensor reading
lux_reading = None


# update the device status
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


# update the ambient light display
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


# add a command to history
def add_history(command, result):
    current_time = datetime.now().strftime("%H:%M:%S")

    history_list.insert(
        0,
        current_time + "  |  " + command + "  |  " + result
    )


# send a command to the Arduino over BLE
async def send_ble_command(command):
    print("Searching for Arduino...")

    device = await BleakScanner.find_device_by_name(
        DEVICE_NAME,
        timeout=10
    )

    if device is None:
        raise Exception(
            "Arduino not found. Check that it is powered on."
        )

    print("Arduino found:", device.address)

    async with BleakClient(device, timeout=15) as client:
        print("Connected to Arduino.")

        await client.write_gatt_char(
            CHARACTERISTIC_UUID,
            command.encode("utf-8"),
            response=True
        )

    print("Arduino command sent:", command)


# run BLE communication outside the GUI thread
def ble_worker(command, action):
    try:
        asyncio.run(send_ble_command(command))
        ble_queue.put(("success", (command, action)))
    except Exception as error:
        print("BLE error:", error)
        ble_queue.put(("error", (command, str(error))))


# listen for voice commands
def listen_for_commands():
    global system_running

    try:
        microphone = sr.Microphone(
            device_index=MICROPHONE_INDEX
        )

        with microphone as source:
            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

        print("Microphone ready!")

        while system_running:
            try:
                command_queue.put(
                    ("status", "Listening... Speak a command.")
                )

                with microphone as source:
                    audio = recognizer.listen(
                        source,
                        timeout=5,
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


# display the confirmation window
def show_confirmation(command):
    global confirmation_open

    if confirmation_open:
        return

    confirmation_open = True

    listening_status.config(
        text="Command detected - awaiting confirmation",
        fg="#fbbf24"
    )

    command_window = tk.Toplevel(root)
    command_window.title("Confirm Command")
    command_window.geometry("420x250")
    command_window.configure(bg="#202735")
    command_window.resizable(False, False)
    command_window.transient(root)
    command_window.grab_set()

    tk.Label(
        command_window,
        text="VOICE COMMAND DETECTED",
        font=("Arial", 14, "bold"),
        fg="#60a5fa",
        bg="#202735"
    ).pack(pady=(25, 15))

    tk.Label(
        command_window,
        text=command,
        font=("Arial", 17, "bold"),
        fg="white",
        bg="#202735",
        wraplength=370
    ).pack(pady=10)

    # execute the confirmed command
    def execute_command():
        global confirmation_open

        confirmation_open = False
        command_window.destroy()

        # map the command to its BLE command and device
        if command == "Turn ON the Hallway Light":
            ble_command = "HALLWAY_ON"
            action = ("hallway", True)

        elif command == "Turn OFF the Hallway Light":
            ble_command = "HALLWAY_OFF"
            action = ("hallway", False)

        elif command == "Turn ON the Bathroom Light":
            ble_command = "BATHROOM_ON"
            action = ("bathroom", True)

        elif command == "Turn OFF the Bathroom Light":
            ble_command = "BATHROOM_OFF"
            action = ("bathroom", False)

        elif command == "Turn ON the Exhaust Fan":
            ble_command = "FAN_ON"
            action = ("fan", True)

        elif command == "Turn OFF the Exhaust Fan":
            ble_command = "FAN_OFF"
            action = ("fan", False)

        else:
            return

        listening_status.config(
            text="Sending command to Arduino...",
            fg="#60a5fa"
        )

        threading.Thread(
            target=ble_worker,
            args=(ble_command, action),
            daemon=True
        ).start()

    # cancel the command
    def cancel_command():
        global confirmation_open

        add_history(command, "Cancelled")
        confirmation_open = False
        command_window.destroy()

        listening_status.config(
            text="Command cancelled",
            fg="#fbbf24"
        )

        return_to_listening()

    # confirmation buttons
    button_frame = tk.Frame(
        command_window,
        bg="#202735"
    )
    button_frame.pack(pady=20)

    tk.Button(
        button_frame,
        text="OK - Execute",
        command=execute_command,
        font=("Arial", 11, "bold"),
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        width=14,
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=8)

    tk.Button(
        button_frame,
        text="Cancel",
        command=cancel_command,
        font=("Arial", 11, "bold"),
        bg="#374151",
        fg="white",
        activebackground="#4b5563",
        activeforeground="white",
        width=10,
        relief="flat",
        cursor="hand2"
    ).pack(side="left", padx=8)

    command_window.protocol(
        "WM_DELETE_WINDOW",
        cancel_command
    )


# return to listening after an action
def return_to_listening():
    if system_running:
        listening_status.config(
            text="Listening for next command...",
            fg="#22c55e"
        )


# process microphone messages and BLE results
def check_command_queue():
    global system_running
    global hallway_on, bathroom_on, fan_on

    try:
        # process voice recognition messages
        while not command_queue.empty():
            event_type, value = command_queue.get_nowait()

            if event_type == "status":
                if not confirmation_open:
                    listening_status.config(
                        text=value,
                        fg="#22c55e"
                    )

            elif event_type == "command":
                if not confirmation_open:
                    show_confirmation(value)

            elif event_type == "stop":
                close_application()
                return

            elif event_type == "error":
                listening_status.config(
                    text="Microphone error - check terminal",
                    fg="#f87171"
                )

                add_history("Microphone", "Error")

        # process BLE results
        while not ble_queue.empty():
            event_type, value = ble_queue.get_nowait()

            if event_type == "success":
                command, action = value
                device, state = action

                # update the relevant device card
                if device == "hallway":
                    hallway_on = state

                elif device == "bathroom":
                    bathroom_on = state

                elif device == "fan":
                    fan_on = state

                update_status()

                add_history(
                    command,
                    "Command sent; Arduino acknowledged BLE write"
                )

                listening_status.config(
                    text="Command sent to Arduino",
                    fg="#22c55e"
                )

                return_to_listening()

            elif event_type == "error":
                command, error_message = value

                print("BLE error:", error_message)

                listening_status.config(
                    text="BLE failed - check Arduino connection",
                    fg="#f87171"
                )

                add_history(command, "Failed: BLE connection error")

                return_to_listening()

    except tk.TclError:
        return

    if system_running:
        root.after(200, check_command_queue)


# close the application
def close_application():
    global system_running

    system_running = False
    root.destroy()


# create the header
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


# system status panel
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


# ambient light sensor panel
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


# device status cards
device_frame = tk.Frame(
    root,
    bg="#151922"
)
device_frame.pack(fill="x", padx=30, pady=15)


# hallway light card
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


# start voice recognition
microphone_thread = threading.Thread(
    target=listen_for_commands,
    daemon=True
)
microphone_thread.start()

root.after(200, check_command_queue)
root.protocol("WM_DELETE_WINDOW", close_application)
root.mainloop()

