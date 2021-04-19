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
        super().__init__(uuid, uuid_is_path)
        self.serial = kinetic.Controllers.Serial()
        self.motor_left = TestBot.MotorLeft(self)
        self.motor_right = TestBot.MotorRight(self)
        self.motor_bind = TestBot.MotorBind(self)
        self.speed = 255
        TestBot.network_init(self)
        TestBot.client_listen(self, {"SETSPEED": TestBot.set_speed(self, int(self.network.receive())),
                                     "FORWARD": self.motor_bind.forward(self.speed),
                                     "BACKWARD": self.motor_bind.backward(self.speed),
                                     "CLOCKWISE": self.motor_bind.clockwise(self.speed),
                                     "COUNTERCLOCKWISE": self.motor_bind.counterclockwise(self.speed)}, True, True)

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
        pwm = True
        direction = True

        def __init__(self, outer_self: object):
            super().__init__(outer_self.serial,
                             kinetic.Controllers.load_keymap("F://KINETIC//tests//motor_MotorLeft_keymap.json"))
            TestBot.MotorLeft.pwm = self.is_pwm_enabled
            TestBot.MotorLeft.direction = self.is_direction_enabled

    class MotorRight(kinetic.Components.Kinetics.Motor):
        """
        Right-side motor.
        """
        pwm = True
        direction = True

        def __init__(self, outer_self: object):
            super().__init__(outer_self.serial,
                             kinetic.Controllers.load_keymap("F://KINETIC//tests//motor_MotorRight_keymap.json"))
            TestBot.MotorLeft.pwm = self.is_pwm_enabled
            TestBot.MotorLeft.direction = self.is_direction_enabled

    class MotorBind(kinetic.ActionGroups.DualMotor):
        """
        Dual motor action group.
        """

        def __init__(self, outer_self: object):
            super().__init__(outer_self.motor_left, outer_self.motor_right)


if __name__ == "__main__":
    bot = TestBot("6ae2f3bd-2b55-468a-88a3-af0eeae03896", False)
