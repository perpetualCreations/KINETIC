"""
██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗
██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝
█████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║
██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║
██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝

Project KINETIC
Made by perpetualCreations
"""

import swbs
import socket
import serial
from uuid import uuid4
from Cryptodome.Hash import SHA3_512
from typing import Union
from sys import exit
from subprocess import call
import cv2
from imutils.video import VideoStream

class Exceptions:
    """
    Parent class of all module exceptions.
    """
    class ControllerError(BaseException):
        """
        Exception raised by a Controller class instance.
        """
    class ComponentError(BaseException):
        """
        Exception raised by a Component class instance.
        """

class Controllers:
    """
    Parent class of controller abstractions for controlling components.
    """
    class Serial:
        """
        Abstraction class for a serial interface controller.
        """
        def __init__(self, port: str = "/dev/ttyACM0", timeout: int = 5):
            """
            Class initialization, creating class variables and serial object.

            :param port: str, serial port for connection to be made, default /dev/ttyACM0
            :param timeout: int, timeout in seconds for serial port, default 5
            :ivar self.serial_instance: object, pyserial object, can be safely accessed while respecting self.serial_lock,
                including raw I/O without wrapper, do not operate while self.serial_lock is True, set self.serial_lock to True
                for the duration of raw I/O and back to False upon completing the operation
            :ivar self.serial_lock: bool, lock boolean, to prevent multiple multiple calls to serial, a primitive version of a thread resource lock
            """
            self.serial_instance = serial.Serial(timeout = timeout)
            self.serial_instance.port = port
            self.serial_lock = False  # bool, if True new serial operations cannot be made until changed back to False
                                      # prevents more than one serial operation being done simultaneously

            try:
                try: self.serial_instance.open()
                except serial.serialposix.SerialException as ParentException: raise Exceptions.ControllerError("Failed to initialize serial controller.") from ParentException
            except AttributeError:  # compatibility for Windows, this is an extremely dirty bodge
                try: self.serial_instance.open()
                except serial.serialwin32.SerialException as ParentException: raise Exceptions.ControllerError("Failed to initialize serial controller.") from ParentException

        def send(self, message: Union[str, bytes]) -> None:
            """
            Sends bytes through serial.

            :param message: Union[str, bytes], data to be sent
            :return: None
            """
            if isinstance(message, str): message = message.encode("ascii", "replace")
            while self.serial_lock is True: pass
            try:
                self.serial_lock = True
                for x in range(0, len(message)): self.serial_instance.write(message[x])
                self.serial_instance.write(b"\x0A")
                self.serial_lock = False
                return None
            except objects.serial.serialposix.SerialException as ParentException:
                self.serial_lock = False
                raise Exceptions.ControllerError("Serial controller failed to send bytes.") from ParentException

        def receive(self) -> str:
            """
            Receives bytes through serial.

            :return: str, decoded byte string
            """
            while self.serial_lock is True: pass
            try:
                self.serial_lock = True
                response = self.serial_instance.read_until(b"\x0A").rstrip(b"\n").decode("utf-8", "replace")
                self.serial_lock = False
                return response
            except objects.serial.serialposix.SerialException as ParentException:
                self.serial_lock = False
                raise Exceptions.ControllerError("Serial controller failed to receive bytes.") from ParentException

    class SenseHAT:
        """
        Raspberry Pi SenseHAT module.
        """
        def __init__(self):
            """
            Class initialization, creating class variables and SenseHAT object.
            Requires SenseHAT and Raspbian host with the SenseHAT APT package installed.

            See https://pythonhosted.org/sense-hat/ for more information.
            """
            try:
                from sense_hat import SenseHat
                from gpiozero import CPUTemperature
            except ModuleNotFoundError as ParentException:
                raise Exceptions.ComponentError("SenseHAT component was initialized without pre-requisites.") from ParentException
            self.sense = SenseHat()
            self.sense.set_imu_config(True, True, True)

