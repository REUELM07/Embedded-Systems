import tkinter as tk
import RPi.GPIO as GPIO

# gpio pins for the three lights
lights = [18, 12, 13]

GPIO.setmode(GPIO.BCM)

# create pwm for each light
pwm = []

for pin in lights:
    GPIO.setup(pin, GPIO.OUT)
    light = GPIO.PWM(pin, 1000)
    light.start(0)
    pwm.append(light)


# update the brightness of a light
def set_brightness(number, value):
    pwm[number].ChangeDutyCycle(float(value))


# create the gui
window = tk.Tk()
window.title("Living Room Light Control")

tk.Label(window, text="Light Intensity Control").pack(pady=10)

# create one slider for each light
for number in range(3):
    tk.Scale(
        window,
        from_=0,
        to=100,
        orient="horizontal",
        label=f"Light {number + 1}",
        command=lambda value, n=number: set_brightness(n, value)
    ).pack(pady=5)


# run the gui
try:
    window.mainloop()

finally:
    # stop pwm and clean the gpio pins
    for light in pwm:
        light.stop()

    GPIO.cleanup()