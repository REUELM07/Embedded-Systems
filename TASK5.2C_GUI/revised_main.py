import tkinter as tk 
import RPi.GPIO as GPIO 
 
 
# GPIO SETUP 
 
# gpio pins used for the three lights 
# gpio 18 -> light 1 
# gpio 12 -> light 2 
# gpio 13 -> light 3 
lights = [18, 12, 13] 
 
# use bcm gpio numbering instead of physical pin numbering 
GPIO.setmode(GPIO.BCM) 
 
# list used to store the pwm objects for each light 
pwm = [] 
 
# create pwm for every light 
for pin in lights: 
    GPIO.setup(pin, GPIO.OUT) 
 
    # pwm frequency = 1000 hz 
    light = GPIO.PWM(pin, 1000) 
 
    # start with 0% brightness 
    light.start(0) 
 
    # store the pwm object in the list 
    pwm.append(light) 
 
 
 
# BRIGHTNESS FUNCTION 
 
# this function changes the brightness of a selected light 
# 
# number -> tells us which light to control 
# value  -> brightness value from the gui slider 
# 
# the value is used as the pwm duty cycle 
# 
# 0%   -> light off 
# 50%  -> medium brightness 
# 100% -> maximum brightness 
def set_brightness(number, value): 
 
    # convert the slider value into a number 
    brightness = float(value) 
 
    # change the pwm duty cycle of the selected light 
    pwm[number].ChangeDutyCycle(brightness) 
 
# GUI SETUP 
 
# create the main tkinter window 
window = tk.Tk() 
 
# window title 
window.title("Smart Light Control") 
 
# window size 
# css-style: width = 500px, height = 430px 
window.geometry("500x430") 
 
# background colour of the complete gui 
# css-style: background-color = #0F172A [DARK BLUE]
window.configure(bg="#0F172A") 
 
# GUI HEADING 
tk.Label( 
    window, 
 
    # text displayed at the top 
    text="SMART LIGHT CONTROL", 
 
    # css-style: font-size = 20px 
    # css-style: font-weight = bold 
    font=("Arial", 20, "bold"), 
 
    # css-style: background-color = #0F172A 
    bg="#0F172A", 
 
    # css-style: color = white 
    fg="#FFFFFF" 
).pack( 
    # css-style: margin-top/bottom = 20px 
    pady=20 
) 
 
 
 
# SLIDER SETUP 
 
# different colours for the three light controls 
# this makes each light easy to identify 
slider_colours = [ 
    "#3B82F6",   # blue -> light 1 
    "#14B8A6",   # teal -> light 2 
    "#8B5CF6"    # purple -> light 3 
] 
 
 
# create one slider for each light 
for number in range(3): 
    tk.Scale( 
        window, 
 
        # slider range 
        # 0 = light off 
        # 100 = maximum brightness 
        from_=0, 
        to=100, 
 
        # display the slider horizontally 
        orient="horizontal", 
 
        # name shown above each slider 
        label=f"Light {number + 1}", 
 
        # call set_brightness() when the slider changes 
        # 
        # n=number keeps the correct light number 
        command=lambda value, n=number: 
            set_brightness(n, value), 
 
        # css-style: font-size = 14px 
        # css-style: font-weight = bold 
        font=("Arial", 14, "bold"), 
 
        # css-style: background-color 
        bg=slider_colours[number], 
 
        # css-style: color = white 
        fg="#FFFFFF", 
 
        # colour of the slider track 
        # css-style: track-color = #E2E8F0 
        troughcolor="#E2E8F0", 
 
        # colour when the mouse is over the slider 
        # css-style: hover-color 
        activebackground=slider_colours[number], 
 
        # border thickness 
        # css-style: border-width = 3px 
        bd=3, 
 
        # border style 
        # css-style: border-style = solid 
        relief="solid", 
 
        # width of the slider 
        # css-style: width = 350px 
        length=350 
 
    ).pack( 
        # css-style: margin-top/bottom = 12px 
        pady=12 
    ) 
 
# RUN THE GUI 
 
try: 
 
    # keep the window running until the user closes it 
    window.mainloop() 
 
 
finally: 
 
    # stop all pwm signals when the program closes 
    for light in pwm: 
        light.stop() 
 
    # reset all gpio pins 
    GPIO.cleanup() 