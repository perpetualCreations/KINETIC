"""
██╗  ██╗██╗███╗   ██╗███████╗████████╗██╗ ██████╗
██║ ██╔╝██║████╗  ██║██╔════╝╚══██╔══╝██║██╔════╝
█████╔╝ ██║██╔██╗ ██║█████╗     ██║   ██║██║
██╔═██╗ ██║██║╚██╗██║██╔══╝     ██║   ██║██║
██║  ██╗██║██║ ╚████║███████╗   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝ ╚═════╝

Project KINETIC
Made by perpetualCreations

generate.py module, generates serial endpoints from given components.

*Do you feel nostalgic, looking at something not riddled with class structures and decorators?*
*Do you remember how we all started, at the root of this world?*
*The days where we used global statements in place of instance variables.*
*It is only right for us to finish what you began.*
*The cursor is awaiting your next input.*
*Press any key to continue. I am waiting.*
*-X*
"""

# Imports
from time import time

init_time = time()

import kinetic
import argparse
import inspect
import configparser
from os.path import split, splitext
from sys import path
from importlib import import_module
from random import randint

# Argument Configuration
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("configpath", help = "Path to generation configuration.", type = str)
argument_parser.parse_args()

# Parameter Retrieval
configuration_parser = configparser.ConfigParser()
configuration_parser.read(argument_parser.configpath)

# Initial Preparation of End-User Agent Module
path.insert(0, split(configuration_parser["path"]["script_path"])[0])
target = import_module(splitext(split(configuration_parser["path"]["script_path"])[1])[0])

# Defining Script Variables
components = [] # empty list to be appended to by component indexing
components_set = [] # components list but elements only contain the bases, and contain only one of each type
components_valid = [kinetic.Components.Kinetics.Motor,
                    kinetic.Components.Sensors.VL53L0X,
                    kinetic.Components.Power.VoltageSensor,
                    kinetic.Components.Power.Switch,
                    kinetic.Components.Generic
                    ] # list of valid component classes that have serial endpoint as a valid controller
                      # this is a kluge, and could be automated, but I want to get a commit done by today
pwm_pin_reference = [3, 9, 10, 11, 2, 7, 8, 12, 44, 45, 46] # 3-11 -> Uno/Nano/Mini, 2-12 and 44-46 -> Extended Mega
normal_digital_pin_reference = [2]                                                            # 0, 1 not included for being TX/RX pins
normal_digital_pin_reference += list(range(4, 7)) + list(range(13, 44)) + list(range(47, 54)) # PWM 5, 6, 4, 13 are treated as normal digital pins since they have a irregular frequency of 980 Hz
pin_index = {"PWM":0, "DIGITAL":0, "ANALOG":0} # integer variables that progress the index head with every assignment
                                               # could be upgraded to a more elegant solution
generic_index = 0

# Component Collection of End-User Agent Module
for head in inspect.getmembers(target):
    if head[0] == configuration_parser["class"]["agent_class"]:
        for neck in inspect.getmembers(head[1]):
            if neck[1].__bases__[0] in components_valid:
                components.append({"ORIGIN":neck[1], "COMPONENT":neck[1].__bases__[0]})
                components_set.append(neck[1].__bases__[0])
        break

if not components: raise Exception("Could not find Agent/Component inherited classes.")

components_set.sort()

# Define Filtering Function
def mono_type_component_filter(component_type: object) -> list:
    """
    Filters component list for a single component type in components_valid.
    Returns all dictionary elements with the given component type as a list.

    :param component_type: kinetic.Components.*, component type to filter for
    :return: list, filtered components, can be empty if no component exists of type
    """
    result = [] # appended to for each valid element
    for items in components:
        if items["COMPONENT"] == component_type: result.append(items)
    return result

# Pin Assignment
motors = []         # thanks to Python scope referencing, edits made to elements in the list returned by the filter function are not applied to the main component list.
voltage_sensors = [] # solution? more lists.
switches = []         # these get appended to with the new dictionary entries containing pin assignments
for motor in mono_type_component_filter(kinetic.Components.Kinetics.Motor):
    if motor["ORIGIN"].is_pwm_enabled is True:
        motor.update({"PWM":pwm_pin_reference[pin_index["PWM"]]})
        pin_index["PWM"] += 1
    else: motor.update({"PWM":None})
    if motor["ORIGIN"].is_direction_enabled is True:
        motor.update({"DIR":normal_digital_pin_reference[pin_index["DIGITAL"]]})
        pin_index["DIGITAL"] += 1
    else: motor.update({"DIR":None})
    motor.update({"BRAKE":normal_digital_pin_reference[pin_index["DIGITAL"]]})
    pin_index["DIGITAL"] += 1
    motors.append(motor)
