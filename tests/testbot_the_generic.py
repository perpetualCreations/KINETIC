"""
██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗
██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝
█████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║
██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║
██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝

Project KINETIC
Made by perpetualCreations

example kinetic.Agent module.
"""

import kinetic

class TestBot(kinetic.Agent):
    """
    Test Bot: Generic as ever, comes in green and emerald colors.
    """
    def __init__(self, uuid, uuid_is_path):
        super(TestBot, self).__init__(uuid, uuid_is_path)
        self.serial = kinetic.Controllers.Serial()
        self.motor_left = TestBot.MotorLeft()
        self.motor_right = TestBot.MotorRight()
        self.motor_bind = TestBot.MotorBind()
        self.speed = 255
        TestBot.network_init(self)
        TestBot.client_listen(self, {"SETSPEED":TestBot.set_speed(self, int(self.network.receive())), "FORWARD":self.motor_bind.forward(self.speed), "BACKWARD":self.motor_bind.backward(self.speed), "CLOCKWISE":self.motor_bind.clockwise(self.speed), "COUNTERCLOCKWISE":self.motor_bind.counterclockwise(self.speed)}, True, True)

    def set_speed(self, speed: int) -> None:
        """
        Assigns parameter input to self.speed.

        :param speed: int, 0-255
        :return: None
        """
        self.speed = abs(speed)

    class MotorLeft(kinetic.Components.Kinetics.Motor):
        """
        Left-side motor.
        """
        def __init__(self):
            super(MotorLeft, self).__init__(self.serial, kinetic.Controllers.load_keymap("F://KINETIC//tests//motor_MotorLeft_keymap.json"))

    class MotorRight(kinetic.Components.Kinetics.Motor):
        """
        Right-side motor.
        """
        def __init__(self):
            super(MotorRight, self).__init__(self.serial, kinetic.Controllers.load_keymap("F://KINETIC//tests//motor_MotorRight_keymap.json"))

    class MotorBind(kinetic.ActionGroups.DualMotor):
        """
        Dual motor action group.
        """
        def __init__(self):
            super(MotorBind, self).__init__(self.motor_left, self.motor_right)

if __name__ == "__main__":
    bot = TestBot("6ae2f3bd-2b55-468a-88a3-af0eeae03896", False)
