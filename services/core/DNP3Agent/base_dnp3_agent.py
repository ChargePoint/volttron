# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2018, SLAC / Kisensum.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor SLAC, nor Kisensum, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# SLAC, or Kisensum. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
# }}}

import json
import logging
import os
import re

from pydnp3 import opendnp3

from volttron.platform.agent import utils
from volttron.platform.messaging import headers
from volttron.platform.vip.agent import Agent, RPC

from outstation import DNP3Outstation

DEFAULT_POINT_TOPIC = 'dnp3/point'
DEFAULT_LOCAL_IP = "0.0.0.0"
DEFAULT_PORT = 20000

# PointDefinition.fcodes values:
DIRECT_OPERATE = 'direct_operate'       # This is actually DIRECT OPERATE / RESPONSE
SELECT = 'select'                       # This is actually SELECT / RESPONSE
OPERATE = 'operate'                     # This is actually OPERATE / RESPONSE

# Some PointDefinition.point_type values:
POINT_TYPE_ANALOG_INPUT = 'Analog Input'
POINT_TYPE_ANALOG_OUTPUT = 'Analog Output'
POINT_TYPE_BINARY_INPUT = 'Binary Input'
POINT_TYPE_BINARY_OUTPUT = 'Binary Output'

# Default event group and variation for each of these types, in case they weren't spec'd for a point in the data file.
EVENT_DEFAULTS_BY_POINT_TYPE = {
    POINT_TYPE_ANALOG_INPUT: {"group": 32, "variation": 3},
    POINT_TYPE_ANALOG_OUTPUT: {"group": 42, "variation": 3},
    POINT_TYPE_BINARY_INPUT: {"group": 2, "variation": 1},
    POINT_TYPE_BINARY_OUTPUT: {"group": 11, "variation": 1}
}

EVENT_CLASSES = {
    1: opendnp3.PointClass.Class1,
    2: opendnp3.PointClass.Class2,
    3: opendnp3.PointClass.Class3
}

GROUP_AND_VARIATIONS = {
    '1.1': opendnp3.StaticBinaryVariation.Group1Var1,
    '1.2': opendnp3.StaticBinaryVariation.Group1Var2,
    '2.1': opendnp3.EventBinaryVariation.Group2Var1,
    '2.2': opendnp3.EventBinaryVariation.Group2Var2,
    '2.3': opendnp3.EventBinaryVariation.Group2Var3,
    '3.2': opendnp3.StaticDoubleBinaryVariation.Group3Var2,
    '4.1': opendnp3.EventDoubleBinaryVariation.Group4Var1,
    '4.2': opendnp3.EventDoubleBinaryVariation.Group4Var2,
    '4.3': opendnp3.EventDoubleBinaryVariation.Group4Var3,
    '10.2': opendnp3.StaticBinaryOutputStatusVariation.Group10Var2,
    '11.1': opendnp3.EventBinaryOutputStatusVariation.Group11Var1,
    '11.2': opendnp3.EventBinaryOutputStatusVariation.Group11Var2,
    '20.1': opendnp3.StaticCounterVariation.Group20Var1,
    '20.2': opendnp3.StaticCounterVariation.Group20Var2,
    '20.5': opendnp3.StaticCounterVariation.Group20Var5,
    '20.6': opendnp3.StaticCounterVariation.Group20Var6,
    '21.1': opendnp3.StaticFrozenCounterVariation.Group21Var1,
    '21.2': opendnp3.StaticFrozenCounterVariation.Group21Var2,
    '21.5': opendnp3.StaticFrozenCounterVariation.Group21Var5,
    '21.6': opendnp3.StaticFrozenCounterVariation.Group21Var6,
    '21.9': opendnp3.StaticFrozenCounterVariation.Group21Var9,
    '21.10': opendnp3.StaticFrozenCounterVariation.Group21Var10,
    '22.1': opendnp3.EventCounterVariation.Group22Var1,
    '22.2': opendnp3.EventCounterVariation.Group22Var2,
    '22.5': opendnp3.EventCounterVariation.Group22Var5,
    '22.6': opendnp3.EventCounterVariation.Group22Var6,
    '23.1': opendnp3.EventFrozenCounterVariation.Group23Var1,
    '23.2': opendnp3.EventFrozenCounterVariation.Group23Var2,
    '23.5': opendnp3.EventFrozenCounterVariation.Group23Var5,
    '23.6': opendnp3.EventFrozenCounterVariation.Group23Var6,
    '30.1': opendnp3.StaticAnalogVariation.Group30Var1,
    '30.2': opendnp3.StaticAnalogVariation.Group30Var2,
    '30.3': opendnp3.StaticAnalogVariation.Group30Var3,
    '30.4': opendnp3.StaticAnalogVariation.Group30Var4,
    '30.5': opendnp3.StaticAnalogVariation.Group30Var5,
    '30.6': opendnp3.StaticAnalogVariation.Group30Var6,
    '32.1': opendnp3.EventAnalogVariation.Group32Var1,
    '32.2': opendnp3.EventAnalogVariation.Group32Var2,
    '32.3': opendnp3.EventAnalogVariation.Group32Var3,
    '32.4': opendnp3.EventAnalogVariation.Group32Var4,
    '32.5': opendnp3.EventAnalogVariation.Group32Var5,
    '32.6': opendnp3.EventAnalogVariation.Group32Var6,
    '32.7': opendnp3.EventAnalogVariation.Group32Var7,
    '32.8': opendnp3.EventAnalogVariation.Group32Var8,
    '40.1': opendnp3.StaticAnalogOutputStatusVariation.Group40Var1,
    '40.2': opendnp3.StaticAnalogOutputStatusVariation.Group40Var2,
    '40.3': opendnp3.StaticAnalogOutputStatusVariation.Group40Var3,
    '40.4': opendnp3.StaticAnalogOutputStatusVariation.Group40Var4,
    '42.1': opendnp3.EventAnalogOutputStatusVariation.Group42Var1,
    '42.2': opendnp3.EventAnalogOutputStatusVariation.Group42Var2,
    '42.3': opendnp3.EventAnalogOutputStatusVariation.Group42Var3,
    '42.4': opendnp3.EventAnalogOutputStatusVariation.Group42Var4,
    '42.5': opendnp3.EventAnalogOutputStatusVariation.Group42Var5,
    '42.6': opendnp3.EventAnalogOutputStatusVariation.Group42Var6,
    '42.7': opendnp3.EventAnalogOutputStatusVariation.Group42Var7,
    '42.8': opendnp3.EventAnalogOutputStatusVariation.Group42Var8,
    '50.4': opendnp3.StaticTimeAndIntervalVariation.Group50Var4,
    '121.1': opendnp3.StaticSecurityStatVariation.Group121Var1,
    '122.1': opendnp3.EventSecurityStatVariation.Group122Var1,
    '122.2': opendnp3.EventSecurityStatVariation.Group122Var2
}

