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

import gevent
import pytest
import json
import os
import time

from pydnp3 import asiodnp3, asiopal, opendnp3, openpal

from volttron.platform import get_services_core
from services.core.DNP3Agent.tests.mesa_master import MesaMasterApplication
from services.core.DNP3Agent.base_dnp3_agent import PointDefinitions
from services.core.DNP3Agent.tests.util.function_test import FunctionTestException

FILTERS = opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS
HOST = "127.0.0.1"
LOCAL = "0.0.0.0"
PORT = 20000

MESA_AGENT_ID = 'mesaagent'

POINT_DEFINITIONS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'opendnp3_data.config'))
FUNCTION_DEFINITIONS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'mesa_functions.yaml'))

pdefs = PointDefinitions(POINT_DEFINITIONS_PATH)

input_group_map = {
    1: "Binary",
    2: "Binary",
    30: "Analog",
    31: "Analog",
    32: "Analog",
    33: "Analog",
    34: "Analog"
}

MESA_AGENT_CONFIG = {
    "point_definitions_path": POINT_DEFINITIONS_PATH,
    "function_definitions_path": FUNCTION_DEFINITIONS_PATH,
    "point_topic": "mesa/point",
    "outstation_config": {
        "database_sizes": 100,
        "log_levels": "NORMAL | ALL_APP_COMMS"
    },
    "local_ip": "0.0.0.0",
    "port": 20000
}

web_address = ""

MESA_TEST_AGENT_CONFIG = {
    "mesaagent_id": "mesaagent_test",
    "point_topic": "mesa/point",
    "function_topic": "mesa/function",
    "outstation_status_topic": "mesa/outstation_status"
}

messages = {}


def onmessage(peer, sender, bus, topic, headers, message):
    messages[topic] = {'headers': headers, 'message': message}


def clear_messages():
    global messages
    messages = {}


TRIM_DICT_KEYS = ["name", "function_id", "function_name"]


def trim_dictionary(d):
    return {k: v for k, v in d.items() if k not in TRIM_DICT_KEYS}


@pytest.fixture(scope="module")
def agent(request, volttron_instance_module_web):
    """Build the test agent for rpc call."""

    test_agent = volttron_instance_module_web.build_agent()

    print('Installing DNP3Agent')
    agent_id = volttron_instance_module_web.install_agent(agent_dir=get_services_core("DNP3Agent"),
                                                          config_file=MESA_AGENT_CONFIG,
                                                          vip_identity=MESA_AGENT_ID,
                                                          start=True)

    global web_address
    web_address = volttron_instance_module_web.bind_web_address

    # Subscribe to MESA functions/points
    test_agent.vip.pubsub.subscribe(peer='pubsub',
                                    prefix='mesa/function',
                                    callback=onmessage)

    def stop():
        """Stop test agent."""
        volttron_instance_module_web.stop_agent(agent_id)
        test_agent.core.stop()

    gevent.sleep(3)        # wait for agents and devices to start

    request.addfinalizer(stop)

    return test_agent


@pytest.fixture(scope="module")
def run_master():
    return MesaMasterApplication(local_ip=MESA_AGENT_CONFIG['local_ip'],
                                 port=MESA_AGENT_CONFIG['port'])


class TestMesaAgent:
    """Regression tests for the Mesa Agent."""

    @staticmethod
    def get_point(agent, point_name):
        """Ask DNP3Agent for a point value for a DNP3 resource."""
        return agent.vip.rpc.call(MESA_AGENT_ID, 'get_point', point_name).get(timeout=10)

    @staticmethod
    def get_point_by_index(agent, group, index):
        """Ask DNP3Agent for a point value for a DNP3 resource."""
        return agent.vip.rpc.call(MESA_AGENT_ID, 'get_point_by_index', group, index).get(timeout=10)

    @staticmethod
    def set_point(agent, point_name, value):
        """Use DNP3Agent to set a point value for a DNP3 resource."""
        return agent.vip.rpc.call(MESA_AGENT_ID, 'set_point', point_name, value).get(timeout=10)

    @staticmethod
    def send_points(master, send_json):
        """Master loads points from json and send them to mesa agent."""
        try:
            master.send_function_test(func_test_json=send_json)
        except Exception as e:
            print("exception {}".format(e))

    @staticmethod
    def get_value_from_master(master, point_name):
        """Get value of the point from master after being set by test agent."""
        try:
            pdef = pdefs.point_named(point_name)
            group = input_group_map[pdef.group]
            index = pdef.index
            return master.soe_handler.result[group][index]
        except KeyError:
            return None

    def run_test(self, master, agent, json_file, support_point='', fail_state=False):
        """Test get points to confirm if points is set correctly by master."""

        if support_point:
            if fail_state:
                self.set_point(agent, support_point, False)
            else:
                self.set_point(agent, support_point, True)
            time.sleep(1)

        send_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'sample_json', json_file))
        send_json = json.load(open(send_json_path))
        self.send_points(master, send_json)

        for point_name in send_json.keys():
            if point_name not in TRIM_DICT_KEYS:

                pdef = pdefs.point_named(point_name)

                if pdef.type == "array":
                    group = pdef.group
                    index = pdef.index

                    for d in send_json[point_name]:
                        for point in pdef.array_points:
                            get_point = self.get_point_by_index(agent, group, index)
                            if fail_state:
                                assert get_point == None
                            else:
                                assert get_point == d[point["name"]]
                            index += 1
                else:
                    get_point = self.get_point(agent, point_name)
                    if fail_state:
                        assert get_point == None
                    else:
                        assert get_point == send_json[point_name]

        if fail_state:
            assert messages == {}
        else:
            assert messages['mesa/function']['message']['points'].items() == trim_dictionary(send_json)
            clear_messages()

    def test_fail_charge_discharge(self, run_master, agent):
        """Do not set the support point to True"""
        self.run_test(run_master, agent, 'charge_discharge.json', "Supports Charge/Discharge Mode", True)

    def test_charge_discharge(self, run_master, agent):
        """Test function charge_discharge_mode."""

        self.run_test(run_master, agent, 'charge_discharge.json', "Supports Charge/Discharge Mode")

        self.set_point(agent, "DCHD.WinTms (in)", 45)
        assert self.get_value_from_master(run_master, "DCHD.WinTms (in)") == 45

    def test_curve(self, run_master, agent):
        """Test function curve_function."""
        self.run_test(run_master, agent, 'curve.json')

    def test_inverter(self, run_master, agent):
        """Test inverter function"""
        self.run_test(run_master, agent, 'inverter.json')


send_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'sample_json', 'selector_block_1.json'))
TestMesaAgent.send_points(run_master(), json.load(open(send_json_path)))

# master = run_master()
# send_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'sample_json', 'charge_discharge.json'))
# try:
#     master.send_function_test(func_test_path=send_json_path)
# except Exception as e:
#     print("exception {}".format(e))
# while True:
#     print master.soe_handler.result["Analog"][91]
#     time.sleep(2)

#     print master.soe_handler.result["Binary"][36]
#     time.sleep(2)