class Components:
    """
    Parent class of hardware abstraction types.
    """
    class Kinetics:
        """
        Moving parts on your agent.
        """
        class Motor:
            """
            Generic DC motor.
            """
            def __init__(self, controller: object, keymap: dict, enable_pwm: bool = True, enable_direction: bool = True):
                """
                Class initialization, creating class variables.
                Supports Controllers.Serial instance(s) as a controller.

                :ivar self.control: int, limited to -1 to 1, abstracts motor direction where 1 is forwards, -1 is backwards,
                    and 0 is full-stop, gradients between 1 to 0 and 0 to -1 control speed (if PWM is available),
                    not to be overwritten directly, use Motor.set_control.
                :ivar self.is_pwm_enabled: bool, dump of parameter enable_pwm
                :ivar self.is_direction_enabled: bool, dump of parameter enable_direction
                :ivar self.keymap: dict, dump of parameter keymap
                :ivar self.controller: object, controller instance
                :param controller: class instance of Controllers, controller to use for interfacing with component
                :param keymap: dict, should contain keys FORWARDS, BACKWARDS, SPEED, BRAKE, for their respective serial commands
                :param enable_pwm: bool, whether Motor instance supports PWM speed control, default True
                :param enable_direction: bool, whether Motor instance supports direction control, default True
                """
                self.control = 0
                self.is_pwm_enabled = enable_pwm
                self.is_direction_enabled = enable_direction
                self.keymap = keymap
                if isinstance(controller, Controllers.Serial) is True: self.controller = controller
                else: raise Exceptions.ComponentError("Unsupported controller.")

            def set_control(self, new: Union[float, int], autocommit: bool = True) -> None:
                """
                Set self.control, unless autocommit is False, forwards to serial resulting in actuation.

                :ivar self.control: see documentation for __init__
                :param new: Union[float, int], new control integer
                :param autocommit: bool, whether new control variable should be committed immediately to serial
                :return: None
                """
                self.control = min([max([new, -1]), 1])
                if autocommit is True:
                    if self.control == 0:
                        self.controller.send(self.keymap["BRAKE"])
                        return None
                    if self.is_pwm_enabled is True: self.controller.send(self.keymap["SPEED"] + " " + str(255 * self.control))
                    if self.is_direction_enabled is False: self.controller.send(self.keymap["FORWARDS"])
                    else:
                        if self.control > 0: self.controller.send(self.keymap["FORWARDS"])
                        elif self.control < 0: self.controller.send(self.keymap["BACKWARDS"])

    class Sensors:
        """
        Sensor inputs and other data streams on your agent.
        """
        class USBCamera:
            """
            Generic USB camera.
            """
            def __init__(self, source: int = 0, use_pi_camera: bool = False, resolution: tuple = (1920, 1080), frame_rate: int = 60, quality: int = 80):
                """
                Class initialization, creating class variables.
                Accepts no controller.

                :ivar self.stream: object, VideoStream object, created by USBCamera.start_stream, None until first call
                :ivar self.source: int, dump of parameter source
                :ivar self.use_pi_camera: bool, dump of parameter use_pi_camera
                :ivar self.resolution: tuple, dump of parameter resolution
                :ivar self.frame_rate: int, dup of parameter int
                :ivar self.quality: int, dump of parameter quality
                :param source: int, source index piped into VideoStream src parameter, default 0
                :param use_pi_camera: bool, whether to use a Raspberry Pi camera (if installed) piped into VideoStream usePiCamera parameter, default False
                :param resolution: tuple, video stream resolution formatted (WIDTH, HEIGHT) and piped into VideoStream resolution parameter, default (1920, 1080))
                :param frame_rate: int, video stream frame rate piped into VideoStream framerate parameter, default 60
                :param quality: int, image quality to compress to, 0-100, higher quality costs more bandwidth to transmit, the opposite is true for lower quality, default 80
                """
                self.source = source
                self.use_pi_camera = use_pi_camera
                self.resolution = resolution
                self.frame_rate = frame_rate
                self.stream = None
                self.quality = quality

            def start_stream(self) -> None:
                """
                Creates and starts VideoStream object, self.stream.

                :return: None
                """
                self.stream = VideoStream(self.source, self.use_pi_camera, self.resolution, self.frame_rate).start()

            def stop_stream(self) -> None:
                """
                Stops VideoStream object, self.stream, and reverts it back to None.

                :return: None
                """
                self.stream.stop()
                self.stream = None

            def collect_stream(self) -> Union[object, None]:
                """
                Reads self.stream VideoStream, uses cv2.IMWRITE_JPEG_QUALITY for compression
                Returns None if video stream has not been started and is still None.

                :return: Union[object, None], cv2 JPEG encoded image
                """
                if self.stream is None: return None
                result = None # placeholder for encoding result
                try:
                    result, image = cv2.imencode(".jpg", self.stream.read(), [int(cv2.IMWRITE_JPEG_QUALITY), self.quality])
                    return image
                except cv2.error as ParentException:
                    print("CV IMENCODE RESULT: ", result)
                    raise Exceptions.ComponentError("Camera stream failed to capture image.") from ParentException

            def broadcast_stream(self) -> None:
                """
                TODO

                :return: None
                """
                raise NotImplementedError # NOTICE FOR FUTURE ME!!! DON'T USE IMAGEZMQ FOR CAMERA, CONVERT IMAGES TO BASE64, TRANSMIT AS BYTES

        class SenseHAT:
            """
            Raspberry Pi SenseHAT sensors.
            """
            def __init__(self, sense: Controllers.SenseHAT):
                """
                Class initialization, creating class variables.
                Accepts SenseHAT controller. Requires SenseHAT and Raspbian host with the SenseHAT APT package installed.

                See https://pythonhosted.org/sense-hat/ for more information.

                :ivar self.sense: object, SenseHat() instance, from parameter sense
                :param sense: object, SenseHAT controller instance
                """
                self.sense = sense.sense

            def get_temperature(self, offset_cpu = True, round_to: Union[int, None] = None) -> Union[int, float]:
                """
                Collects temperature in Celsius.

                :param offset_cpu: bool, if True accounts for CPU temperature leeching into SenseHAT temperature readings, default True
                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: Union[int, float], temperature in Celsius
                """
                raw = self.sense.get_temperature()
                if offset_cpu is True: raw = raw - (CPUTemperature() - raw) / 5.466
                if round_to is not None: raw = round(raw, round_to)
                return raw

            def get_pressure(self, round_to: Union[int, None] = None) -> Union[int, float]:
                """
                Collects atmospheric pressure in millibars.

                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: Union[int, float], pressure in millibars
                """
                raw = self.sense.get_pressure()
                if round_to is not None: raw = round(raw, round_to)
                return raw

            def get_humidity(self, round_to: Union[int, None] = None) -> Union[int, float]:
                """
                Collects atmospheric humidity by a percentage.

                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: Union[int, float], humidity by percentage
                """
                raw = self.sense.get_humidity()
                if round_to is not None: raw = round(raw, round_to)
                return raw

            def get_orientation(self, round_to: Union[int, None] = None) -> list:
                """
                Collects orientation data in degrees on axis X, Y, and Z.

                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: list, ROLL, PITCH, and YAW axis orientation in degrees, in that order respectively
                """
                self.sense.set_imu_config(True, True, True)
                raw = self.sense.get_orientation_degrees()
                for_return = [raw["roll"], raw["pitch"], raw["yaw"]]
                if round_to is not None:
                    for x in range(0, len(for_return)): for_return[x] = round(for_return[x], round_to)
                return for_return

            def get_accelerometer(self, round_to: Union[int, None] = None) -> list:
                """
                Collects accelerometer data in degrees on axis X, Y, and Z.

                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: list, ROLL, PITCH, and YAW axis orientation in degrees, in that order respectively
                """
                raw = self.sense.get_accelerometer()
                for_return = [raw["roll"], raw["pitch"], raw["yaw"]]
                if round_to is not None:
                    for x in range(0, len(for_return)): for_return[x] = round(for_return[x], round_to)
                return for_return

            def get_compass(self, round_to: Union[int, None] = None) -> Union[int, float]:
                """
                Collect compass data in degrees, 0 being north.

                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: Union[int, float], compass degrees
                """
                raw = self.sense.get_compass()
                if round_to is not None: raw = round(raw, round_to)
                return raw

    class Interfaces:
        """
        Non-INET interfaces and I/O on your agent, including lights and displays.
        """
        class SenseHAT:
            """
            Raspberry Pi SenseHat LED matrix and joystick interface.
            """
            def __init__(self, sense: Controllers.SenseHAT):
                """
                Class initialization, creating class variables.
                Accepts SenseHAT controller. Requires SenseHAT and Raspbian host with the SenseHAT APT package installed.

                See https://pythonhosted.org/sense-hat/ for more information.

                :ivar self.sense: object, SenseHat() instance, from parameter sense
                :param sense: object, SenseHAT controller instance
                """
                self.sense = sense.sense

    class Power:
        """
        Power distribution, management, sensing, storage, and control components on your agent.
        """
        class VoltageSensor:
            """
            Analogue input from a 7.5K+30K ohm voltage divider, connected to a circuit.
            """
            def __init__(self, controller: object, keymap: dict):
                """
                Class initialization, creating class variables.
                Supports Controllers.Serial instance(s) as a controller.

                :ivar self.controller: object, controller instance
                :ivar self.keymap: dict, dump of parameter keymap
                :param controller: class instance of Controllers, controller to use for interfacing with component
                :param keymap: dict, should contain key COLLECT, for their respective serial commands
                """
                if isinstance(controller, Controllers.Serial) is True: self.controller = controller
                else: raise Exceptions.ComponentError("Unsupported controller.")
                self.keymap = keymap

            def collect(self, round_to: Union[int, None]) -> Union[int, float]:
                """
                Collect voltage data from sensor.

                :param round_to: Union[int, None], decimal to round to, None to return raw, default None
                :return: Union[int, float], sensor voltage
                """
                self.controller.send(self.keymap["COLLECT"])
                result = int(self.controller.receive())
                if round_to is not None: round(result, round_to)
                return result

        class Switch:
            """
            Transistor, relay, or MOSFET switching component.
            """
            def __init__(self, controller: object, keymap: dict):
                """
                Class initialization, creating class variables.
                Supports Controllers.Serial instance(s) as a controller.

                :ivar self.controller: object, controller instance
                :ivar self.keymap: dict, dump of parameter keymap
                :param controller: class instance of Controllers, controller to use for interfacing with component
                :param keymap: dict, should contain keys OPEN and CLOSE, for their respective serial commands
                """
                if isinstance(controller, Controllers.Serial) is True: self.controller = controller
                else: raise Exceptions.ComponentError("Unsupported controller.")
                self.keymap = keymap

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