POINT_TYPES_BY_GROUP = {
    # Single-Bit Binary: See DNP3 spec, Section A.2-A.5 and Table 11-17
    1: POINT_TYPE_BINARY_INPUT,         # Binary Input (static): Reporting the present value of a single-bit binary object
    2: POINT_TYPE_BINARY_INPUT,         # Binary Input Event: Reporting single-bit binary input events and flag bit changes
    # Double-Bit Binary: See DNP3 spec, Section A.4 and Table 11-15
    3: 'Double Bit Binary',             # Double-Bit Binary Input (static): Reporting present state value
    4: 'Double Bit Binary',             # Double-Bit Binary Input Event: Reporting double-bit binary input events and flag bit changes
    # Binary Output: See DNP3 spec, Section A.6-A.9 and Table 11-12
    10: POINT_TYPE_BINARY_OUTPUT,       # Binary Output (static): Reporting the present output status
    11: POINT_TYPE_BINARY_OUTPUT,       # Binary Output Event: Reporting changes to the output status or flag bits
    12: POINT_TYPE_BINARY_OUTPUT,       # Binary Output Command: Issuing control commands
    13: POINT_TYPE_BINARY_OUTPUT,       # Binary Output Command Event: Reporting control command was issued regardless of its source
    # Counter: See DNP3 spec, Section A.10-A.13 and Table 11-13
    20: 'Counter',                      # Counter: Reporting the count value
    21: 'Counter',                      # Frozen Counter: Reporting the frozen count value or changed flag bits
    22: 'Counter',                      # Counter Event: Reporting counter events
    23: 'Counter',                      # Frozen Counter Event: Reporting frozen counter events
    # Analog Input: See DNP3 spec, Section A.14-A.18 and Table 11-9
    30: POINT_TYPE_ANALOG_INPUT,        # Analog Input (static): Reporting the present value
    31: POINT_TYPE_ANALOG_INPUT,        # Frozen Analog Input (static): Reporting the frozen value
    32: POINT_TYPE_ANALOG_INPUT,        # Analog Input Event: Reporting analog input events or changes to the flag bits
    33: POINT_TYPE_ANALOG_INPUT,        # Frozen Analog Input Event: Reporting frozen analog input events
    34: POINT_TYPE_ANALOG_INPUT,        # Analog Input Reporting Deadband (static): Reading and writing analog deadband values
    # Analog Output: See DNP3 spec, Section A.19-A.22 and Table 11-10
    40: POINT_TYPE_ANALOG_OUTPUT,       # Analog Output Status (static): Reporting present value of analog outputs
    41: POINT_TYPE_ANALOG_OUTPUT,       # Analog Output (command): Controlling analog output values
    42: POINT_TYPE_ANALOG_OUTPUT,       # Analog Output Event: Reporting changes to the analog output or flag bits
    43: POINT_TYPE_ANALOG_OUTPUT,       # Analog Output Command Event: Reporting output points being commanded from any source
    # Time and Date: See DNP3 spec, Section A.23-A.25
    50: 'Time And Date',
    51: 'Time And Date',                # Time and Date Common Time-of-Occurrence
    52: 'Time And Date',                # Time Delay
    # Class Objects: See DNP3 spec, Section A.26
    60: 'Class Objects',
    # File-Control: See DNP3 spec, Section A.27
    70: 'File-Control',
    # Information Objects: See DNP3 spec, Section A.28-A.31
    80: 'Internal Indications',
    81: 'Device Storage',
    82: 'Device Profile',
    83: 'Data Set Registration',
    # Data Set Objects: See DNP3 spec, Section A.32-A.35
    85: 'Data Set Prototype',
    86: 'Data Set Descriptor',
    87: 'Data Set',
    88: 'Data Set Event',
    # Application & Status of Operation Information Objects: See DNP3 spec, Section A.36-A.37
    90: 'Application',
    91: 'Status of Requested Operation',
    # Floating-Point (Obsolete): See DNP3 spec, Section A.38
    100: 'Floating-Point',
    # Numeric Static Objects: See DNP3 spec, Section A.39-A.40
    101: 'BCD',                         # Device-dependent values in Binary-Coded Decimal form (Table 11-11)
    102: 'Unsigned Integer',
    # Octet String: See DNP3 spec, Section A.41-A.42 and Table 11-16
    110: 'Octet String',                # To convey the present value
    111: 'Octet String',                # Reporting an octet string event
    # Virtual Terminal: See DNP3 spec, Section A.43-A.44 and Table 11-18
    112: 'Virtual Terminal',            # Conveying data to the command interpreter at the outstation
    113: 'Virtual Terminal',            # Conveying data from the command interpreter at the outstation
    # Security: See DNP3 spec, Section A.45
    120: 'Authentication',
    # Security Statistic: See DNP3 spec, Section A.46-A.47 and Table 11-20
    121: 'Security Statistic',          # Reporting the current value of the statistics
    122: 'Security Statistic'           # Reporting changes to the statistics
}

