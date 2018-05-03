# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2018, eightminuteenergy / Kisensum.
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
# Neither eightminuteenergy nor Kisensum, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by eightminuteenergy or Kisensum.
# }}}
import argparse
import logging
import os
import sys
import yaml

from pydnp3 import opendnp3

from volttron.platform.agent import utils
from volttron.platform.vip.agent import RPC

from services.core.DNP3Agent.base_dnp3_agent import BaseDNP3Agent, DNP3Exception
from services.core.DNP3Agent.base_dnp3_agent import PointDefinitions, PointDefinition, PointValue
from services.core.DNP3Agent.base_dnp3_agent import POINT_TYPE_ANALOG_INPUT, POINT_TYPE_ANALOG_OUTPUT
from services.core.DNP3Agent.base_dnp3_agent import POINT_TYPE_BINARY_INPUT, POINT_TYPE_BINARY_OUTPUT
from services.core.DNP3Agent.base_dnp3_agent import DEFAULT_LOCAL_IP, DEFAULT_PORT
from services.core.DNP3Agent.outstation import DNP3Outstation

DEFAULT_POINT_TOPIC = 'mesa/point'
DEFAULT_FUNCTION_TOPIC = 'mesa/function'
DEFAULT_OUTSTATION_STATUS_TOPIC = 'mesa/outstation_status'

# Values of StepDefinition.optional
OPTIONAL = "O"
MANDATORY = "M"
CONDITIONAL = "C"
ALL_OMC = [OPTIONAL, MANDATORY, CONDITIONAL]

# Values of the elements of StepDefinition.fcodes:
DIRECT_OPERATE = 'direct_operate'       # This is actually DIRECT OPERATE / RESPONSE
SELECT = 'select'                       # This is actually SELECT / RESPONSE
OPERATE = 'operate'                     # This is actually OPERATE / RESPONSE

# Values of StepDefinition.action:
ACTION_ECHO = 'echo'
ACTION_PUBLISH = 'publish'
ACTION_ECHO_AND_PUBLISH = 'echo_and_publish'
ACTION_PUBLISH_AND_RESPOND = 'publish_and_respond'
ACTION_NONE = 'none'

__version__ = '1.0'

utils.setup_logging()
_log = logging.getLogger(__name__)