for voltage_sensor in mono_type_component_filter(kinetic.Components.Power.VoltageSensor):
    voltage_sensor.update({"COLLECT":pin_index["ANALOG"]})
    pin_index["ANALOG"] += 1
    voltage_sensors.append(voltage_sensor)
for switch in mono_type_component_filter(kinetic.Components.Power.Switch):
    switch.update({"CONTROL":normal_digital_pin_reference[pin_index["DIGITAL"]]})
    pin_index["DIGITAL"] += 1

# Write Script from Preliminary Details
with open("serial_endpoint_" + str(randint(1, 9999)) + ".cpp", "w") as script_export:
    script = """// KINETIC Serial Endpoint Code Generation
// Auto-Generated

// See documentation on pinouts and additional information.
"""

    if input("Using the stock Arduino IDE to upload? [y/n]: ").lower() is "n":
        script += """
#include <Arduino.h>
"""

    if kinetic.Components.Sensors.VL53L0X in components_set:
        script += """
#include <Wire.h>
#include <VL53L0X.h>
"""

    for vl53l0x_sensor in mono_type_component_filter(kinetic.Components.Sensors.VL53L0X): script += "\nVL53L0X " + vl53l0x_sensor["ORIGIN"].__name__ + ";"

    script += """
int incomingData;
int accumulatorIndex = 0;
char accumulator[64];
"""

    for motor in motors:
        if motor["PWM"] is not None: script += "\nbool motorIsReadingSpeed" + motor["ORIGIN"].__name__ + " = false;"

    if kinetic.Components.Power.VoltageSensor in components_set:
        script += """
static float voltage_get(int pin) {
    float raw = analogRead(pin);
    return ((raw * 5.0000000) / 1024.000000) / (7.50/37.50);
}
"""

    if kinetic.Components.Sensors.VL53L0X in components_set:
        script += """
static distance_dump(VL53L0X sensor) {
    Serial.print(sensor.readRangeSingleMillimeters());
    if (sensor.timeoutOccurred()) {
        Serial.write("TIMEOUT");
    }
    Serial.write("\n");
}
"""

    script += """
void setup() {
    Serial.begin(9600);
"""

    for motor in motors:
        if motor["PWM"] is not None: script += "\n    pinMode(" + str(motor["PWM"]) + ", OUTPUT); // PWM CONTROL FOR " + motor["ORIGIN"].__name__
        if motor["DIR"] is not None: script += "\n    pinMode(" + str(motor["DIR"]) + ", OUTPUT); // DIRECTION CONTROL FOR " + motor["ORIGIN"].__name__
        script += "\n    pinMode(" + str(motor["BRAKE"]) + ", OUTPUT); // BRAKE CONTROL FOR " + motor["ORIGIN"].__name__

    for switch in switches: script += "\n    pinMode(" + str(switch["CONTROL"]) + ", OUTPUT); // SWITCH CONTROL FOR " + switch["ORIGIN"].__name__

    for vl53l0x_sensor in mono_type_component_filter(kinetic.Components.Sensors.VL53L0X):
        script += "\n" + vl53l0x_sensor["ORIGIN"].__name__ + ".setTimeout(500);"
        script += "\n" + vl53l0x_sensor["ORIGIN"].__name__ + ".init();"

    script += "\n}\n"

    script += """
void loop() {
"""

    # TODO reimplement voltage sensor checks on init for battery

    script += """
    if (Serial.available() > 0) {

        incomingData = Serial.read();

        if (incomingData == 0x0A) { // 0x0A is the decimal code for a newline character, when it's received, the accumulator is dumped and evaluated
            accumulatorIndex = 0; // reset accumulator write index"""

    # prepare yourselves for some **brain damage**!!!
    # problems:
    # 1. component generation is depressing
    # 2. component generation is depressing
    # 3. component generation is depressing
    # 4. also haha if statement spam go brr
    # what could be done instead:
    # 1. load commands as templates from file, use Jinja to apply variables to template
    # 2. use switch statements in C++ code

    for voltage_sensor in voltage_sensors: # TODO fix voltage decimal length
        script += '''\n            if (strcmp(accumulator, "''' + "VOLTAGE_SENSOR_COLLECT " + voltage_sensor["ORIGIN"].__name__ + '''") == 0) {'''
        script +=   "\n                static char converted_voltage[5];"
        script +=   "\n                dtostrf(voltage_get(" + str(voltage_sensor["COLLECT"]) + "), 5, 3, converted_voltage);"
        script +=   "\n                Serial.write(converted_voltage);"
        script +=   "\n                Serial.write(\\n);"
        script +=   "\n            }"

    for switch in switches:
        script += '''\n            if (strcmp(accumulator, "''' + "SWITCH_OPEN " + switch["ORIGIN"].__name__ + '''") == 0) {'''
        script +=   "\n                digitalWrite(" + str(switch["CONTROL"]) + ", LOW);"
        script +=   "\n            }"
        script += '''\n            if (strcmp(accumulator, "''' + "SWITCH_CLOSE " + switch["ORIGIN"].__name__ + '''") == 0) {'''
        script +=   "\n                digitalWrite(" + str(switch["CONTROL"]) + ", HIGH);"
        script +=   "\n            }"

    for motor in motors:
        script += '''\n            if (strcmp(accumulator, "''' + "MOTOR_BRAKE_HOLD " + motor["ORIGIN"].__name__ + '''") == 0) {'''
        script +=   "\n                digitalWrite(" + str(motor["BRAKE"]) + ", HIGH);"
        script +=   "\n            }"
        script += '''\n            if (strcmp(accumulator, "''' + "MOTOR_BRAKE_RELEASE " + motor["ORIGIN"].__name__ + '''") == 0) {'''
        script +=   "\n                digitalWrite(" + str(motor["BRAKE"]) + ", LOW);"
        script +=   "\n            }"
        if motor["DIR"] is not None:
            script += '''\n            if (strcmp(accumulator, "''' + "MOTOR_FORWARD " + motor["ORIGIN"].__name__ + '''") == 0) {'''
            script +=   "\n                digitalWrite(" + str(motor["DIR"]) + ", HIGH);"
            script +=   "\n            }"
            script += '''\n            if (strcmp(accumulator, "''' + "MOTOR_BACKWARD " + motor["ORIGIN"].__name__ + '''") == 0) {'''
            script +=   "\n                digitalWrite(" + str(motor["DIR"]) + ", LOW);"
            script +=   "\n            }"
        if motor["PWM"] is not None:
            script += '''\n            if (strcmp(accumulator, "''' + "MOTOR_SPEED " + motor["ORIGIN"].__name__ + '''") == 0) {'''
            script +=   "\n                motorIsReadingSpeed" + motor["ORIGIN"].__name__ + " = true;"
            script +=   "\n            }"
            script +=   "\n            if (motorIsReadingSpeed" + motor["ORIGIN"].__name__ + " == true) {"
            script +=   "\n                analogWrite(" + str(motor["PWM"]) + ", atoi(accumulator));"
            script +=   "\n                motorIsReadingSpeed" + motor["ORIGIN"].__name__ + " = false;"
            script +=   "\n            }"

    for vl53l0x_sensor in mono_type_component_filter(kinetic.Components.Sensors.VL53L0X):
        script += '''\n            if (strcmp(accumulator, "''' + "VL53L0X_COLLECT " + vl53l0x_sensor["ORIGIN"].__name__ + '''") == 0) {'''
        script +=   "\n                distance_dump(" + vl53l0x_sensor["ORIGIN"].__name__ + ");"
        script +=   "\n            }"

    script += """

            memset(accumulator, 0, sizeof(accumulator)); // clears array.
        }
        else {
            if (accumulatorIndex <= 63) {
                accumulator[accumulatorIndex] = incomingData;
                accumulatorIndex += 1;
            }
        }
    }
}
    """
    script_export.write(script)
pass

print("Done, task completed in ", time() - init_time, " seconds.")