utils.setup_logging()
_log = logging.getLogger(__name__)


class BaseDNP3Agent(Agent):
    """
        DNP3Agent is a VOLTTRON agent that handles DNP3 outstation communications.

        DNP3Agent models a DNP3 outstation, communicating with a DNP3 master.

        For further information about this agent and DNP3 communications, please see the VOLTTRON
        DNP3 specification, located in VOLTTRON readthedocs
        under http://volttron.readthedocs.io/en/develop/specifications/dnp3_agent.html.

        This agent can be installed from a command-line shell as follows:
            export VOLTTRON_ROOT=<your volttron install directory>
            export DNP3_ROOT=$VOLTTRON_ROOT/services/core/DNP3Agent
            cd $VOLTTRON_ROOT
            python scripts/install-agent.py -s $DNP3_ROOT -i dnp3agent -c $DNP3_ROOT/dnp3agent.config -t dnp3agent -f
    """

    def __init__(self, point_definitions_path='', point_topic='', local_ip=None, port=None, outstation_config=None,
                 **kwargs):
        """Initialize the DNP3 agent."""
        super(BaseDNP3Agent, self).__init__(enable_web=True, **kwargs)
        self.point_definitions_path = point_definitions_path
        self.point_topic = point_topic
        self.local_ip = local_ip
        self.port = port
        self.outstation_config = outstation_config
        self.default_config = {
            'point_definitions_path': point_definitions_path,
            'point_topic': point_topic,
            'local_ip': local_ip,
            'port': port,
            'outstation_config': outstation_config,
        }
        self.application = None
        self.volttron_points = None

        self.point_definitions = None
        self._current_point_values = {}

    def _configure(self, config_name, action, contents):
        """
            Initialize/Update the DNP3Agent configuration.

            DNP3Agent configuration parameters:

            point_definitions_path: (string, required) Pathname of the JSON file containing DNP3 point definitions.
            point_topic: (string) VOLTTRON message bus topic to use when publishing DNP3 point values.
                        Default: dnp3/point.
            local_ip: (string) Outstation's host address (DNS resolved).
                        Default: 0.0.0.0.
            port: (integer) Outstation's port number - the port that the remote endpoint (Master) is listening on.
                        Default: 20000.
            outstation_config: (dictionary) Outstation configuration parameters. All are optional.
                Parameters include:
                    database_sizes: (integer) Size of each DNP3 database buffer.
                                Default: 10.
                    event_buffers: (integer) Size of the database event buffers.
                                Default: 10.
                    allow_unsolicited: (boolean) Whether to allow unsolicited requests.
                                Default: True.
                    link_local_addr: (integer) Link layer local address.
                                Default: 10.
                    link_remote_addr: (integer) Link layer remote address.
                                Default: 1.
                    log_levels: List of bit field names (OR'd together) that filter what gets logged by DNP3.
                                Default: NORMAL.
                                Possible values: ALL, ALL_APP_COMMS, ALL_COMMS, NORMAL, NOTHING.
                    threads_to_allocate: (integer) Threads to allocate in the manager's thread pool.
                                Default: 1.
        """
        config = self.default_config.copy()
        config.update(contents)
        self.point_definitions_path = config.get('point_definitions_path', '')
        self.point_topic = config.get('point_topic', DEFAULT_POINT_TOPIC)
        self.local_ip = config.get('local_ip', DEFAULT_LOCAL_IP)
        self.port = int(config.get('port', DEFAULT_PORT))
        self.outstation_config = config.get('outstation_config', {})
        _log.debug('DNP3Agent configuration parameters:')
        _log.debug('\tpoint_definitions_path={}'.format(self.point_definitions_path))
        _log.debug('\tpoint_topic={}'.format(self.point_topic))
        _log.debug('\tlocal_ip={}'.format(self.local_ip))
        _log.debug('\tport={}'.format(self.port))
        _log.debug('\toutstation_config={}'.format(self.outstation_config))
        self.point_definitions = PointDefinitions(self.point_definitions_path)
        DNP3Outstation.set_agent(self)
        self.application = DNP3Outstation(self.local_ip, self.port, self.outstation_config)

    def _get_point(self, point_name):
        """
            (Internal) Look up the most-recently-received value for a given point (no debug trace).

        @param point_name: The name of a DNP3 PointDefinition.
        @return: The (unwrapped) value of a received point.
        """
        try:
            point_def = self.point_definitions.get_point_named(point_name)
            point_type = PointDefinition.point_type_for_group(point_def.group)
            point_value = self.get_current_point_value(point_type, point_def.index)
            return point_value.unwrapped_value() if point_value else None
        except Exception as e:
            raise DNP3Exception(e.message)

    def _get_point_by_index(self, group, index):
        """
            (Internal) Look up the most-recently-received value for a given point (no debug trace).

        @param group: The group number of a DNP3 point.
        @param index: The index of a DNP3 point.
        @return: The (unwrapped) value of a received point.
        """
        try:
            point_value = self.get_current_point_value(PointDefinition.point_type_for_group(group), index)
            return point_value.unwrapped_value() if point_value else None
        except Exception as e:
            raise DNP3Exception(e.message)

    def get_current_point_value(self, point_type, index):
        """Return the most-recently-received PointValue for a given PointDefinition."""
        if point_type not in self._current_point_values:
            return None
        elif index not in self._current_point_values[point_type]:
            return None
        else:
            return self._current_point_values[point_type][index]

    def _set_point(self, point_name, value):
        """
            (Internal) Set the value of a given input point (no debug trace).

        @param point_name: The VOLTTRON point name of a DNP3 PointDefinition.
        @param value: The value to set. The value's data type must match the one in the DNP3 PointDefinition.
        """
        point_properties = self.volttron_points.get(point_name, {})
        group = point_properties.get('group', None)
        index = point_properties.get('index', None)
        point_type = PointDefinition.point_type_for_group(group)
        try:
            if point_type == POINT_TYPE_ANALOG_INPUT:
                wrapped_value = opendnp3.Analog(value)
            elif point_type == POINT_TYPE_BINARY_INPUT:
                wrapped_value = opendnp3.Binary(value)
            else:
                raise Exception('Unexpected data type for DNP3 point named {0}'.format(point_name))
            DNP3Outstation.apply_update(wrapped_value, index)
        except Exception as e:
            raise DNP3Exception(e.message)

    def process_point_value(self, command_type, command, index, op_type):
        """
            A point value was received from the Master. Process its payload.

        @param command_type: Either 'Select' or 'Operate'.
        @param command: A ControlRelayOutputBlock or else a wrapped data value (AnalogOutputInt16, etc.).
        @param index: DNP3 index of the payload's data definition.
        @param op_type: An OperateType, or None if command_type == 'Select'.
        @return: A CommandStatus value.
        """
        response = opendnp3.CommandStatus.DOWNSTREAM_FAIL
        try:
            point_value = self.point_value_for_command(command_type, command, index, op_type)
            if point_value:
                try:
                    self._process_point_value(point_value)
                    return opendnp3.CommandStatus.SUCCESS
                except Exception as ex:
                    self.discard_cached_point_value(point_value)
                    _log.error('Error processing DNP3 command: {}'.format(ex))
        except Exception as ex:
            _log.error('No DNP3 PointDefinition for command with index {}'.format(index))
        return response

    def _process_point_value(self, point_value):
        _log.debug('Received DNP3 {}'.format(point_value))
        if point_value.command_type == 'Select':
            # Perform any needed validation now, then wait for the subsequent Operate command.
            pass
        else:
            self.add_to_current_values(point_value)
            self.publish_point_value(point_value)

    def point_value_for_command(self, command_type, command, index, op_type):
        """
            A DNP3 Select or Operate was received from the master. Create and return a PointValue for its data.

        @param command_type: Either 'Select' or 'Operate'.
        @param command: A ControlRelayOutputBlock or else a wrapped data value (AnalogOutputInt16, etc.).
        @param index: DNP3 index of the payload's data definition.
        @param op_type: An OperateType, or None if command_type == 'Select'.
        @return: An instance of PointValue
        """
        function_code = command.functionCode if type(command) == opendnp3.ControlRelayOutputBlock else None
        point_type = POINT_TYPE_BINARY_OUTPUT if function_code else POINT_TYPE_ANALOG_OUTPUT
        point_def = self.point_definitions.for_point_type_and_index(point_type, index)
        if not point_def:
            raise DNP3Exception('No DNP3 PointDefinition found for point type {0} and index {1}'.format(point_type,
                                                                                                        index))
        point_value = PointValue(command_type,
                                 function_code,
                                 command.value if not function_code else None,
                                 point_def,
                                 index,
                                 op_type)
        _log.debug('Received DNP3 {}'.format(point_value))
        return point_value

    def add_to_current_values(self, value):
        """Update a dictionary that holds the most-recently-received value of each point."""
        point_type = value.point_def.point_type
        if point_type not in self._current_point_values:
            self._current_point_values[point_type] = {}
        self._current_point_values[point_type][int(value.index)] = value

    def get_point_named(self, point_name):
        return self.point_definitions.get_point_named(point_name)

    def for_point_type_and_index(self, point_type, index):
        return self.point_definitions.for_point_type_and_index(point_type, index)

    def discard_cached_point_value(self, point_value):
        """Delete a cached point value (typically occurs only if an error is being handled)."""
        try:
            point_type = point_value.point_def.point_type
            if point_type not in self._current_point_values:
                self._current_point_values[point_type] = {}
            del self._current_point_values[point_type][int(point_value.index)]
        except Exception as err:
            _log.error('Error discarding cached value {}'.format(point_value))

    def publish_point_value(self, point_value):
        """Publish a PointValue as it is received from the DNP3 Master."""
        _log.debug('Publishing DNP3 {}'.format(point_value))
        self.publish_points({point_value.name: (point_value.unwrapped_value() if point_value else None)})

    def publish_points(self, msg):
        """Publish point values to the message bus."""
        self.publish_data(self.point_topic, msg)

    def publish_data(self, topic, msg):
        """Publish a payload to the message bus."""
        self.vip.pubsub.publish(peer='pubsub',
                                topic=topic,
                                headers={headers.TIMESTAMP: utils.format_timestamp(utils.get_aware_utc_now())},
                                message=msg)


