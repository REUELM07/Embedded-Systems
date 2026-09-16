import tkinter as tk
from gpiozero import LED

#connect each room light to its GPIO pin
living_room = LED(17)
bathroom = LED(27)
closet = LED(22)

#turn off every light before switching on the selected one
def change_light():
    living_room.off()
    bathroom.off()
    closet.off()

    selected = light_choice.get()

    if selected == "Living Room":
        living_room.on()
    elif selected == "Bathroom":
        bathroom.on()
    elif selected == "Closet":
        closet.on()

#turn off all LEDs and close the GUI
def exit_program():
    living_room.off()
    bathroom.off()
    closet.off()
    window.destroy()

#create the main GUI window
window = tk.Tk()
window.title("Smart House Lighting")
window.geometry("350x300")

#stores which room the user selected
light_choice = tk.StringVar()

tk.Label(
    window,
    text="Smart House Lighting",
    font=("Arial", 18)
).pack(pady=20)

#each radio button represents one room in the house
rooms = ["Living Room", "Bathroom", "Closet"]

for room in rooms:
    tk.Radiobutton(
        window,
        text=room,
        variable=light_choice,
        value=room,
        command=change_light,
        font=("Arial", 12)
    ).pack(pady=5)

#exit button safely turns off the LEDs before closing
tk.Button(
    window,
    text="Exit",
    command=exit_program,
    font=("Arial", 12)
).pack(pady=20)

window.mainloop()