class ActionGroups:
    """
    Various abstractions for common actions that may involve controlling multiple components.
    """

class Agent:
    """
    Agent class for deriving from, for custom robotic agents.
    """
    def __init__(self):
        """
        Class initialization, creating class variables.

        :ivar self.id: str, Agent UUID
        """
        self.id = "6ae2f3bd-2b55-468a-88a3-af0eeae03896"
        self.network = None # swbs instance placeholder, overwritten by Agent.network_init

    def network_init(self, host:str = "arbiter.local", port:int = 999, key: Union[str, bytes, None] = None, key_is_path: bool = False) -> None:
        """
        Built-in network initialization, when invoked, tries to connect as a client to specified host controller. If one is not specified, tries arbiter.local as hostname.
        If connection fails, initializes self temporarily into a Host instance, waiting for a controller or a plain client pointing the agent to a controller.
        Client/controller should send b"CONTROLLER" or b"POINT <HOSTNAME HERE>" respectively. If agent receives neither, restarts socket. If signaled to be controller, re-initializes as client to controller with specified or default port. If signaled to another host, connects to supplied host with specified or default port.
        Operations are done on port 999 (connecting to and listening on) unless specified otherwise in parameters. AES is disabled by default, unless the key value is specified otherwise. Is blocking if entering Host state.

        :param host: str, expected controller hostname, default arbiter.local
        :param port: int, port connecting to in client mode, and listening on in host
        :param key: Union[str, bytes, None], if key_is_path is False, key string, otherwise path to key file, default False disabling AES
        :param key_is_path: bool, if True, key parameter is treated as path to key file for reading from, default False
        :return: None
        """
        try:
            self.network = swbs.Client(host, port, key, key_is_path)
            self.network.connect()
            return None
        except socket.error:
            self.network.close()
            self.network = swbs.Host(port, key, key_is_path = key_is_path)
            while True:
                self.network.listen()
                signal = self.network.receive()
                controller = None # placeholder for scope
                if signal == "CONTROLLER": controller = self.network.client_address[0]
                elif signal[:5] == "POINT": controller = signal.split(" ")[1] # this prevents a dictionary switch statement, find a rewrite
                if controller is not None:
                    self.network.disconnect()
                    self.network = swbs.Client(self.network.client_address[0], port, key, key_is_path)
                    self.network.connect()
                    return None
                else: self.network.restart()

    def stop(self, status: int, extended_callbacks = None) -> None:
        """
        Exits agent application. Executes optional supplied function parameter.

        :param status: int, exit status
        :param extended_callbacks: function, called before exiting, specify a function here to be invoked
        :return: None
        """
        if callable(extended_callbacks) is True: extended_callbacks()
        if self.network is not None: self.network.disconnect()
        exit(status)

    def shutdown(self, status: int = 0, extended_callbacks = None, command = "sudo shutdown now") -> None:
        """
        Runs OS-level shutdown command, default for Linux.
        In addition, runs Agent.stop and shares status and extended_callbacks parameters, which are both optional.
        Default exit code 0.

        :param status: see Agent.stop for parameter documentation
        :param extended_callbacks: see Agent.stop for parameter documentation
        :param command: str, shutdown command called through shell, default for Linux
        :return: None
        """
        call(command, shell = True)
        Agent.stop(self, status, extended_callbacks)

    def reboot(self, status: int = 0, extended_callbacks = None, command = "sudo reboot now") -> None:
        """
        Runs OS-level reboot command, default for Linux.
        In addition, runs Agent.stop and shares status and extended_callbacks parameters, which are both optional.
        Default exit code 0.

        :param status: see Agent.stop for parameter documentation
        :param extended_callbacks: see Agent.stop for parameter documentation
        :param command: str, reboot command called through shell, default for Linux
        :return: None
        """
        call(command, shell = True)
        Agent.stop(self, status, extended_callbacks)

    @staticmethod
    def update(command = "sudo apt update && apt upgrade -y") -> None:
        """
        Runs OS-level update command, default for Linux distributions using APT.

        :param command: str, update command called through shell, default for Linux
        :return: None
        """
        call(command, shell = True)
