"""
Project KINETIC, kinetic.Components.Sensors.USBCamera unit test, camera \
    streamer.

██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗
██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝
█████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║
██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║
██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝

Made by perpetualCreations
"""

import sys
import os

sys.path.insert(0, os.path.abspath('F://KINETIC//'))

import kinetic  # noqa: E402


class Test(kinetic.Components.Sensors.USBCamera):
    """Hardware abstraction."""

    def __init__(self):
        """Initialize base class."""
        super().__init__()


if __name__ == '__main__':
    inst = Test()
    inst.start_stream()
    inst.broadcast_stream("localhost", 999, None, debug=True)
