"""Module for hardware abstraction types."""

from typing import Union, Tuple, Literal
from time import sleep
import cv2
import swbs
from imutils.video import VideoStream
from kinetic import controllers as Controllers
from kinetic.exceptions import ComponentError


class Generic:
    """
    Perfectly Generic Object, colored a perfectly generic green.

    Generic component class, with no special attributes. \
        Exists as a placeholder.

    When creating a component class that does not have an existing \
        subclass to derive from in Components, use this class for \
            kinetic.generate to properly recognize the class as a \
                component for serial endpoint generation.
    """

    def __init__(self, controller, keymap: dict):
        """
        Class initialization, creating instance variables.

        :param controller: class instance of controllers, controller to use
            for interfacing with component
        :param keymap: should contain keys for their respective serial
        commands
        :type keymap: dict
        """
        self.controller = controller
        self.keymap: dict = keymap


class Kinetics:
    """Moving parts on your agent."""

    class Motor:
        """Generic motor."""

        def __init__(self, controller, keymap: dict,
                     enable_pwm: bool = True, enable_direction: bool = True):
            """
            Class initialization, creating instance variables.

            Supports controllers.Serial instances as a controller.

            :param controller: class instance of controllers, controller to use
                for interfacing with component
            :param keymap: should contain keys FORWARDS, BACKWARDS, SPEED,
                BRAKE, RELEASE, for their respective serial commands
            :type keymap: dict
            :param enable_pwm: whether Motor instance supports PWM speed
                control, default True
            :type enable_pwm: bool
            :param enable_direction: whether Motor instance supports direction
                control, default True
            :type enable_direction: bool
            """
            self.control: Union[int, float] = 0
            self.is_pwm_enabled: bool = enable_pwm
            self.is_direction_enabled: bool = enable_direction
            self.keymap: dict = keymap
            if isinstance(controller, Controllers.Serial) is not True:
                raise ComponentError("Unsupported controller.")
            self.controller = controller

        def set_control(self, new: Union[float, int],
                        autocommit: bool = True) -> None:
            """
            Set self.control, unless autocommit is False, forwards to serial \
                resulting in actuation.

            :param new: limited to -1 to 1, abstracts motor direction where 1
                is forwards, -1 is backwards, and 0 is full-stop, gradients
                between 1 to 0 and 0 to -1 control speed (if PWM is available)
            :type new: Union[float, int]
            :param autocommit: whether new control variable should be committed
                immediately to serial
            :type autocommit: bool
            """
            self.control = min([max([new, -1]), 1])
            if autocommit is True:
                if self.control == 0:
                    self.controller.send(self.keymap["BRAKE"])
                    return None
                if self.is_pwm_enabled is True:
                    self.controller.send(
                        self.keymap["SPEED"], "SEND",
                        (str(round(255 * abs(self.control))),))
                if self.is_direction_enabled is False:
                    self.controller.send(self.keymap["FORWARDS"])
                else:
                    if self.control > 0:
                        self.controller.send(self.keymap["FORWARDS"])
                    elif self.control < 0:
                        self.controller.send(self.keymap["BACKWARDS"])
                self.controller.send(self.keymap["RELEASE"])

        def forward(self, speed: int = 1) -> None:
            """
            Tell Motor.set_control to move forward.

            Safe to use regardless if direction is disabled.

            :param speed: absolute, 0 < x =< 1 indicating motor speed, return
                None if 0, x > 1 will result in x becoming 1, if PWM is
                disabled speed is safely ignored
            :type speed: int
            """
            Kinetics.Motor.set_control(self, abs(speed))

        def backward(self, speed: int = 1) -> None:
            """
            Tell Motor.set_control to move backward.

            Safe to use regardless if direction is disabled, however if \
                direction is disabled, is effectively the same as calling \
                    Motor.forward.

            :param speed: absolute, 0 < x =< 1 indicating motor speed, return
                None if 0, x > 1 will result in x becoming 1, if PWM is
                disabled speed is safely ignored
            :type speed: int
            """
            Kinetics.Motor.set_control(self, abs(speed) * -1)

        def stop(self) -> None:
            """
            Tell Motor.set_control to stop.

            Safe to use regardless if direction or PWM is disabled.
            """
            Kinetics.Motor.set_control(self, 0)


