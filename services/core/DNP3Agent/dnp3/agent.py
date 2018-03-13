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

import logging
import sys

from pydnp3 import opendnp3, openpal, asiopal, asiodnp3

from volttron.platform.agent import utils
from volttron.platform.vip.agent import RPC

from base_dnp3_agent import BaseDNP3Agent, PointDefinition
from base_dnp3_agent import DNP3Exception
from base_dnp3_agent import POINT_TYPE_ANALOG_INPUT, POINT_TYPE_BINARY_INPUT
from outstation import DNP3Outstation

utils.setup_logging()
_log = logging.getLogger(__name__)

__version__ = '1.0'


class DNP3Agent(BaseDNP3Agent):
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

    def __init__(self, **kwargs):
        """Initialize the DNP3 agent."""
        super(DNP3Agent, self).__init__(**kwargs)
        self.vip.config.set_default('config', self.default_config)
        self.vip.config.subscribe(self._configure, actions=['NEW', 'UPDATE'], pattern='config')

    @RPC.export
    def get_point(self, point_name):
        """
            Look up the most-recently-received value for a given output point.

        @param point_name: The point name of a DNP3 PointDefinition.
        @return: The (unwrapped) value of a received point.
        """
        _log.debug('Getting DNP3 point value for {}'.format(point_name))
        self._get_point(point_name)

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
        _log.debug('Setting DNP3 {} point value to {}'.format(point_name, value))
        self._set_point(point_name, value)

    @RPC.export
    def set_points(self, point_list):
        """
            Set point values for a list of points.

        @param point_list: An array of (point_name, value) for a list of DNP3 points to set.
        """
        _log.debug('Setting an array of DNP3 point values')
        for (point_name, value) in point_list:
            self.set_point(point_name, value)

    @RPC.export
    def config_points(self, point_map):
        """
            For each of the agent's points, map its point name to its DNP3 group and index.

        @param point_map: A dictionary that maps a point's name to its DNP3 group and index.
        """
        _log.debug('Configuring DNP3 points: {}'.format(point_map))
        self.volttron_points = point_map

    def _process_point_value(self, point_value):
        _log.debug('Received DNP3 {}'.format(point_value))
        if point_value.command_type == 'Select':
            # Perform any needed validation now, then wait for the subsequent Operate command.
            pass
        else:
            self.add_to_current_values(point_value)
            self.echo_point(point_value)
            self.publish_point_value(point_value)

    @staticmethod
    def echo_point(point_value):
        """
            When appropriate, echo a received PointValue, sending it back to the Master as Input.

        :param point_value: A PointValue.
        """
        echo = point_value.point_def.echo
        if echo is not None:
            # An echo has been defined. Send the received value back to the Master, using the configured point type.
            echo_point_type = PointDefinition.point_type_for_group(echo.get('group'))
            if echo_point_type == POINT_TYPE_ANALOG_INPUT:
                value = float(point_value.value)
                wrapped_value = opendnp3.Analog(value)
            elif echo_point_type == POINT_TYPE_BINARY_INPUT:
                # If the Master sent a function code, echo True if it was LATCH_ON, false otherwise
                value = point_value.value or (point_value.function_code == opendnp3.ControlCode.LATCH_ON)
                wrapped_value = opendnp3.Binary(value)
            else:
                value = wrapped_value = None
            if wrapped_value is not None:
                _log.debug('Echoing received DNP3 point, echo={}, type={}, value={}'.format(echo,
                                                                                            echo_point_type,
                                                                                            value))
                DNP3Outstation.apply_update(wrapped_value, echo.get('index'))


def dnp3_agent(config_path, **kwargs):
    """
        Parse the DNP3 Agent configuration. Return an agent instance created from that config.

    :param config_path: (str) Path to a configuration file.
    :returns: (DNP3Agent) The DNP3 agent
    """
    try:
        config = utils.load_config(config_path)
    except StandardError:
        config = {}
    return DNP3Agent(point_definitions_path=config.get('point_definitions_path', ''),
                     point_topic=config.get('point_topic', 'dnp3/point'),
                     local_ip=config.get('local_ip', '0.0.0.0'),
                     port=config.get('port', 20000),
                     outstation_config=config.get('outstation_config', {}),
                     **kwargs)


def main():
    """Main method called to start the agent."""
    utils.vip_main(dnp3_agent, identity='dnp3agent', version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