class MesaAgent(BaseDNP3Agent):
    """
        MesaAgent is a VOLTTRON agent that handles MESA-ESS DNP3 outstation communications.

        MesaAgent models a DNP3 outstation, communicating with a DNP3 master.

        For further information about this agent, MESA-ESS, and DNP3 communications, please
        see the VOLTTRON DNP3 specification, located in VOLTTRON readthedocs
        under http://volttron.readthedocs.io/en/develop/specifications/dnp3_agent.html,

        and TBD... for MESA-ESS information...

        This agent can be installed from a command-line shell as follows:
            export VOLTTRON_ROOT=<your volttron install directory>
            export MESA_ROOT=$VOLTTRON_ROOT/services/core/MesaAgent
            cd $VOLTTRON_ROOT
            python scripts/install-agent.py -s $MESA_ROOT -i mesaagent -c $MESA_ROOT/mesaagent.config -t mesaagent -f
    """

    def __init__(self, point_definitions_path='', point_topic='', local_ip=None, port=None, outstation_config=None,
                 function_definitions_path='', function_topic='', outstation_status_topic='', **kwargs):
        """Initialize the MESA agent."""
        super(MesaAgent, self).__init__(**kwargs)
        self.function_definitions_path = function_definitions_path
        self.function_topic = function_topic
        self.outstation_status_topic = outstation_status_topic
        self.default_config = {
            'point_definitions_path': point_definitions_path,
            'point_topic': point_topic,
            'local_ip': local_ip,
            'port': port,
            'outstation_config': outstation_config,
            'function_definitions_path': function_definitions_path,
            'function_topic': function_topic,
            'outstation_status_topic': outstation_status_topic
        }
        self.vip.config.set_default('config', self.default_config)
        self.vip.config.subscribe(self._configure, actions=['NEW', 'UPDATE'], pattern='config')

        self.function_definitions = None
        self._current_func = None
        self._current_array = None
        self._current_selector_block = None
        self._selector_blocks = {}

    def _configure(self, config_name, action, contents):
        """
            Initialize/Update the MesaAgent configuration.

            MesaAgent configuration parameters:

            point_definitions_path: (string, required) Pathname of the JSON file containing DNP3 point definitions.
            function_definitions_path: TBD.
            point_topic: (string) Message bus topic to use when publishing DNP3 point values.
                        Default: mesa/point.
            function_topic: (string) Message bus topic to use when publishing MESA-ESS functions.
                        Default: mesa/function.
            outstation_status_topic: (string) Message bus topic to use when publishing outstation status.
                        Default: mesa/outstation_status.
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
        self.function_definitions_path = config.get('function_definitions_path', '')
        self.point_topic = config.get('point_topic', DEFAULT_POINT_TOPIC)
        self.function_topic = config.get('function_topic', DEFAULT_FUNCTION_TOPIC)
        self.outstation_status_topic = config.get('outstation_status_topic', DEFAULT_OUTSTATION_STATUS_TOPIC)
        self.local_ip = config.get('local_ip', DEFAULT_LOCAL_IP)
        self.port = int(config.get('port', DEFAULT_PORT))
        self.outstation_config = config.get('outstation_config', {})
        _log.debug('MesaAgent configuration parameters:')
        _log.debug('\tpoint_definitions_path={}'.format(self.point_definitions_path))
        _log.debug('\tfunction_definitions_path={}'.format(self.function_definitions_path))
        _log.debug('\tpoint_topic={}'.format(self.point_topic))
        _log.debug('\tfunction_topic={}'.format(self.function_topic))
        _log.debug('\toutstation_status_topic={}'.format(self.outstation_status_topic))
        _log.debug('\tlocal_ip={}'.format(self.local_ip))
        _log.debug('\tport={}'.format(self.port))
        _log.debug('\toutstation_config={}'.format(self.outstation_config))
        self.point_definitions = PointDefinitions(self.point_definitions_path)
        self.function_definitions = FunctionDefinitions(self.function_definitions_path)
        self.publish_outstation_status('starting')
        DNP3Outstation.set_agent(self)
        self.application = DNP3Outstation(self.local_ip, self.port, self.outstation_config)
        self.publish_outstation_status('running')
        # Un-comment the next line to do more detailed validation and print definition statistics.
        # validate_definitions(self.point_definitions, self.function_definitions)

    @RPC.export
    def get_point(self, point_name):
        """
            Look up the most-recently-received value for a given output point.

        @param point_name: The point name of a DNP3 PointDefinition.
        @return: The (unwrapped) value of a received point.
        """
        val = self._get_point(point_name)
        _log.debug('Getting {} point value = {}'.format(point_name, val))
        return val

    @RPC.export
    def get_point_by_index(self, group, index):
        """
            Look up the most-recently-received value for a given point.

        @param group: The group number of a DNP3 point.
        @param index: The index of a DNP3 point.
        @return: The (unwrapped) value of a received point.
        """
        _log.debug('Getting DNP3 point value for group {} and index {}'.format(group, index))
        return self._get_point_by_index(group, index)

    @RPC.export
    def get_points(self):
        """
            Look up the most-recently-received value of each configured output point.

        @return: A dictionary of point values, indexed by their point names.
        """
        if self.volttron_points is None:
            raise DNP3Exception('DNP3 points have not been configured')
        else:
            _log.debug('Getting all DNP3 configured point values')
            try:
                return {name: self._get_point(name) for name in self.volttron_points}
            except Exception as e:
                raise DNP3Exception(e.message)

    @RPC.export
    def set_point(self, point_name, value):
        """
            Set the value of a given input point.

        @param point_name: The point name of a DNP3 PointDefinition.
        @param value: The value to set. The value's data type must match the one in the DNP3 PointDefinition.
        """
        _log.debug('Setting DNP3 {} point value = {}'.format(point_name, value))
        try:
            self.update_input_point(self.get_point_named(point_name), value)
        except Exception as e:
            raise DNP3Exception(e.message)

    @RPC.export
    def set_points(self, point_dict):
        """
            Set point values for a dictionary of points.

        @param point_dict: A dictionary of {point_name: value} for a list of DNP3 points to set.
        """
        _log.debug('Setting DNP3 point values')
        for point_name, value in point_dict.iteritems():
            self.update_input_point(self.get_point_named(point_name), value)

    @RPC.export
    def config_points(self, point_map):
        """
            For each of the agent's points, map its VOLTTRON point name to its DNP3 group and index.

        @param point_map: A dictionary that maps a point's VOLTTRON point name to its DNP3 group and index.
        """
        _log.debug('Configuring DNP3 points: {}'.format(point_map))
        self.volttron_points = point_map

    @RPC.export
    def get_point_definitions(self, point_name_list):
        """
            For each DNP3 point name in point_name_list, return a dictionary with each of the point definitions.

            The returned dictionary looks like this:

            {
                "point_name1": {
                    "property1": "property1_value",
                    "property2": "property2_value",
                    ...
                },
                "point_name2": {
                    "property1": "property1_value",
                    "property2": "property2_value",
                    ...
                }
            }

        :param point_name_list: A list of point names.
        :return: A dictionary of point definitions.
        """
        _log.debug('Fetch a list of DNP3 point definitions')
        try:
            return {name: self._get_point(name).as_json() for name in point_name_list}
        except Exception as e:
            raise DNP3Exception(e.message)

    def _process_point_value(self, point_value):
        """
            A PointValue was received from the Master. Process its payload.

        :param point_value: A PointValue.
        """
        try:
            self.add_to_current_values(point_value)
            if point_value.command_type == 'Select':
                # The point value was validated and cached, and an error was returned if a failure occurred
                # during that processing. Nothing more needs to be done for the Select command.
                pass
            else:
                step = self.update_function_for_point_value(point_value)
                if step:
                    self.set_current_function(step.function)

                    if point_value.point_def.save_on_write:
                        curr_block = self._current_selector_block
                        _log.debug('Saving selector_block state for block index {}'.format(curr_block.block_index))
                        new_block = SelectorBlock(curr_block.block_index,
                                                  curr_block.selector_block_start,
                                                  curr_block.selector_block_end)
                        new_block.points = list(curr_block.points)
                        self._selector_blocks[curr_block.block_index] = new_block

                    if step.definition.action in [ACTION_ECHO, ACTION_ECHO_AND_PUBLISH]:
                        # Echo a received PointValue, sending it back to the Master as Input.
                        self.update_input_point(self.get_point_named(step.definition.response),
                                                point_value.unwrapped_value())

                    if step.definition.action in [ACTION_PUBLISH, ACTION_ECHO_AND_PUBLISH, ACTION_PUBLISH_AND_RESPOND]:
                        self.publish_function_step(step)
        except Exception as err:
            self.set_current_function(None)             # Discard the current function
            raise DNP3Exception('Error processing point value: {}'.format(err))

    def point_value_for_command(self, command_type, command, index, op_type):
        """
            A DNP3 Select or Operate was received from the master. Create and return a PointValue for its data.

        :param command_type: Either 'Select' or 'Operate'.
        :param command: A ControlRelayOutputBlock or else a wrapped data value (AnalogOutputInt16, etc.).
        :param index: DNP3 index of the payload's data definition.
        :param op_type: An OperateType, or None if command_type == 'Select'.
        :return: An instance of PointValue
        """
        function_code = command.functionCode if type(command) == opendnp3.ControlRelayOutputBlock else None
        point_type = POINT_TYPE_BINARY_OUTPUT if function_code else POINT_TYPE_ANALOG_OUTPUT

        array = self._current_array
        if array and array.contains_index(index):
            # Search for an Array point using index offsets.
            # This debug line is too chatty...
            # _log.debug('Receiving array point {} (bounds = {},{})'.format(index,
            #                                                               array.point_def.index,
            #                                                               array.point_def.array_last_index))
            point_def = self.for_point_type_and_index(point_type, array.point_def.index)
        else:
            # It's not an Array point: search for a normal point definition.
            point_def = self.for_point_type_and_index(point_type, index)

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

    def update_function_for_point_value(self, point_value):
        """Add point_value to the current Function if appropriate."""
        try:
            step_def = self.function_definitions.step_definition_for_point(point_value.point_def)
            if not step_def:
                return None
            current_function = self.current_function_for(point_value.point_def, step_def.function)

            # If the received PointValue belongs to a SelectorBlock, update it.
            if point_value.point_def.is_selector_block:
                _log.debug('Starting to receive a SelectorBlock of {}'.format(point_value.name))
                self._current_selector_block = SelectorBlock(point_value.unwrapped_value(),
                                                             point_value.point_def.selector_block_start,
                                                             point_value.point_def.selector_block_end)
            if self._current_selector_block and self._current_selector_block.contains_index(point_value.index):
                self._current_selector_block.add_point_value(point_value)

            if point_value.point_def.is_array:
                # The received point belongs to a PointArray. Update it."""
                if point_value.starts_array:
                    _log.debug('Start to receive an Array of {}'.format(point_value.name))
                    array = PointArray(point_value.point_def)
                    _log.debug('New Array starting at {} with bounds ({}, {})'.format(array.point_def.index,
                                                                                      array.point_def.index,
                                                                                      array.point_def.array_last_index))
                    self._current_array = array
                else:
                    if self._current_array is None:
                        raise DNP3Exception('Array point received, but there is no current Array.')
                if not self._current_array.contains_index(point_value.index):
                    raise DNP3Exception('Received Array point outside of current Array.')
                self._current_array.add_point_value(point_value)

            step = current_function.add_point_value(step_def, point_value, current_array=self._current_array)
            return step

        except DNP3Exception as err:
            raise DNP3Exception('Error updating function: {}'.format(err))

    def current_function_for(self, new_point_def, new_function_def):
        """A point was received. Return the current Function, updating it if necessary."""
        current_function = self.current_function()
        if current_function and new_function_def != current_function.definition:
            # The received Step belongs to a different FunctionDefinition.
            if not current_function.complete:
                raise DNP3Exception('Mismatch: {} does not belong to {}'.format(new_point_def, current_function))
            # The current Function is done, and a new Function is arriving. Discard the old one.
            current_function = self.set_current_function(None)
        if not current_function:
            current_function = self.set_current_function(Function(new_function_def))
        return current_function

    def update_input_point(self, point_def, value):
        """
            Update an input point. This may send its PointValue to the Master.

        :param point_def: A PointDefinition.
        :param value: A value to send (unwrapped simple data type, or else a list/array).
        """
        if type(value) == list:
            # The value is an array. Break it down into its constituent points, and send each one separately.
            col_count = len(point_def.array_points)
            cols_by_name = {pt['name']: col for col, pt in enumerate(point_def.array_points)}
            for row_number, point_dict in enumerate(value):
                for pt_name, pt_val in point_dict.iteritems():
                    column_number = cols_by_name[pt_name]
                    pt_index = point_def.index + col_count * row_number + column_number
                    self._apply_point_update(point_def, pt_index, pt_val)
        else:
            self._apply_point_update(point_def, point_def.index, value)

            # Side-effect: If it's a Support point for a Function, update the Function's "supported" property.
            func = self.function_definitions.support_point_names().get(point_def.name, None)
            if func is not None and func.supported != value:
                _log.debug('Updating supported property to {} in {}'.format(value, func))
                func.supported = value

    @staticmethod
    def _apply_point_update(point_def, point_index, value):
        """
            Set an input point in the outstation database. This may send its PointValue to the Master.

        :param point_def: A PointDefinition.
        :param point_index: A numeric index for the point.
        :param value: A value to send (unwrapped, simple data type).
        """
        point_type = PointDefinition.point_type_for_group(point_def.group)
        if point_type == POINT_TYPE_ANALOG_INPUT:
            wrapped_val = opendnp3.Analog(float(value))
        elif point_type == POINT_TYPE_BINARY_INPUT:
            wrapped_val = opendnp3.Binary(value)
        else:
            # @todo Also support data types other than Analog and Binary.
            raise DNP3Exception('Unsupported point type {}'.format(point_type))
        if wrapped_val is not None:
            DNP3Outstation.apply_update(wrapped_val, point_index)
        _log.debug('Sent DNP3 point {}, value={}'.format(point_def, wrapped_val.value))

    def current_function(self):
        """Return the Function being accumulated by the Outstation."""
        return self._current_func

    def set_current_function(self, func):
        """Set the Function being accumulated by the Outstation to the supplied value, which might be None."""
        if func:
            if not func.definition.supported:
                raise DNP3Exception('Received a point for unsupported {}'.format(func))
        self._current_func = func
        return func

    def publish_function_step(self, step_to_send):
        """A Function Step was received from the DNP3 Master. Publish the Function."""
        function_to_send = step_to_send.function
        msg = {
            "function_name": function_to_send.definition.name,
            "points": {step.definition.name: step.as_json(self.get_point_named(step.definition.name).type)
                       for step in function_to_send.steps}
        }
        if step_to_send.definition.action == ACTION_PUBLISH_AND_RESPOND:
            msg["expected_response"] = step_to_send.definition.response
        _log.debug('Publishing MESA {} message {}'.format(function_to_send, msg))
        self.publish_data(self.function_topic, msg)

    def publish_outstation_status(self, outstation_status):
        """Publish outstation status."""
        _log.debug('Publishing outstation status: {}'.format(outstation_status))
        self.publish_data(self.outstation_status_topic, outstation_status)