class Sensors:
    """Sensor inputs and other data streams on your agent."""

    class USBCamera:
        """Generic USB camera."""

        def __init__(self, source: int = 0, use_pi_camera: bool = False,
                     resolution: Tuple[int, int] = (1920, 1080),
                     frame_rate: int = 60, quality: int = 80):
            """
            Class initialization, creating instance variables.

            Accepts no controller.

            :param source: source index piped into VideoStream src parameter,
                default 0
            :type source: int
            :param use_pi_camera: whether to use a Raspberry Pi camera (if
                installed) piped into VideoStream usePiCamera parameter,
                default False
            :type use_pi_camera: bool
            :param resolution: tuple, video stream resolution formatted (WIDTH,
                HEIGHT), default (1920, 1080)
            :param frame_rate: int, video stream frame rate piped into
                VideoStream framerate parameter, default 60
            :param quality: int, image quality to compress to, 0-100,
                higher quality costs more bandwidth to transmit, the opposite
                is true for lower quality, default 80
            """
            self.source: int = source
            self.use_pi_camera: bool = use_pi_camera
            self.resolution: Tuple[int, int] = resolution
            self.frame_rate: int = frame_rate
            self.stream: Union[None, VideoStream] = None
            self.quality: int = quality

        def start_stream(self) -> None:
            """Create and start VideoStream object, self.stream."""
            self.stream = VideoStream(self.source, self.use_pi_camera,
                                      self.resolution, self.frame_rate).start()

        def stop_stream(self) -> None:
            """Stop VideoStream object, self.stream, and revert it back to \
                None."""
            if self.stream is None:
                return None
            self.stream.stop()
            self.stream = None

        def collect_stream(self, debug: bool = False):
            """
            Read self.stream VideoStream, use cv2.IMWRITE_JPEG_QUALITY for \
                compression.

            :param debug: if True show collected image with cv2.imshow, default
                False
            :type debug: bool
            :return: cv2 JPEG encoded image, or None if video stream has not
                been started and is still None
            """
            if self.stream is None:
                return None
            # placeholder for encoding result
            result = None
            try:
                result, image = cv2.imencode(
                    ".jpg", self.stream.read(), [int(cv2.IMWRITE_JPEG_QUALITY),
                                                 self.quality])
                if debug is True:
                    cv2.imshow("KINETIC COLLECT_STREAM DEBUG",
                               self.stream.read())
                    cv2.waitKey(1)
                return image
            except cv2.error as parent_exception:
                print("CV IMENCODE RESULT: ", result)
                raise ComponentError("Camera stream failed to capture image."
                                     ) from parent_exception

        def broadcast_stream(self, host: str, port: int,
                             key: Union[str, bytes, None],
                             key_is_path: bool = False,
                             restart_delay: Union[int, None] = 1,
                             debug: bool = False) -> None:
            """
            Create swbs.Client instance, with host, port, and key parameters \
                pointing to a swbs.Host or swbs.Server instance, or other \
                    compatible swbs.Instance derivative.

            Is a blocking function.

            When using SWBS to receive bytes from TX, set parameter \
                return_bytes to True.

            TODO more compression

            Decode the image on the receiving end with,

            cv2.imdecode(numpy.frombuffer(host.receive(500000), numpy.uint8), \
                cv2.IMREAD_COLOR)

            If self.stream is None, returns None before execution starts.
            If ComponentError is raised when collecting VideoStream image, \
                restarts camera and then waits 1 second, unless the delay is \
                    specified otherwise, before resuming.

            :param host: hostname of host to connect to
            :type host: str
            :param port: port that host is listening on
            :type port: int
            :param key: AES encryption key, if None, AES is disabled
            :type key: Union[str, bytes, None]
            :param key_is_path: if True key parameter is treated as path to
                file containing encryption key, default False
            :type key_is_path: bool
            :param restart_delay: delay in seconds after a video stream
                restart due to an exception being raised, if None delay is
                disabled, default 1
            :type restart_delay: Union[int, None]
            :param debug: print MD5 hash of image frame to stdout if True,
                also show raw image with cv2.imshow, default False
            :type debug: bool
            """
            if self.stream is None:
                return None
            streamer: swbs.Client = swbs.Client(host, port, key, key_is_path)
            streamer.connect()
            while True:
                try:
                    frame = self.collect_stream(debug).tobytes()
                    if debug is True:
                        # yes, this fetches the MD5 class from swbs,
                        # imported from Pycryptodomex, no I feel no shame
                        print(swbs.MD5.new(frame).hexdigest())
                    streamer.send(frame)
                except ComponentError:
                    Sensors.USBCamera.stop_stream(self)
                    Sensors.USBCamera.start_stream(self)
                    if restart_delay is not None:
                        sleep(restart_delay)

    class VL53L0X:
        """
        VL53L0X time-of-flight distance sensor.

        For future release iteration: adjustable measurement time budget, \
            and other API inclusions.
        """

        def __init__(self, controller, keymap: dict):
            """
            Class initialization, creating instance variables.

            Supports controllers.Serial instances as a controller.

            :param controller: class instance of controllers, controller to use
                for interfacing with component
            :param keymap: should contain key COLLECT for their respective
                serial commands
            :type keymap: dict
            """
            self.keymap: dict = keymap
            if isinstance(controller, Controllers.Serial) is True:
                self.controller = controller
            else:
                raise ComponentError("Unsupported controller.")

        def collect(self, round_to: Union[int, None]) -> \
                Union[int, float, None]:
            """
            Collect distance data from sensor.

            :param round_to: decimal to round to, None to return raw,
                default None
            :type round_to: Union[int, None]
            :return: distance in millimeters, None if type conversion failed
            :rtype: Union[int, float, None]
            """
            self.controller.send(self.keymap["COLLECT"])
            try:
                result = int(self.controller.receive())
            except ValueError:
                return None
            if round_to is not None:
                round(result, round_to)
            return result

    class SenseHAT:
        """Raspberry Pi SenseHAT sensors."""

        def __init__(self, sense: Controllers.SenseHAT):
            """
            Class initialization, creating instance variables.

            Accepts SenseHAT controller.
            Requires SenseHAT and Raspbian host with the SenseHAT APT package \
                installed.
            See https://pythonhosted.org/sense-hat/ for more information.

            :param sense: object, SenseHAT controller instance
            """
            self.sense = sense.sense
            try:
                # pylint: disable=import-outside-toplevel
                from gpiozero import CPUTemperature
            except ModuleNotFoundError as parent_exception:
                raise ComponentError("SenseHAT component was initialized "
                                     "without pre-requisites.") from \
                                         parent_exception
            self.cpu_temperature: CPUTemperature = CPUTemperature

        def get_temperature(self, offset_cpu: bool = True,
                            round_to: Union[int, None] = None) -> \
                Union[int, float]:
            """
            Collect temperature in Celsius.

            :param offset_cpu: bool, if True accounts for CPU temperature
                leeching into SenseHAT temperature readings, default True
            :type offset_cpu: bool
            :param round_to: decimal to round to, None to return raw,
                default None
            :type round_to: Union[int, None]
            :return: Union[int, float], temperature in Celsius
            """
            raw = self.sense.get_temperature()
            if offset_cpu is True:
                raw = raw - (self.cpu_temperature() - raw) / 5.466
            if round_to is not None:
                raw = round(raw, round_to)
            return raw

        def get_pressure(self, round_to: Union[int, None] = None) -> \
                Union[int, float]:
            """
            Collect atmospheric pressure in millibars.

            :param round_to: decimal to round to, None to return raw, default
                None
            :type round_to: Union[int, None]
            :return: pressure in millibars
            :rtype: Union[int, float]
            """
            raw = self.sense.get_pressure()
            if round_to is not None:
                raw = round(raw, round_to)
            return raw

        def get_humidity(self, round_to: Union[int, None] = None) -> \
                Union[int, float]:
            """
            Collect atmospheric humidity by a percentage.

            :param round_to: decimal to round to, None to return raw, default
                None
            :type round_to: Union[int, None]
            :return: humidity by percentage
            :rtype: Union[int, float]
            """
            raw = self.sense.get_humidity()
            if round_to is not None:
                raw = round(raw, round_to)
            return raw

        def get_orientation(self, round_to: Union[int, None] = None) -> list:
            """
            Collect orientation data in degrees on axes X, Y, and Z.

            :param round_to: decimal to round to, None to return raw, default
                None
            :type round_to: Union[int, None]
            :return: ROLL, PITCH, and YAW axes orientation in degrees,
                in that order respectively
            :rtype: list
            """
            self.sense.set_imu_config(True, True, True)
            raw = self.sense.get_gyroscope()
            for_return = [raw["roll"], raw["pitch"], raw["yaw"]]
            if round_to is not None:
                for x in range(0, len(for_return)):
                    for_return[x] = round(for_return[x], round_to)
            return for_return

        def get_accelerometer(self, round_to: Union[int, None] = None) -> list:
            """
            Collect accelerometer data in G-force on axes X, Y, and Z.

            :param round_to: decimal to round to, None to return raw, default
                None
            :type round_to: Union[int, None]
            :return: X, Y, and Z axes acceleration in G-force, in that order
                respectively
            :rtype: list
            """
            raw = self.sense.get_accelerometer_raw()
            for_return = [raw["x"], raw["y"], raw["z"]]
            if round_to is not None:
                for x in range(0, len(for_return)):
                    for_return[x] = round(for_return[x], round_to)
            return for_return

        def get_compass(self, round_to: Union[int, None] = None) -> \
                Union[int, float]:
            """
            Collect compass data in degrees, 0 being north.

            :param round_to: decimal to round to, None to return raw, default
                None
            :type round_to: Union[int, None]
            :return: compass degrees
            :rtype: Union[int, float]
            """
            raw = self.sense.get_compass()
            if round_to is not None:
                raw = round(raw, round_to)
            return raw


