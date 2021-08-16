"""Module for controller abstractions to operate components."""

from json import load as json_load
from typing import Union, Literal
from threading import Lock
import serial
from kinetic.exceptions import ControllerError


def load_keymap(path: str) -> dict:
    """
    Load JSON keymap file with supplied path.

    :param path: path to JSON keymap file
    :type path: str
    :return: keymap as dictionary
    :rtype: dict
    """
    with open(path) as map_handler:
        return json_load(map_handler)


class Serial:
    """
    Abstraction class for a serial interface controller.

    Designed specifically for Arduino or other language-compatible \
        microcontrollers as serial endpoints. See kinetic.generate for \
            producing endpoint C code.
    """

    def __init__(self, port: str = "/dev/ttyACM0", timeout: int = 5):
        """
        Class initialization, creating instance variables and serial object.

        :param port: serial port for connection to be made, \
            default /dev/ttyACM0
        :type port: str
        :param timeout: timeout in seconds for serial port, default 5
        :type timeout: int
        """
        self.LOOKUP: dict = {"SEND": self.send, "RECEIVE": self.receive}
        self.serial_instance: serial.Serial = serial.Serial(timeout=timeout)
        self.serial_instance.port = port
        self.serial_lock: Lock = Lock()
        try:
            try:
                self.serial_instance.open()
            except serial.serialposix.SerialException as parent_exception:
                raise ControllerError("Failed to initialize serial controller"
                                      ".") from parent_exception
        except AttributeError:
            # compatibility for Windows tests, this is an extremely dirty bodge
            try:
                self.serial_instance.open()
            except serial.serialwin32.SerialException as parent_exception:
                raise ControllerError("Failed to initialize serial controller"
                                      ".") from parent_exception

    def send(self, message: Union[str, bytes],
             chain_call: Union[Literal["SEND", "RECEIVE"], None] = None,
             chain_call_parameters: Union[tuple, dict, None] = None,
             in_recursion: bool = False) -> None:
        """
        Send bytes through serial.

        :param message: data to be sent
        :type message: Union[str, bytes]
        :param chain_call: string specifying whether to "SEND" or "RECEIVE",
            None to disable, ignored if chain_call_parameters is empty,
            default None
        :type chain_call: Union[Literal["SEND", "RECEIVE"], None]
        :param chain_call_parameters: parameters for send or receive function
            call, ignored if chain_call is empty, default None
        :type chain_call_parameters: Union[tuple, dict, None]
        :param in_recursion: if True function call ignores self.serial_lock,
            should not be True unless triggered by chain call, default False
        :type in_recursion: bool
        """
        if isinstance(message, str):
            message = message.encode("ascii", "replace")
        if in_recursion is not True:
            self.serial_lock.acquire()
        try:
            for index, _ in enumerate(message):
                self.serial_instance.write(message[index])
            self.serial_instance.write(b"\x0A")
            if chain_call is not None and chain_call_parameters is not None:
                if isinstance(chain_call_parameters, list):
                    if chain_call_parameters[3] is not True:
                        # minor tuple mutability hack
                        chain_call_parameters = list(chain_call_parameters)
                        chain_call_parameters[3] = True
                        chain_call_parameters = tuple(chain_call_parameters)
                    return self.LOOKUP[
                        chain_call.upper()](*chain_call_parameters)
                if isinstance(chain_call_parameters, dict):
                    chain_call_parameters["in_recursion"] = True
                    return Serial.LOOKUP[chain_call.upper()](
                        **chain_call_parameters)
        except serial.serialposix.SerialException as parent_exception:
            raise ControllerError("Serial controller failed to send bytes.") \
                from parent_exception
        except KeyError as parent_exception:
            raise ControllerError("Invalid chain call.") from parent_exception
        finally:
            self.serial_lock.release()

    def receive(self,
                chain_call: Union[Literal["SEND", "RECEIVE"], None] = None,
                chain_call_parameters: Union[tuple, dict, None] = None,
                in_recursion: bool = False) -> str:
        """
        Receives bytes through serial.

        :param chain_call: string specifying whether to "SEND" or "RECEIVE",
            None to disable, ignored if chain_call_parameters is empty,
            default None
        :type chain_call: Union[Literal["SEND", "RECEIVE"], None]
        :param chain_call_parameters: parameters for send or receive function
            call, ignored if chain_call is empty, default None
        :type chain_call_parameters: Union[tuple, dict, None]
        :param in_recursion: if True function call ignores self.serial_lock,
            should not be True unless triggered by chain call, default False
        :type in_recursion: bool
        :return: str, decoded byte string
        """
        if in_recursion is not True:
            self.serial_lock.acquire()
        try:
            response = self.serial_instance.read_until(b"\x0A").rstrip(b"\n").\
                decode("utf-8", "replace")
            if chain_call is not None and chain_call_parameters is not None:
                if isinstance(chain_call_parameters, list):
                    if chain_call_parameters[3] is not True:
                        # minor tuple mutability hack
                        chain_call_parameters = list(chain_call_parameters)
                        chain_call_parameters[3] = True
                        chain_call_parameters = tuple(chain_call_parameters)
                    Serial.LOOKUP[chain_call.upper()](*chain_call_parameters)
                    return response
                if isinstance(chain_call_parameters, dict):
                    chain_call_parameters["in_recursion"] = True
                    self.LOOKUP[chain_call.upper()](**chain_call_parameters)
                    return response
            return response
        except serial.serialposix.SerialException as parent_exception:
            raise ControllerError("Serial controller failed to receive bytes"
                                  ".") from parent_exception
        except KeyError as parent_exception:
            raise ControllerError("Invalid chain call.") from parent_exception
        finally:
            self.serial_lock.release()


class SenseHAT:
    """Raspberry Pi SenseHAT module."""

    def __init__(self):
        """
        Class initialization, creating instance variables and SenseHAT object.

        Requires SenseHAT and Raspbian host with the SenseHAT APT package \
            installed.
        See https://pythonhosted.org/sense-hat/ for more information.
        """
        try:
            # pylint: disable=import-outside-toplevel
            from sense_hat import SenseHat
        except ModuleNotFoundError as parent_exception:
            raise ControllerError("SenseHAT controller was initialized without"
                                  " pre-requisites.") from parent_exception
        self.sense = SenseHat()
        self.sense.set_imu_config(True, True, True)


class Generic:
    """
    Perfectly Generic Object, colored a perfectly generic green.

    Generic controller class, with no special attributes. \
        Exists as a placeholder.
    """
