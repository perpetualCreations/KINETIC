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
            is safely ignored, default 1
        :type speed: int, optional
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
            is safely ignored, default 1
        :type speed: int, optional
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
            is safely ignored, default 1
        :type speed: int, optional
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
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_left.backward(speed)
        self.motor_right.forward(speed)


class QuadMotor:
    """Abstraction for quad motor drive train."""

    def __init__(self, motor_front_left: Components.Kinetics.Motor,
                 motor_front_right: Components.Kinetics.Motor,
                 motor_back_left: Components.Kinetics.Motor,
                 motor_back_right: Components.Kinetics.Motor):
        """
        Class initialization, creating instance variables.

        Takes two Components.Kinetics.Motor instances.

        :param motor_front_left: front-left-side motor
        :type motor_front_left: Components.Kinetics.Motor
        :param motor_front_right: front-right-side motor
        :type motor_front_right: Components.Kinetics.Motor
        :param motor_back_left: back-left-side motor
        :type motor_back_left: Components.Kinetics.Motor
        :param motor_back_right: back-right-side motor
        :type motor_back_right: Components.Kinetics.Motor
        """
        self.motor_front_left = motor_front_left
        self.motor_front_right = motor_front_right
        self.motor_back_left = motor_back_left
        self.motor_back_right = motor_back_right

    def forward(self, speed: int = 1) -> None:
        """
        Quad-motor control to move forward.

        Safe to use regardless if direction is disabled.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.forward(speed)
        self.motor_front_right.forward(speed)
        self.motor_back_left.forward(speed)
        self.motor_back_right.forward(speed)

    def backward(self, speed: int = 1) -> None:
        """
        Quad-motor control to move backward.

        Safe to use regardless if direction is disabled, however if direction \
            is disabled, is effectively the same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.backward(speed)
        self.motor_front_right.backward(speed)
        self.motor_back_left.backward(speed)
        self.motor_back_right.backward(speed)

    def clockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin clockwise, effectively turning right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.forward(speed)
        self.motor_back_left.forward(speed)
        self.motor_front_right.backward(speed)
        self.motor_back_right.backward(speed)

    def counterclockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin counterclockwise, effectively turning left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.backward(speed)
        self.motor_back_left.backward(speed)
        self.motor_front_right.forward(speed)
        self.motor_back_right.forward(speed)


class MecanumQuadMotor(QuadMotor):
    """Extends QuadMotor drive train with mecanum-wheel strafing."""

    def __init__(self):
        """Class initialization."""
        super().__init__()

    def left(self, speed: int = 1) -> None:
        """
        Quad-motor control to strafe left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.backward(speed)
        self.motor_back_left.forward(speed)
        self.motor_front_right.forward(speed)
        self.motor_back_right.backward(speed)

    def right(self, speed: int = 1) -> None:
        """
        Quad-motor control to strafe right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.forward(speed)
        self.motor_back_left.backward(speed)
        self.motor_front_right.backward(speed)
        self.motor_back_right.forward(speed)

    def diagonal_forward_left(self, speed: int = 1) -> None:
        """
        Quad-motor control to move diagonally forward-left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_back_left.forward(speed)
        self.motor_front_right.forward(speed)

    def diagonal_forward_right(self, speed: int = 1) -> None:
        """
        Quad-motor control to move diagonally forward-right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.forward(speed)
        self.motor_back_right.forward(speed)

    def diagonal_backward_left(self, speed: int = 1) -> None:
        """
        Quad-motor control to move diagonally backward-left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.backward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_back_left.backward(speed)
        self.motor_front_right.backward(speed)

    def diagonal_backward_right(self, speed: int = 1) -> None:
        """
        Quad-motor control to move diagonally backward-right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.backward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.backward(speed)
        self.motor_back_right.backward(speed)

    def back_right_clockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin clockwise around the back right corner, \
            effectively turning right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.forward(speed)
        self.motor_back_left.forward(speed)

    def back_right_counterclockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin counterclockwise around the back right \
            corner, effectively turning left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.backward(speed)
        self.motor_back_left.backward(speed)

    def front_left_clockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin clockwise around the front left corner, \
            effectively turning right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_right.forward(speed)
        self.motor_back_right.forward(speed)

    def front_left_counterclockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin counterclockwise around the front left \
            corner, effectively turning left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_right.backward(speed)
        self.motor_back_right.backward(speed)

    def back_clockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin clockwise around the center of the back, \
            effectively turning right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.forward(speed)
        self.motor_front_right.backward(speed)

    def back_counterclockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin counterclockwise around the center of the \
            back, effectively turning left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_front_left.backward(speed)
        self.motor_front_right.forward(speed)

    def front_clockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin clockwise around the center of the front, \
            effectively turning right.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_back_left.forward(speed)
        self.motor_back_right.backward(speed)

    def front_counterclockwise(self, speed: int = 1) -> None:
        """
        Quad-motor control to spin counterclockwise around the center of the \
            front, effectively turning left.

        Requires at least direction control, otherwise is effectively the \
            same as calling QuadMotor.forward.

        :param speed: absolute, 0 < x =< 1 indicating motor speed, return None
            if 0, x > 1 will result in x becoming 1, if PWM is disabled speed
            is safely ignored, default 1
        :type speed: int, optional
        """
        self.motor_back_left.backward(speed)
        self.motor_back_right.forward(speed)
