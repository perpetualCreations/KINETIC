"""Module for various abstractions to common actions that may involve \
    controlling multiple components."""

from kinetic import components as Components


class DualMotor:
    """Abstraction for dual motor drive train."""

    def __init__(self, motor_left: Components.Kinetics.Motor,
                 motor_right: Components.Kinetics.Motor):
        """
        Class initialization, creating instance variables.

        Takes two Components.Kinetics.Motor instances.

        :param motor_left: left-side motor
        :type motor_left: Components.Kinetics.Motor
        :param motor_right: right-side motor
        :type motor_right: Components.Kinetics.Motor
        """
        self.motor_left = motor_left
        self.motor_right = motor_right

    def forward(self, speed: int = 1) -> None:
        """
        Bi-motor control to move forward.

        Safe to use regardless if direction is disabled.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored
        :type speed: int
        """
        self.motor_left.forward(speed)
        self.motor_right.forward(speed)

    def backward(self, speed: int = 1) -> None:
        """
        Bi-motor control to move backward.

        Safe to use regardless if direction is disabled, however if direction \
            is disabled, is effectively the same as calling DualMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored
        :type speed: int
        """
        self.motor_left.backward(speed)
        self.motor_right.backward(speed)

    def clockwise(self, speed: int = 1) -> None:
        """
        Bi-motor control to spin clockwise, effectively turning right.

        Requires at least direction control, otherwise is effectively the \
            same as calling DualMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored
        :type speed: int
        """
        self.motor_left.forward(speed)
        self.motor_right.backward(speed)

    def counterclockwise(self, speed: int = 1) -> None:
        """
        Bi-motor control to spin counterclockwise, effectively turning left.

        Requires at least direction control, otherwise is effectively the \
            same as calling DualMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored
        :type speed: int
        """
        self.motor_left.backward(speed)
        self.motor_right.forward(speed)

# TODO write mecanum wheel drive train abstraction
