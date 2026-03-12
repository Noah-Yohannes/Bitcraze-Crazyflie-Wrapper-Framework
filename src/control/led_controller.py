import time

class LEDController:

    def __init__(self, cf):
        self.cf = cf

    def identify_drone(self):
        address = self.cf.link_uri.upper()

        if address.endswith("E8"):
            self.activate_ring_led()

        elif address.endswith("E9"):
            self.activate_onboard_led()

        else:
            print("[LED] Unknown Crazyflie")

    def activate_ring_led(self):
        """a function to control the LED board. The onboard LED board sold by Bitcraze works only with the brushed drones. """
        try:
            self.cf.param.set_value("ring.effect", "13")
            self.cf.param.set_value("ring.solidRed", "255")
            self.cf.param.set_value("ring.solidGreen", "40")
            self.cf.param.set_value("ring.solidBlue", "0")
        except Exception as e:
            print("LED error:", e)

    def activate_onboard_led(self):
        """A function to control the onboard LEDs of the drone. This function works with both brushed and brushless drones."""

        blink_seq = [
            0b10010000,
            0b10001000,
            0b10000100,
            0b10000010,
            0b10000001,
        ]

        for _ in range(20):
            for mask in blink_seq:
                self.cf.param.set_value("led.bitmask", str(mask))
                time.sleep(0.1)

        self.cf.param.set_value("led.bitmask", "0")