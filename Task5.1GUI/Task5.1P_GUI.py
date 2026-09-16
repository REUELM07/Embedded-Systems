import tkinter as tk
from gpiozero import LED

#connect each room light to a different Raspberry Pi GPIO pin
living_room = LED(17)
bathroom = LED(27)
closet = LED(22)


#this function controls which room light should be turned ON
def change_light():

    #turn OFF all lights before turning ON the selected light
    living_room.off()
    bathroom.off()
    closet.off()

    #get the room selected by the user from the radio buttons
    selected = light_choice.get()

    #turn ON the LED according to the selected room
    if selected == "Living Room":
        living_room.on()

    elif selected == "Bathroom":
        bathroom.on()

    elif selected == "Closet":
        closet.on()


#this function turns OFF all LEDs and safely closes the GUI
def exit_program():

    #make sure all lights are OFF before closing the program
    living_room.off()
    bathroom.off()
    closet.off()

    #close the main GUI window
    window.destroy()


#create the main Tkinter window for the lighting system
window = tk.Tk()

#give the GUI a title and set its size
window.title("Smart House Lighting")
window.geometry("350x300")


#this variable stores the room selected by the user
light_choice = tk.StringVar()


#display the main heading of the GUI
tk.Label(
    window,
    text="Smart House Lighting",
    font=("Arial", 18)
).pack(pady=20)


#store the available rooms so radio buttons can be created for each one
rooms = ["Living Room", "Bathroom", "Closet"]


#create one radio button for each room
#when a radio button is selected, change_light() is called
for room in rooms:
    tk.Radiobutton(
        window,
        text=room,
        variable=light_choice,
        value=room,
        command=change_light,
        font=("Arial", 12)
    ).pack(pady=5)


#create an Exit button to safely stop the lighting system
tk.Button(
    window,
    text="Exit",
    command=exit_program,
    font=("Arial", 12)
).pack(pady=20)


#keep the GUI running and wait for user actions
window.mainloop()