class DNP3Exception(Exception):
    """Raise exceptions that are specific to the DNP3 agent. No special exception behavior is needed at this time."""
    pass


class PointDefinitions(object):
    """In-memory repository of PointDefinitions."""

    _points = {}
    _point_variation_dict = {}
    _point_name_dict = {}

    def __init__(self, point_definitions_path=None):
        if point_definitions_path:
            file_path = os.path.expandvars(os.path.expanduser(point_definitions_path))
            self.load_points(file_path)

    def load_points(self, point_definitions_path):
        """
            Load and cache a dictionary of PointDefinitions from a json list.

            Index the dictionary by point_type and point index.
        """

        # Use a regular expression to filter comments out of the JSON configuration file's definitions.
        # See VOLTTRON platform/agent/utils.py for the source of this regular expression.
        _comment_re = re.compile(
            r'((["\'])(?:\\?.)*?\2)|(/\*.*?\*/)|((?:#|//).*?(?=\n|$))',
            re.MULTILINE | re.DOTALL)

        def _repl(match):
            """
                Replace the match group with an appropriate string.

                If the first group was matched, a quoted string was matched and should be returned unchanged.
                Otherwise a comment was matched and an empty string should be returned.
            """
            return match.group(1) or ''

        _log.debug('Loading DNP3 point definitions from {}.'.format(point_definitions_path))
        try:
            with open(point_definitions_path, 'r') as f:
                self._points = {}           # If they're already loaded, force a reload.
                # Filter comments out of the file's contents before loading it as JSON.
                filtered_file_contents = _comment_re.sub(_repl, f.read())
                json_file_contents = json.loads(filtered_file_contents)
                for element in json_file_contents:
                    point_def = PointDefinition(element)
                    if point_def.array_points is not None:
                        self._expand_array_points(point_def)
                    if self._points.get(point_def.point_type, None) is None:
                        self._points[point_def.point_type] = {}
                    point_type_dict = self._points[point_def.point_type]
                    duplicate_point = point_type_dict.get(point_def.index, None)
                    if duplicate_point:
                        error_message = 'Discarding DNP3 duplicate {0} (conflicting {1})'
                        raise DNP3Exception(error_message.format(point_def, duplicate_point))
                    else:
                        # _log.debug('Loading {}'.format(point_def))
                        point_type_dict[point_def.index] = point_def
        except Exception as err:
            raise ValueError('Problem parsing {}. No data loaded. Error={}'.format(point_definitions_path, err))
        _log.debug('Loaded {} PointDefinitions'.format(len(self.all_point_names())))

    def _expand_array_points(self, point_def):
        """Load up a separate PointDefinition for each name in the array's 'points' list."""
        for pt_offset, pt in enumerate(point_def.array_points):
            # The first point in the list is already defined as the parent point, so skip it here.
            if pt_offset > 0:
                pt_element_def = {
                    'name': pt['name'],
                    'index': point_def.index + pt_offset,
                    'group': point_def.group,
                    'variation': point_def.variation,
                    'scaling_multiplier': point_def.scaling_multiplier,
                    'units': point_def.units
                }
                array_pt = PointDefinition(pt_element_def)
                point_type_dict = self._points[array_pt.point_type]
                duplicate_point = point_type_dict.get(array_pt.index, None)
                if duplicate_point:
                    error_message = 'Discarding DNP3 duplicate {0} (conflicting {1})'
                    _log.error(error_message.format(array_pt, duplicate_point))
                else:
                    point_type_dict[array_pt.index] = array_pt

    def _points_dictionary(self):
        """Return a (cached) dictionary of PointDefinitions, indexed by point_type and point index."""
        return self._points

    def for_group_and_index(self, group, index):
        return self._points_dictionary().get(PointDefinition.point_type_for_group(group), {}).get(index, None)

    def for_point_type_and_index(self, point_type, index):
        """
            Return a PointDefinition for a given data type and index.

        @param point_type: A point type (string).
        @param index: Unique integer index of the PointDefinition to be looked up.
        @return: A PointDefinition.
        """
        return self._points_dictionary().get(point_type, {}).get(index, None)

    def _points_by_variation(self):
        """Return a (cached) dictionary of PointDefinitions, indexed by group, variation and index."""
        if not self._point_variation_dict:
            for point_type, inner_dict in self._points_dictionary().items():
                for index, point_def in inner_dict.items():
                    if self._point_variation_dict.get(point_def.group, None):
                        self._point_variation_dict[point_def.group] = {}
                    if self._point_variation_dict[point_def.group].get(point_def.variation, None):
                        self._point_variation_dict[point_def.group][point_def.variation] = {}
                    self._point_variation_dict[point_def.group][point_def.variation][index] = point_def
        return self._point_variation_dict

    def point_for_variation_and_index(self, group, variation, index):
        """Return a PointDefinition for a given group, variation and index."""
        return self._points_by_variation().get(group, {}).get(variation, {}).get(index, None)

    def points_by_name(self):
        """Return a (cached) dictionary of PointDefinitions, indexed by name."""
        if not self._point_name_dict:
            for point_type, inner_dict in self._points_dictionary().items():
                for index, point_def in inner_dict.items():
                    if self._point_name_dict.get(point_def.name, None):
                        raise ValueError('Duplicate point name: {}'.format(point_def.name))
                    self._point_name_dict[point_def.name] = point_def
        return self._point_name_dict

    def point_named(self, name):
        """Return the PointDefinition with the indicated name."""
        return self.points_by_name().get(name, None)

    def get_point_named(self, name):
        """Return the PointDefinition with the indicated name. Raise an exception if none found."""
        point_def = self.points_by_name().get(name, None)
        if point_def is None:
            raise DNP3Exception('No point named {}'.format(name))
        return point_def

    def all_points(self):
        """Return a flat list of all PointDefinitions."""
        point_list = []
        for inner_dict in self._points_dictionary().values():
            point_list.extend(inner_dict.values())
        return point_list

    def all_point_names(self):
        return self.points_by_name().keys()