class FunctionDefinitions(object):
    """In-memory repository of FunctionDefinitions."""

    _functions = {}
    _functions_by_id = {}
    _named_step_definitions = {}

    def __init__(self, function_definitions_path=None):
        if function_definitions_path:
            file_path = os.path.expandvars(os.path.expanduser(function_definitions_path))
            self._load_functions(file_path)

    def step_definition_for_point(self, point_definition):
        """Return a StepDefinition for a given point. If there isn't exactly one matching StepDefinition, complain."""
        name = point_definition.name
        step_list = self._step_definitions_by_name().get(name, [])
        if not step_list:
            raise DNP3Exception('No StepDefinition named {}'.format(name))
        if len(step_list) > 1:
            raise DNP3Exception('Found multiple StepDefinitions named {}'.format(name))
        return step_list[0]

    def all_function_names(self):
        return self._functions_dictionary().keys()

    def support_point_names(self):
        """Return a dictionary of FunctionDefinitions keyed by their (non-null) support_point_names."""
        return {f.support_point_name: f
                for f in self._functions_dictionary().itervalues()
                if f.support_point_name is not None}

    def _functions_dictionary(self):
        """Return a (cached) dictionary of FunctionDefinitions, indexed by function name."""
        return self._functions

    def _load_functions(self, function_definitions_path):
        """Load and cache a dictionary of FunctionDefinitions, indexed by function name."""
        _log.debug('Loading MESA-ESS FunctionDefinitions from {}.'.format(function_definitions_path))
        # Load MESA-ESS FunctionDefinitions from a YAML config file. Strip comments.
        self.functions = {}
        try:
            with open(function_definitions_path, 'r') as f:
                for function_def in yaml.load(f)['functions']:
                    # _log.debug('Loading {}'.format(function_def))
                    self._add_function_to_cache(FunctionDefinition(function_def))
        except Exception as err:
            _log.error("Problem parsing {}. No FunctionDefinitions loaded. Error={}".format(function_definitions_path,
                                                                                            err))
        _log.debug('Loaded {} FunctionDefinitions'.format(len(self._functions.keys())))

    def _add_function_to_cache(self, new_function):
        self._functions[new_function.name] = new_function
        # Ensure that the other function caches get rebuilt
        self._functions_by_id = {}
        self.named_step_definitions = {}

    def _step_definitions_by_name(self):
        """Return a (cached) dictionary of lists of StepDefinitions for each step name."""
        if not self._named_step_definitions:
            for func in self._functions_dictionary().values():
                for s in func.steps:
                    if self._named_step_definitions.get(s.name, None):
                        self._named_step_definitions[s.name].append(s)
                    else:
                        self._named_step_definitions[s.name] = [s]
        return self._named_step_definitions

    def functions_by_id(self):
        """Return a (cached) dictionary of FunctionDefinitions, indexed by function ID."""
        if not self._functions_by_id:
            self._functions_by_id = {func.function_id: func for func in self._functions_dictionary().values()}
        return self._functions_by_id

    def function_for_id(self, function_id):
        """Return a specific function definition from (cached) dictionary of FunctionDefinitions."""
        return self.functions_by_id().get(function_id, None)


class FunctionDefinition(object):
    """A MESA-ESS FunctionDefinition (aka mode, command)."""

    def __init__(self, function_def_dict):
        """
            Data holder for the definition of a MESA-ESS function.

        :param function_def_dict: A dictionary of data from which to create the FunctionDefinition.
        """
        try:
            self.function_id = function_def_dict["id"]
            self.name = function_def_dict["name"]
            self.ref = function_def_dict.get("ref", None)
            self.support_point_name = function_def_dict.get("support_point", None)
            self.steps = [StepDefinition(self, step_def) for step_def in function_def_dict["steps"]]
            # Set supported to False if the Function has a defined support_point_name -- the Control Agent must set it.
            self.supported = not self.support_point_name
            # @todo Hard-coded temporarily for test purposes.
            self.supported = True
        except AttributeError as err:
            raise AttributeError('Error creating FunctionDefinition {}, err={}'.format(self.name, err))

    def __str__(self):
        return 'Function {}'.format(self.name)

    def describe_function(self):
        """Return a string describing a function: its name and all of its StepDefinitions."""
        return 'Function {}: {}'.format(self.name, [s.__str__() for s in self.steps])


class StepDefinition(object):
    """Step definition in a MESA-ESS FunctionDefinition."""

    def __init__(self, function_def, step_def=None):
        """
            Data holder for the definition of a step in a MESA-ESS FunctionDefinition.

        :param function_def: The FunctionDefinition to which the StepDefinition belongs.
        :param step_def: A dictionary of data from which to create the StepDefinition.
        """
        self.function = function_def
        self.step_number = step_def.get('step_number', None)
        self.name = step_def.get('point_name', None)
        self.optional = step_def.get('optional', OPTIONAL)
        self.fcodes = step_def.get('fcodes', [])
        self.response = step_def.get('response', None)
        self.action = step_def.get('action', None)
        self.validate()

    def __str__(self):
        return '{} Step {}: {}'.format(self.function, self.step_number, self.name)

    def validate(self):
        if self.step_number is None:
            raise AttributeError('Missing step number in {}'.format(self))
        if self.name is None:
            raise AttributeError('Missing name in {}'.format(self))
        if self.optional not in ALL_OMC:
            raise AttributeError('Invalid optional value in {}: {}'.format(self, self.optional))
        if type(self.fcodes) != list:
            raise ValueError('Invalid fcode for {}, type={}'.format(self.name, type(self.fcodes)))
        for fc in self.fcodes:
            if fc not in [DIRECT_OPERATE, SELECT, OPERATE]:
                raise ValueError('Invalid fcode for {}, fcode={}'.format(self.name, type(self.fcodes)))


