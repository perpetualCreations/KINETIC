Modular Robotic Control Application for Python 3
================================================
:Latest Version - |version|:

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* `Back to Projects </index.html##projects>`_

Install
-------
KINETIC is available on PyPI or as a wheel file for manual installation. Install through PIP.

.. code-block:: bash

   pip install project-kinetic

.. parsed-literal::

   wget https://github.com/perpetualCreations/kinetic/releases/download/\ |release|\ /project_kinetic-\ |release|\ -py3-none-any.whl
   pip install /path/to/wheel/file/project_kinetic-\ |release|\ -py3-none-any.whl

.. |release| replace:: |version|

Examples
--------
KINETIC contains base classes for derivative classes.
Base class include components and component controllers, that serve as software abstractions.

The usage of bases is modular, allowing for the creation of custom agents.

.. code-block:: python

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


Create custom components and controllers with the Generic classes.

.. code-block:: python

   import kinetic

   class CustomComponent(kinetic.Components.Generic):
       def __init__(self):
           super.__init__()
           # do this and that

   class CustomController(kinetic.Controllers.Generic)
       def __init__(self):
           super.__init__()
           # do this and that

See API reference for more information for individual bases.

Agent
-----
kinetic.Agent is the base class for any robotic agent.
Nest derivative component classes under the derivative agent class.
Controllers can be initialized under the __init__ function of the derivative agent, alongside component derivatives.

Comes with internal support for network initialization, connecting with an operating controller, application exit, and shutdown/reboot/update.

Components
----------
kinetic.Components contain all component bases.
These classes are abstractions for parts, and are further subdivided into Kinetics, Sensors, Interfaces, and Power.

Documentation for classes can be found in the API reference.

Hardware Controllers
--------------------
kinetic.Controllers contain all controller bases.
These classes are abstractions for hardware controllers that operate parts.
The sole controller in use is the Serial controller (which is for Arduino and Arduino-compatible boards that interface with components).

Documentation for classes can be found in the API reference.

Operating Controllers
---------------------
Operating controllers are hosts running a swbs.Host or swbs.Server instance.
Agents are to have only one main connection to a operating controller (some components can result in multiple connections, such as kinetic.Components.Sensor.USBCamera which has a video streaming function built-in).

Controllers send commands to agents, which are then interpreted with a lookup dictionary.
Dictionary keys (valid commands) are linked to function names that are invoked upon receiving a command.

Architecturally, operating controllers are to be either control servers that automate agent operation, or UI applications for a human operator to control agents.

The kinetic.Agent base has a built-in function for accepting a controller. See API reference on its usage.

Serial Endpoint
---------------
In version 1.0, there is only one hardware controller: kinetic.Controllers.Serial.
It is accepted by several components that require it upon initialization.

The intention behind the Serial controller is for it to interface with an Arduino or Arduino-compatible board over serial.
The board would then be further connected to actual hardware components. This abstracts low-level complexity away.
Whether this is helpful or only sure to cause confusion is debatable.

The custom serial protocol involves a 64 byte accumulator, and the line-feed character.
The serial endpoint (Arduino or Arduino-compatible board) listens for bytes, one byte at a time.
Received bytes are sequentially dumped to the accumulator character array.
When the endpoint receives a line-feed character (hex 0x0A), the accumulator is compared against a set of valid command strings through if conditionals.
After all conditionals have been processed, the array is cleared with memset, and the cycle starts again.
The standard baudrate is 9600.

The code for the serial endpoint can be generated with kinetic.generate. See section below, Generation, for more information.
The auto-generator command is also a valid point for reverse engineering the serial protocol further, in case the brief explanation is insufficient.

As you may have noticed, the serial endpoint accepts a limited set of strings as commands.
The Serial controller, or more specifically, the components using the Serial controller, since the controller only handles transmitting and receiving, needs to know the commands and their associated actions ahead of time.
And so, components using a Serial controller require a keymap, a dictionary that accepts keys being expected actions (i.e COLLECT, FORWARD, BRAKE) which then reference the command string.

Generation
----------
KINETIC comes with an automatic serial endpoint generation tool, kinetic.generate.

.. code-block:: bash

    python3 -m kinetic.generate <path to config>

The path-to-config should go to a configuration file structured as such.

.. code-block::

    [path]
    # script_path should direct to python module of agent class
    script_path = F://KINETIC//tests//testbot.py
    # output_path should be the directory that the generated endpoint code and command dictionaries are dumped to
    output_path = F://KINETIC//tests//

    [class]
    # name of agent class deriving from Kinetic.Agent
    agent_class = TestBot

As the comments specify, the script_path under section path should go to the Python file of the agent program.
output_path also under path should go to the directory where the generated .cpp code and JSON keymaps should be written to.
the agent_class field under class should be the name of the agent derivative class in the Python file.

The script imports the agent class from the file, through sys.path black magic and an exec function call (don't worry, it's probably safe).
It will then parse through the class for nested component derivative classes.

Notice about kinetic.Components.Kinetics.Motor,
    The generation tool will produce code dynamically for motor instances, in reference to whether speed and direction control is enabled or not.
    To specify whether speed and direction control is enabled or disabled, please specify **class** variables "speed" and "direction" with booleans True or False.
    This is different from the built-in **instance** variables "is_pwm_enabled" and "is_direction_enabled".

Notice about kinetic.Components.Generic,
    Please add a **class variable** named "generate_ignore" and assign a boolean to it, for whether if you want the generation tool to ignore or interpret your component.
    If set to True, an empty command if conditional will be inserted for the component.

Component classes that use serial will receive a pin assignment (if applicable, not applicable for kinetic.Components.Sensors.VL53L0X as it uses I2C).
Pins will be assigned sequentially. They are in the orders as specified below.

- Digital PWM (used only by kinetic.Components.Kinetics.Motor for speed control if enabled) → 3, 9, 10, 11, 2, 7, 8, 12, 44, 45, 46
- Digital Non-PWM → 2, 4 to 6, 13 to 43, 47 to 53
- Analog → 0 to Infinity

If the generated runs out of digital pins for assignment, an out of index exception will be raised.
Technically, there is a (fairly limited, under 2-digit) finite number of analog pins on Arduino and Arduino-compatible boards.
Non-PWM digital pins are assigned to kinetic.Components.Kinetics.Motor instances for direction (if enabled) and brake control, and kinetic.Components.Power.Switch instances.
Analog pins are assigned to kinetic.Components.Power.VoltageSensor instances.

The script will then generate the rest of the code structure, and statements for each component, including setting pinMode, creating commands and command logic, and then write the keymap and generated script to the output path specified.

Please review the pin assignments and rest of generated code. **You are required to do so if you included Generic components in your agent**.

Use whatever editor (vetted for PlatformIO and the Arduino IDE) to upload. Requires the Arduino standard library (including Wire) and the VL53L0X_ library if using the VL53L0X sensor, to compile and build.

.. _VL53L0X: https://github.com/pololu/vl53l0x-arduino/

KINETIC API
===========

API
---
Details API structures under parent kinetic.* and their usage.
kinetic.generate is intended to be used as a script! See section above, Generation.

Agent
-----
.. autoclass:: kinetic.Agent
   :special-members: __init__
   :members:

Components
----------
.. autoclass:: kinetic.Components
   :special-members: __init__
   :members:

Controllers
-----------
.. autoclass:: kinetic.Controllers
   :special-members: __init__
   :members:

Action Groups
-------------
.. autoclass:: kinetic.ActionGroups
   :special-members: __init__
   :members:

Exceptions
----------
.. autoclass:: kinetic.Exceptions
   :members:
