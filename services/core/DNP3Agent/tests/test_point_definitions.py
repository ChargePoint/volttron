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
from services.core.DNP3Agent.dnp3.base_dnp3_agent import PointDefinitions, PointDefinition
from services.core.DNP3Agent.dnp3.mesa.agent import FunctionDefinitions

POINT_DEFINITIONS_CONFIG = 'data/opendnp3_data.config'
FUNCTION_CONFIG = 'data/mesa_functions.yaml'

def test_point_definition_load():
    point_defs = PointDefinitions()
    point_defs.load_points(POINT_DEFINITIONS_CONFIG)
    import pprint
    pprint.pprint(point_defs._points)
    pprint.pprint(point_defs._point_name_dict)
    print("_point_variations_dict")
    pprint.pprint(point_defs._point_variation_dict)

def test_point_definition():

    test_dict = {
        "name": "CurveStart-X",
        "type": "array",                # Start of the curve's X/Y array
        "array_times_repeated": 100,
        "group": 40,
        "variation": 1,
        "index": 207,
        "description": "Starting index for a curve of up to 99 X/Y points",
        "array_points": [
            {
                "name": "Curve-X"
            },
            {
                "name": "Curve-Y"
            }
        ]
    }
    test_def = PointDefinition(test_dict)
    print(test_def)

def test_function_definitions():
    point_definitions = PointDefinitions(POINT_DEFINITIONS_CONFIG)
    fd = FunctionDefinitions(point_definitions, FUNCTION_CONFIG).function_for_id("curve")
    print(fd)

    function_definitions = FunctionDefinitions(point_definitions, FUNCTION_CONFIG)

if __name__ == "__main__":
    test_function_definitions()
    #test_point_definition()
    #test_point_definition_load()