class Step(object):
    """A MESA-ESS Step that has been received by an outstation."""

    def __init__(self, definition, func, value):
        """
            Data holder for a received Step.

        :param definition: A StepDefinition.
        :param value: A PointValue.
        """
        self.definition = definition
        self.function = func
        self.value = value

    def __str__(self):
        return '{}: {}'.format(self.definition, self.value)

    def as_json(self, point_type):
        return self.value.as_json() if point_type == 'array' else self.value.unwrapped_value()


class Function(object):
    """A MESA-ESS Function that has been received by an outstation."""

    def __init__(self, definition):
        """
            Data holder for a Function received by an outstation.

        :param definition: A FunctionDefinition.
        """
        self.definition = definition
        self.steps = []
        self.complete = False

    def __str__(self):
        return 'Function {}'.format(self.definition.name)

    def add_step(self, step):
        self.steps.append(step)

    def is_complete(self):
        """
            Confirm whether the Function is complete and ready to release.

            For it to be complete, a Step value must have been received
            for each Mandatory StepDefinition in the FunctionDefinition.

        :return: (boolean) Whether the Function is complete.
        """
        received_step_names = [received_step.definition.name for received_step in self.steps]
        for step_def in self.definition.steps:
            if step_def.optional == MANDATORY and step_def.name not in received_step_names:
                _log.debug('Function is incomplete: missing mandatory step {}'.format(step_def))
                return False
        return True

    def add_point_value(self, step_def, point_value, current_array=None):
        """Add a received PointValue as a Step in the current Function. Return the Step."""
        step_number = step_def.step_number
        if len(self.steps) == 0:
            step_value = Step(step_def, self, point_value)
            self.add_step(step_value)
        else:
            prior_step = self.steps[-1]
            last_received_step_number = prior_step.definition.step_number
            if step_number == last_received_step_number:
                if not point_value.point_def.is_array:
                    raise DNP3Exception('Duplicate step number {} received'.format(step_number))
                # An array point was received for an existing step. Update the step's value.
                prior_step.value = current_array
                step_value = prior_step
            elif step_number < last_received_step_number:
                # The Function's steps must be received in step-number order
                if not self.complete:
                    raise DNP3Exception('Step {} received after {}'.format(step_number, last_received_step_number))
                # Since the old function was complete, treat this as the first step of a new function.
                self.complete = False
                self.steps = []
                self.check_for_missing_steps(step_def)
                step_value = Step(step_def, self, point_value)
                self.add_step(step_value)
            else:
                self.check_for_missing_steps(step_def)
                step_value = Step(step_def, self, point_value)
                self.add_step(step_value)
        if not self.missing_step_numbers():
            self.complete = True
        return step_value

    def check_for_missing_steps(self, step_def):
        """All Mandatory steps with smaller step numbers must be received prior to the current step."""
        for n in self.missing_step_numbers():
            if step_def.step_number > n:
                raise DNP3Exception('Function {} is missing Mandatory step number {}'.format(self, n))

    def missing_step_numbers(self):
        """Return a list of the numbers of this function's Mandatory steps that have not yet been received."""
        received_step_numbers = [s.definition.step_number for s in self.steps]
        missing_step_numbers = [sd.step_number
                                for sd in self.definition.steps
                                if sd.optional == MANDATORY and sd.step_number not in received_step_numbers]
        return missing_step_numbers