class Interfaces:
    """Non-INET interfaces and I/O on your agent, including lights and \
        displays."""

    class SenseHAT:
        """TODO: Raspberry Pi SenseHat LED matrix and joystick interface."""

        def __init__(self, sense: Controllers.SenseHAT):
            """
            Class initialization, creating instance variables.

            Accepts SenseHAT controller.
            Requires SenseHAT and Raspbian host with the SenseHAT APT package \
                installed.
            See https://pythonhosted.org/sense-hat/ for more information.

            :param sense: object, SenseHAT controller instance
            """
            self.sense = sense.sense

        def led_set_rotation(self, state: Literal[0, 90, 180, 270]) -> None:
            """
            Rotates LED image by given state representing number of degrees.

            :param state: degrees to rotate the image by
            :type state: Literal[0, 90, 180, 270]
            """
            self.sense.set_rotation(state)

        def flip_horizontal(self) -> None:
            """Reflect LED image horizontally."""
            self.sense.flip_h()

        def flip_vertical(self) -> None:
            """Reflect LED image vertically."""
            self.sense.flip_v()

        # i am so sorry
        def set_pixels(self, image:
                       Tuple[Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int],
                             Tuple[int, int, int], Tuple[int, int, int]]) -> \
                None:
            """
            Set LED image using a tuple, with 64 elements, being tuples that \
                represent the RGB value (0-255, 0-255, 0-255) of each pixel, \
                    the LED being set relative to its corresponding RGB \
                        value's position in the image tuple.

            :param image: tuple representing image to be rendered on LED matrix
            :type image: Tuple[Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int]]
            """
            self.sense.set_pixels(list(map(list, image)))  # type: ignore

        def get_pixels(self) -> \
                Tuple[Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int],
                      Tuple[int, int, int], Tuple[int, int, int]]:
            """
            Return LED image represented as a tuple, with 64 elements, being \
                tuples that represent the RGB value (0-255, 0-255, 0-255) of \
                    each pixel, the LED being represented relative to its \
                        corresponding RGB value's position in the image tuple.

            :return: tuple representing image rendered on LED matrix
            :rtype: Tuple[Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int],
                Tuple[int, int, int], Tuple[int, int, int]]
            """
            return tuple(map(tuple, self.sense.get_pixels()))  # type: ignore

        def set_pixel(self, x: int, y: int, rgb: Tuple[int, int, int]) -> None:
            """
            Set a pixel on the LED matrix.

            :param x: x coordinate of the pixel, 0-7
            :type x: int
            :param y: y coordinate of the pixel, 0-7
            :type y: int
            :param rgb: RGB value of the pixel, (0-255, 0-255, 0-255)
            :type rgb: Tuple[int, int, int]
            """
            self.sense.set_pixel(x, y, rgb)

        def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
            """
            Get a pixel from the LED matrix.

            :param x: x coordinate of the pixel, 0-7
            :type x: int
            :param y: y coordinate of the pixel, 0-7
            :type y: int
            :return: RGB value of the pixel, (0-255, 0-255, 0-255)
            :rtype: Tuple[int, int, int]
            """
            return self.sense.get_pixel(x, y)

        def load_image(self, path: str) -> None:
            """
            Set LED image using an image file.

            File specified with path must be 8x8 pixels in size. The Portable \
                Network Graphics (.png) file format should be a support file \
                    type. Other file formats may also work, however are \
                        untested.

            :param path: path to image file
            :type path: str
            """
            self.sense.load_image(path)

        def clear(self, rgb: Tuple[int, int, int] = (0, 0, 0)) -> None:
            """
            Clear LED image or specify an RGB value with a tuple to overwrite \
                the LED matrix with a single color.

            :param rgb: color to fill LED matrix with, default (0, 0, 0)
            :type rgb: Tuple[int, int, int]
            """
            self.sense.clear(rgb)

        def show_message(self, text: str, speed: float = 0.1,
                         foreground: Tuple[int, int, int] = (255, 255, 255),
                         background: Tuple[int, int, int] = (0, 0, 0)) -> None:
            """
            Scroll text across the LED matrix.

            :param text: text to displayed
            :type text: str
            :param foreground: RGB value for the color of foreground text,
                defaults to (255, 255, 255)
            :type foreground: Tuple[int, int, int]
            :param background: RGB value for the color of background, defaults
                to (0, 0, 0)
            :type background: Tuple[int, int, int]
            :param speed: speed at which text scrolls, represented by the
                amount of time spent paused before advancing text characters
                one column to the left, defaults to 0.1
            :type speed: float
            """
            self.sense.show_message(text, speed, foreground, background)