class PointDefinition(object):
    """Data holder for an OpenDNP3 data element."""

    def __init__(self, element_def):
        """Initialize an instance of the PointDefinition from a dictionary of point attributes."""
        try:
            self.name = str(element_def.get('name', ''))
            self.type = element_def.get('type', None)
            self.group = element_def.get('group', None)
            self.variation = element_def.get('variation', None)
            self.index = element_def.get('index', None)
            self.description = element_def.get('description', '')
            self.scaling_multiplier = element_def.get('scaling_multiplier', 1)
            self.units = element_def.get('units', '')
            self.event_class = element_def.get('event_class', 2)
            self.event_group = element_def.get('event_group', None)
            self.event_variation = element_def.get('event_variation', None)
            self.array_points = element_def.get('array_points', None)
            self.array_times_repeated = element_def.get('array_times_repeated', None)
            self.selector_block_start = element_def.get('selector_block_start', None)
            self.selector_block_end = element_def.get('selector_block_end', None)
            self.save_on_write = element_def.get('save_on_write', None)
            self.validate_point()
        except ValueError as err:
            raise DNP3Exception('Validation error for point with json: {}'.format(element_def, err))

    def validate_point(self):
        """A PointDefinition has been created. Perform a variety of validations on it."""
        if self.type is not None and (self.type not in ['array', 'selector_block']):
            raise ValueError('Invalid type for {}'.format(self.name))
        if self.group is None:
            raise ValueError('Missing group for {}'.format(self.name))
        if self.variation is None:
            raise ValueError('Missing variation for {}'.format(self.name))
        if self.index is None:
            raise ValueError('Missing index for {}'.format(self.name))

        # Use intelligent defaults for event_group and event_variation based on data type
        if self.event_group is None:
            if self.point_type in EVENT_DEFAULTS_BY_POINT_TYPE:
                self.event_group = EVENT_DEFAULTS_BY_POINT_TYPE[self.point_type]["group"]
            else:
                raise ValueError('Missing event group for {}'.format(self.name))
        if self.event_variation is None:
            if self.point_type in EVENT_DEFAULTS_BY_POINT_TYPE:
                self.event_variation = EVENT_DEFAULTS_BY_POINT_TYPE[self.point_type]["variation"]
            else:
                raise ValueError('Missing event variation for {}'.format(self.name))

        if self.is_array:
            if self.array_points is None:
                raise ValueError('Missing array_points for array named {}'.format(self.name))
            if self.array_times_repeated is None:
                raise ValueError('Missing array_times_repeated for array named {}'.format(self.name))
        else:
            if self.array_points is not None:
                raise ValueError('array_points defined for non-array point {}'.format(self.name))
            if self.array_times_repeated is not None:
                raise ValueError('array_times_repeated defined for non-array point {}'.format(self.name))

        if self.is_selector_block:
            if self.selector_block_start is None:
                raise ValueError('Missing selector_block_end for block named {}'.format(self.name))
            if self.selector_block_end is None:
                raise ValueError('Missing selector_block_end for block named {}'.format(self.name))
            if self.selector_block_start > self.selector_block_end:
                raise ValueError('Selector block end index < start index for block named {}'.format(self.name))
            if self.save_on_write is None:
                self.save_on_write = False
        else:
            if self.selector_block_start is not None:
                raise ValueError('selector_block_start defined for non-selector-block point {}'.format(self.name))
            if self.selector_block_end is not None:
                raise ValueError('selector_block_end defined for non-selector-block point {}'.format(self.name))
            if self.save_on_write is not None:
                raise ValueError('save_on_write defined for non-selector-block point {}'.format(self.name))

    def as_json(self):
        """Return a json description of the PointDefinition."""
        point_json = {
            "name": self.name,
            "group": self.group,
            "variation": self.variation,
            "index": self.index,
            "scaling_multiplier": self.scaling_multiplier,
            "event_class": self.event_class
        }
        if self.type is not None:
            point_json["type"] = self.type
        if self.description is not None:
            point_json["description"] = self.description
        if self.units is not None:
            point_json["units"] = self.units
        if self.event_group is not None:
            point_json["event_group"] = self.event_group
        if self.event_variation is not None:
            point_json["event_variation"] = self.event_variation
        # array_points has been excluded because it's not a simple data type. Is it needed in the json?
        # if self.array_points is not None:
        #     point_json["array_points"] = self.array_points
        if self.array_times_repeated is not None:
            point_json["array_times_repeated"] = self.array_times_repeated
        if self.selector_block_start is not None:
            point_json["selector_block_start"] = self.selector_block_start
        if self.selector_block_end is not None:
            point_json["selector_block_end"] = self.selector_block_end
        if self.save_on_write is not None:
            point_json["save_on_write"] = self.save_on_write
        return point_json

    def __str__(self):
        """Return a string description of the PointDefinition."""
        try:
            return 'PointDefinition {0} ({1}, index={2}, type={3})'.format(self.name,
                                                                           self.group_and_variation,
                                                                           self.index,
                                                                           self.point_type)
        except UnicodeEncodeError as err:
            _log.error('Unable to convert point definition to string, err = {}'.format(err))
            return ''

    @property
    def group_and_variation(self):
        """Return a string representation of the PointDefinition's group and variation."""
        return '{0}.{1}'.format(self.group, self.variation)

    @property
    def event_group_and_variation(self):
        """Return a string representation of the PointDefinition's event group and event variation."""
        return '{0}.{1}'.format(self.event_group, self.event_variation)

    @property
    def point_type(self):
        """Return the PointDefinition's point type, derived from its group (indexing is within point type)."""
        return self.point_type_for_group(self.group)

    @property
    def is_input(self):
        """Return True if the PointDefinition is a Binary or Analog input point (i.e., sent by the Outstation)."""
        return self.point_type in [POINT_TYPE_ANALOG_INPUT, POINT_TYPE_BINARY_INPUT]

    @property
    def is_output(self):
        """Return True if the PointDefinition is a Binary or Analog output point (i.e., sent by the Master)."""
        return self.point_type in [POINT_TYPE_ANALOG_OUTPUT, POINT_TYPE_BINARY_OUTPUT]

    @property
    def is_array(self):
        return self.type == 'array'

    @property
    def is_selector_block(self):
        return self.type == 'selector_block'

    @property
    def eclass(self):
        """Return the PointDefinition's event class, or the default (2) if no event class was defined for the point."""
        return EVENT_CLASSES.get(self.event_class, 2)

    @property
    def svariation(self):
        """Return the PointDefinition's group-and-variation enumerated type."""
        return GROUP_AND_VARIATIONS.get(self.group_and_variation)

    @property
    def evariation(self):
        """Return the PointDefinition's event group-and-variation enumerated type."""
        return GROUP_AND_VARIATIONS.get(self.event_group_and_variation)

    @property
    def array_last_index(self):
        """If the point starts an array, calculate and return the array's last index."""
        if self.is_array:
            return self.index + self.array_times_repeated * len(self.array_points) - 1
        else:
            return None

    @classmethod
    def point_type_for_group(cls, group):
        """Return the point type for a group value."""
        ptype = POINT_TYPES_BY_GROUP.get(group, None)
        if ptype is None:
            _log.error('No DNP3 point type found for group {}'.format(group))
        return ptype