class PointArray(object):
    """Data holder for a MESA-ESS Array."""

    def __init__(self, point_def):
        """
            The "points" variable is a dictionary of dictionaries:
                0: {
                    0: PointValue,
                    1: PointValue
                },
                1: {
                    0: PointValue,
                    1: PointValue
                }
                (etc.)
            It's stored as dictionaries indexed by index numbers, not as lists,
            because there's no guarantee that array elements will arrive in order.

        :param point_def: The PointDefinition of the array's head point.
        """
        self.point_def = point_def
        self.points = {}

    def __str__(self):
        return 'Array Instance'

    def as_json(self):
        """
            Return a JSON representation of the PointArray:

                [
                    {name1: val1a, name2: val2a, ...},
                    {name1: val1b, name2: val2b, ...},
                    ...
                ]
        """
        names = [d['name'] for d in sorted(self.point_def.array_points)]
        json_array = []
        for pt_dict_key in sorted(self.points):
            pt_dict = self.points[pt_dict_key]
            json_array.append({name: (pt_dict[i].value if i in pt_dict else None) for i, name in enumerate(names)})
        return json_array

    def contains_index(self, index):
        """Answer whether this Array contains the point index."""
        return self.point_def.index <= index <= self.point_def.array_last_index

    def add_point_value(self, point_value):
        """Add point_value to the Array's "points" dictionary."""
        # This debug line is too chatty...
        # _log.debug('Adding Array point at {} with value {}'.format(point_value.index, point_value.unwrapped_value()))
        array_points = self.point_def.array_points
        array_size = len(array_points)
        i = point_value.array_element(array_size)
        j = point_value.array_points_index(array_size)
        if i not in self.points:
            self.points[i] = {}
        self.points[i][j] = point_value


