"""
Project KINETIC, init module.

██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗
██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝
█████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║
██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║
██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝

Made by perpetualCreations
"""

import socket
from typing import Union, Callable
from sys import exit as stop
from subprocess import call
import swbs
from kinetic import actiongroups as ActionGroups  # noqa: F401
from kinetic import components as Components  # noqa: F401
from kinetic import controllers as Controllers  # noqa: F401
from kinetic import exceptions as Exceptions  # noqa: F401


class Agent:
    """Agent class for deriving from, for custom robotic agents."""

    def __init__(self, uuid: str = "6ae2f3bd-2b55-468a-88a3-af0eeae03896",
                 uuid_is_path: bool = False):
        """
        Class initialization, creating instance variables.

        :param uuid: Agent UUID, default UUID is
            6ae2f3bd-2b55-468a-88a3-af0eeae03896
        :type uuid: str
        :param uuid_is_path: if True treats parameter uuid as path to file
            containing the agent uuid, default False
        :type uuid_is_path: bool
        :ivar self.lookup: dict, keys being commands that translate to function
            calls, defaulted to if Agent.client_listen parameter lookup is
            None, can be directly overwritten, see unionize parameter for
            Agent.client_listen to use both self.lookup and parameter lookup,
            default lookup dictionary is {"STOP": Agent.stop(self, 0),
            "UPDATE": Agent.update(), "SHUTDOWN": Agent.shutdown(self),
            "REBOOT": Agent.shutdown(self),
            "REQUEST TYPE": self.network.send("KINETIC"),
            "REQUEST UUID": self.network.send(self.uuid)}
        """
        if uuid_is_path is True:
            with open(uuid) as uuid_handle:
                self.uuid = uuid_handle.read()
        else:
            self.uuid = uuid
        self.network: Union[swbs.Interface, swbs.Client, swbs.Host] = \
            swbs.Interface
        # noinspection PyUnresolvedReferences
        self.lookup = {
            "STOP": lambda: self.stop(0),
            "UPDATE": lambda: self.update(),
            "SHUTDOWN": lambda: self.shutdown(),
            "REBOOT": lambda: self.reboot(),
            "REQUEST TYPE": lambda: self.network.send("KINETIC"),
            "REQUEST UUID": lambda: self.network.send(self.uuid)}

    def network_init(self, host: str = "arbiter.local", port: int = 999,
                     key: Union[str, bytes, None] = None,
                     key_is_path: bool = False) -> None:
        """
        Built-in network initialization, when invoked, tries to connect as a \
            client to specified host controller.

        If one is not specified, tries arbiter.local as hostname.
        If connection fails, initializes self temporarily into a Host \
            instance, waiting for a controller or a plain client pointing the \
                agent to a controller.

        Client/controller should send b"CONTROLLER" or \
            b"POINT <HOSTNAME HERE>" respectively. If agent receives neither, \
                restarts socket. If signaled to be controller, re-initializes \
                    as client to controller with specified or default port.

        If signaled to another host, connects to supplied host with specified \
            or default port.

        Operations are done on port 999 (connecting to and listening on) \
            unless specified otherwise in parameters. AES is disabled by \
                default, unless the key value is specified otherwise. \
                    Is blocking if entering Host state.

        :param host: expected controller hostname, default arbiter.local
        :type host: str
        :param port: port connecting to in client mode, and listening on in
            host
        :type port: int
        :param key: if key_is_path is False, key string, otherwise path to key
            file, default False disabling AES
        :type key: Union[str, bytes, None]
        :param key_is_path: if True, key parameter is treated as path to key
            file for reading from, default False
        :type key_is_path: bool
        """
        try:
            self.network = swbs.Client(host, port, key, key_is_path)
            self.network.connect()
            return None
        except socket.error:
            self.network.close()
            self.network = swbs.Host(port, key, key_is_path=key_is_path)
            while True:
                self.network.listen()
                self.network.send("KINETIC WAITING FOR CONTROLLER")
                signal = self.network.receive()
                controller = None  # placeholder for scope
                if signal == "CONTROLLER":
                    controller = self.network.client_address[0]
                elif signal[:5] == "POINT":
                    # this prevents a dictionary switch statement,
                    # find a rewrite
                    controller = signal.split(" ")[1]
                if controller is not None:
                    self.network.disconnect()
                    self.network = swbs.Client(self.network.client_address[0],
                                               port, key, key_is_path)
                    self.network.connect()
                    return None
                else:
                    self.network.restart()

    def client_listen(self, lookup: Union[dict, None] = None,
                      no_encrypt: bool = False, unionize: bool = True) -> None:
        """
        Blocking function that listens for controller input over \
            self.network, looks up input as key with lookup dictionary, \
                executing associated function with input command.

        If command exists, replies with "OK" and if command does not exist in \
            dictionary lookup, replies with string, "KEYERROR".

        If dictionary key "HELP" does not exist in lookup, command is set to \
            send all valid commands as individual TXs, initiated with the \
                length of the command list (counting from 1).

        For the controller to receive the command list, it should first \
            receive the "OK" acknowledgement, and then the second TX \
                containing length, and start a for loop lasting the length of \
                    command list.

        If self.network is not swbs.Client, raises Exceptions.AgentError.

        :param lookup: dictionary containing commands as keys and associated
            function calls as values to be executed when given command
            (i.e {"DO THIS": lambda: somewhere.something.do()}), if None
            defaults to self.lookup, if all is None, raises
            Exceptions.AgentError, default None
        :type: Union[dict, None]
        :param no_encrypt: passed to network I/O functions send()/receive(),
            if True disables AES for network I/O operations in this function,
            otherwise if False AES encryption is enabled, default False
        :type no_encrypt: bool
        :param unionize: merge self.lookup and parameter lookup for usage as
            command dictionary if True, default True, leave as True unless
            critically needed, be sure to respect ARIA specifications
        :type unionize: bool
        """
        if isinstance(self.network, swbs.Client) is not True:
            raise Exceptions.AgentError("Instance is not in client state.")
        if lookup is None:
            lookup = self.lookup
        else:
            if isinstance(self.lookup, dict) is True and unionize is True:
                lookup.update(self.lookup)
        if isinstance(lookup, dict) is not True:
            raise Exceptions.AgentError(
                "Lookup dictionary is not a dict type.")
        while True:
            controller_input = self.network.receive(no_decrypt=no_encrypt)
            if controller_input in list(lookup.keys()):
                self.network.send("OK", no_encrypt=no_encrypt)
                lookup[controller_input]()
            else:
                if controller_input == "HELP":
                    self.network.send("OK", no_encrypt=no_encrypt)
                    self.network.send(str(len(list(lookup.keys()))))
                    for x in list(lookup.keys()):
                        self.network.send(x, no_encrypt=no_encrypt)
                else:
                    self.network.send("KEYERROR", no_encrypt=no_encrypt)

    def stop(self, status: int,
             extended_callbacks: Union[Callable, None] = None,
             callback_params: tuple = ()) -> None:
        """
        Exit agent application. Execute optional supplied function parameter.

        :param status: exit status
        :type status: int
        :param extended_callbacks: function, called before exiting, specify a
            function here to be invoked, if parameter is None or not callable,
            callbacks is ignored, default None
        :type extended_callbacks: Union[Callable, None]
        :param callback_params: parameters for extended_callbacks, default
            empty tuple
        :type callback_params: tuple
        """
        if extended_callbacks is not None:
            extended_callbacks(*callback_params)
        if self.network is not None:
            self.network.disconnect()
        stop(status)

    def shutdown(self, status: int = 0,
                 extended_callbacks: Union[Callable, None] = None,
                 callback_params: tuple = (),
                 command: str = "sudo shutdown now") -> None:
        """
        Run OS-level shutdown command, default for Linux, with superuser-do.

        In addition, runs Agent.stop and shares status and extended_callbacks \
            parameters, which are both optional.

        Default exit code 0.

        :param status: exit status
        :type status: int
        :param extended_callbacks: function, called before exiting, specify a
            function here to be invoked, if parameter is None or not callable,
            callbacks is ignored, default None
        :type extended_callbacks: Union[Callable, None]
        :param callback_params: parameters for extended_callbacks, default
            empty tuple
        :type callback_params: tuple
        :param command: shutdown command called through shell, default for
            Linux
        :type command: str
        """
        call(command, shell=True)
        Agent.stop(self, status, extended_callbacks, callback_params)

    def reboot(self, status: int = 0,
               extended_callbacks: Union[Callable, None] = None,
               command: str = "sudo reboot now",
               callback_params: tuple = ()) -> None:
        """
        Run OS-level reboot command, default for Linux, with superuser-do.

        In addition, runs Agent.stop and shares status and extended_callbacks \
            parameters, which are both optional.

        Default exit code 0.

        :param status: exit status
        :type status: int
        :param extended_callbacks: function, called before exiting, specify a
            function here to be invoked, if parameter is None or not callable,
            callbacks is ignored, default None
        :type extended_callbacks: Union[Callable, None]
        :param callback_params: parameters for extended_callbacks, default
            empty tuple
        :type callback_params: tuple
        :param command: reboot command called through shell, default for
            Linux
        :type command: str
        """
        call(command, shell=True)
        Agent.stop(self, status, extended_callbacks, callback_params)

    @staticmethod
    def update(command: str = "sudo apt update && apt upgrade -y") -> None:
        """
        Run OS-level update command, default for Linux distributions using \
            the APT package manager.

        :param command: update command called through shell, default for Linux
        :type command: str
        """
        call(command, shell=True)