class Power:
    """Power distribution, management, sensing, storage, and control \
        components on your agent."""

    class VoltageSensor:
        """Analogue input from a 7.5K+30K ohm voltage divider, connected to a \
            circuit."""

        def __init__(self, controller, keymap: dict):
            """
            Class initialization, creating instance variables.

            Supports controllers.Serial instances as a controller.

            :param controller: class instance of controllers, controller to use
                for interfacing with component
            :param keymap: should contain key COLLECT, for their respective
                serial commands
            :type keymap: dict
            """
            if isinstance(controller, Controllers.Serial) is True:
                self.controller = controller
            else:
                raise ComponentError("Unsupported controller.")
            self.keymap: dict = keymap

        def collect(self, round_to: Union[int, None]) -> Union[int, float]:
            """
            Collect voltage data from sensor.

            :param round_to: decimal to round to, None to return raw, default
                None
            :type round_to: Union[int, None]
            :return: sensor voltage
            :rtype: Union[int, float]
            """
            self.controller.send(self.keymap["COLLECT"])
            result = int(self.controller.receive())
            if round_to is not None:
                round(result, round_to)
            return result

    class Switch:
        """Transistor, relay, or MOSFET switching component."""

        def __init__(self, controller, keymap: dict):
            """
            Class initialization, creating instance variables.

            Supports controllers.Serial instances as a controller.

            :param controller: class instance of controllers, controller to use
                for interfacing with component
            :param keymap: should contain keys OPEN and CLOSE, for their
                respective serial commands
            :type keymap: dict
            """
            if isinstance(controller, Controllers.Serial) is True:
                self.controller = controller
            else:
                raise ComponentError("Unsupported controller.")
            self.keymap: dict = keymap

        def open(self) -> None:
            """
            Open switch, stopping the flow of current.

            :return: None
            """
            self.controller.send(self.keymap["OPEN"])

        def close(self) -> None:
            """
            Close switch, continuing the flow of current.

            :return: None
            """
            self.controller.send(self.keymap["CLOSE"])