class SelectorBlock(object):
    """Data holder for a MESA-ESS SelectorBlock."""

    def __init__(self, block_index, selector_block_start, selector_block_end):
        self.block_index = block_index
        self.selector_block_start = selector_block_start
        self.selector_block_end = selector_block_end
        self.points = []

    def __str__(self):
        return 'SelectorBlock Instance'

    def contains_index(self, index):
        """Answer whether this SelectorBlock contains the point index."""
        return self.selector_block_start <= index <= self.selector_block_end

    def add_point_value(self, point_value):
        # This debug line is too chatty...
        # _log.debug('Adding SelectorBlock point at {} with value {}'.format(point_value.index,
        #                                                                    point_value.unwrapped_value()))
        self.points.append(point_value)


def load_and_validate_definitions():
    """
        Standalone method, intended to be invoked from the command line.

        Load PointDefinition and FunctionDefinition files as specified in command line args,
        and validate their contents.
    """
    # Grab JSON and YAML definition file paths from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument('point_defs', help='path of the point definitions file (json)')
    parser.add_argument('function_defs', help='path of the function definitions file (yaml)')
    args = parser.parse_args()

    point_definitions = PointDefinitions(args.point_defs)
    function_definitions = FunctionDefinitions(args.function_defs)
    validate_definitions(point_definitions, function_definitions)


