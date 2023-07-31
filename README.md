# Geiger Counter
## CircuitPython DFRobot Geiger counter implementation.

*NOTE: CANNOT GUARANTEE THIS WORKS, AND CANNOT TEST IT.* To quote DFRobot: **"This product is not a professional measuring instrument, it is only suitable for principle research and teaching demonstration. Not for use in radiation dose measurement that directly affects personal safety."**

This is a simple CircuitPython application that runs on an Adafruit Metro M4 Express (but could be easily modified to run on many others). It uses a DFRobot Geiger Counter sensor and has code to implement simple CPM (counts per minute) and uSv/h metrics which are then reported to Adafruit IO. The DFRobot sensor could easily be wired differently but I was trying to preserve the existing wiring harness so I could try it with a few other Arduino compatibile format boards. As such, I ended up with the following:

- Adafruit Metro M4 Express with Airlift ([Adafruit](https://www.adafruit.com/product/4000))
- A DFRobot Gravity IO Extension board ([Amazon](https://a.co/d/dOZaMgP) or [DFRobot](https://www.dfrobot.com/product-1009.html))
- And, of course, the DF Robot Geiger counter module (I got mine from [PiHut](https://thepihut.com/products/gravity-geiger-counter-module-ionizing-radiation-detector) or [DFRobot](https://www.dfrobot.com/product-2547.html))

![image of completed project](https://github.com/avnc/geiger/blob/b3079368eeb564b645382b995fef11e30f33ef3a/IMG_1430.jpeg)

You could skip the IO extension board (and just cut the wires) but was simpler this way. I made a simple enclosure in TinkerCad that I 3D printed to hold the thing - it's awful and I will not share until I can clean it up... 

The geiger tube itself relies on *high voltage*, so best to heed the warnings on the [DFRobot wiki](https://wiki.dfrobot.com/SKU_SEN0463_Gravity_Geiger_Counter_Module):

**"⚡ The Geiger tube is driven by a voltage of up to 400V, after powering on do not touch the high voltage circuit near the positive pole of the Geiger tube."**

I didn't find any other Circuitpython or Micropython code but DFRobot does provide an Arduino library that you can take a look at [here on Github](https://github.com/cdjq/DFRobot_Geiger).

To run the code as provided, you'll need the Metro M4 Express, however it shouldn't be hard to run with other Circuitpython supported microcontrollers. Adafruit IO account also needed but you can [set one up for free here](https://io.adafruit.com/) (or just comment out that part of the code). The setttings.toml file has placeholders for you to fill in your WiFi and Adafruit IO info.