class PointValue(object):
    """Data holder for a point value (DNP3 measurement or command) received by an outstation."""

    def __init__(self, command_type, function_code, value, point_def, index, op_type):
        """Initialize an instance of the PointValue."""
        self.when_received = utils.get_aware_utc_now()
        self.command_type = command_type
        self.function_code = function_code
        self.value = value
        self.point_def = point_def
        self.index = index          # MESA Array point indexes can differ from the indexes of their PointDefinitions.
        self.op_type = op_type

    def __str__(self):
        """Return a string description of the PointValue."""
        str_desc = 'Point value {0} ({1}, {2}.{3}, {4})'
        return str_desc.format(self.value or self.function_code,
                               self.name,
                               self.point_def.group_and_variation,
                               self.index,
                               self.command_type)

    @property
    def name(self):
        """Return the name of the PointDefinition."""
        return self.point_def.name

    @property
    def starts_array(self):
        return self.point_def.is_array and (self.index == self.point_def.index)

    def array_point_name(self, array_size):
        # For MESA Array PointValues. Return a unique name that combines Array name with point name.
        return '{}: [{}] {}'.format(self.point_def.name,
                                    self.array_element(array_size),
                                    self.point_def.array_points[self.array_points_index(array_size)].get('name'), '')

    def array_element(self, array_size):
        """For MESA Array PointValues. Return the index into the PointDefinition's array_points."""
        return (self.index - self.point_def.index) // array_size

    def array_points_index(self, array_size):
        """For MESA Array PointValues. Return the index into the PointDefinition's array_points."""
        return (self.index - self.point_def.index) % array_size

    def unwrapped_value(self):
        """Unwrap the point's value, returning the sample data type (e.g. an integer, binary, etc. instance)."""
        if self.value is None:
            # For binary commands, send True if function_code is LATCH_ON, False otherwise
            return self.function_code == opendnp3.ControlCode.LATCH_ON
        else:
            return self.value