def validate_definitions(point_definitions, function_definitions):
    """Validate PointDefinitions, Arrays, SelectorBlocks and FunctionDefinitions."""
    print('\nValidating Point definitions...')
    print('\t{} Point definitions'.format(len(point_definitions.all_point_names())))
    print('\nValidating Array definitions...')
    points_by_name = point_definitions.points_by_name()
    array_points = [pt for pt in points_by_name.values() if pt.is_array]
    array_bounds = {pt: [pt.index, pt.array_last_index] for pt in array_points}
    for pt in array_points:
        # Print each array's definition. Also, check for overlapping array bounds.
        print('\t{} ({}): indexes=({},{}), elements={}'.format(pt.name,
                                                               pt.point_type,
                                                               pt.index,
                                                               pt.array_last_index,
                                                               len(pt.array_points)))
        for other_pt, other_bounds in array_bounds.iteritems():
            if pt.name != other_pt.name:
                if other_bounds[0] <= pt.index <= other_bounds[1]:
                    print('\tERROR: Overlapping array definition in {} and {}'.format(pt, other_pt))
                if other_bounds[0] <= pt.array_last_index <= other_bounds[1]:
                    print('\tERROR: Overlapping array definition in {} and {}'.format(pt, other_pt))
    print('\t{} Array definitions'.format(len(array_points)))
    print('\nValidating Selector Block definitions...')
    selector_block_points = [pt for pt in points_by_name.values() if pt.is_selector_block]
    selector_block_bounds = {pt: [pt.selector_block_start, pt.selector_block_end] for pt in selector_block_points}
    for pt in selector_block_points:
        # Print each selector block's definition. Also, check for overlapping selector block bounds.
        print('\t{} ({}): indexes=({},{})'.format(pt.name,
                                                  pt.point_type,
                                                  pt.selector_block_start,
                                                  pt.selector_block_end))
        for other_pt, other_bounds in selector_block_bounds.iteritems():
            if pt.name != other_pt.name:
                if other_bounds[0] <= pt.selector_block_start <= other_bounds[1]:
                    print('\tERROR: Overlapping selector blocks in {} and {}'.format(pt, other_pt))
                if other_bounds[0] <= pt.selector_block_end <= other_bounds[1]:
                    print('\tERROR: Overlapping selector blocks in {} and {}'.format(pt, other_pt))
    print('\t{} Selector Block definitions'.format(len(selector_block_points)))
    print('\nValidating Function definitions...')
    functions = function_definitions.all_function_names()
    print('\t{} Function definitions'.format(len(functions)))


def mesa_agent(config_path, **kwargs):
    """
        Parse the MesaAgent configuration. Return an agent instance created from that config.

    :param config_path: (str) Path to a configuration file.
    :returns: (MesaAgent) The MESA agent
    """
    try:
        config = utils.load_config(config_path)
    except StandardError:
        config = {}
    return MesaAgent(point_definitions_path=config.get('point_definitions_path', ''),
                     function_definitions_path=config.get('function_definitions_path', ''),
                     point_topic=config.get('point_topic', DEFAULT_POINT_TOPIC),
                     function_topic=config.get('function_topic', DEFAULT_FUNCTION_TOPIC),
                     outstation_status_topic=config.get('outstation_status_topic', DEFAULT_OUTSTATION_STATUS_TOPIC),
                     local_ip=config.get('local_ip', DEFAULT_LOCAL_IP),
                     port=config.get('port', DEFAULT_PORT),
                     outstation_config=config.get('outstation_config', {}),
                     **kwargs)


def main():
    """Main method called to start the agent."""
    utils.vip_main(mesa_agent, identity='mesaagent', version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
