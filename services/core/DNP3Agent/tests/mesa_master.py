import logging
import os
import sys
import time

from pydnp3 import opendnp3

from services.core.DNP3Agent.dnp3.base_dnp3_agent import DIRECT_OPERATE, SELECT, OPERATE
from services.core.DNP3Agent.dnp3.base_dnp3_agent import POINT_TYPE_ANALOG_OUTPUT, POINT_TYPE_BINARY_OUTPUT
from services.core.DNP3Agent.dnp3.base_dnp3_agent import PointDefinition, PointDefinitions
from services.core.DNP3Agent.master import DNP3Master
from services.core.DNP3Agent.dnp3.mesa.agent import FunctionDefinitions
from services.core.DNP3Agent.tests.util.function_test import FunctionTest

stdout_stream = logging.StreamHandler(sys.stdout)
stdout_stream.setFormatter(logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'))

_log = logging.getLogger(__name__)
_log.addHandler(stdout_stream)
_log.setLevel(logging.DEBUG)

FUNCTION_DEF_PATH = "/Users/natehill/repos/volttron/services/core/DNP3Agent/mesa_functions.yaml"


class MesaMasterApplication(DNP3Master):

    def __init__(self, *args, **kwargs):
        super(MesaMasterApplication, self).__init__(*args, **kwargs)

    def send_mesa_array(self):
        """Send requests to the outstation for all points in a MESA-ESS array."""
        start_point = PointDefinition.output_point_named('CurveStart-X')
        _log.debug('Sending a set of array points for {}'.format(start_point))
        element_count = len(start_point.array_points)
        for i in range(start_point.array_times_repeated):
            for j in range(element_count):
                indx = start_point.index + i * element_count + j
                # Use the current index number as the value that's sent for each point in the array.
                self.write_integer_value(indx, indx)

    def send_mesa_function(self, function_id):
        """Send requests to the outstation for each step in a MESA-ESS function."""
        mesa_function = FunctionDefinitions(FUNCTION_DEF_PATH).function_for_id(function_id)
        # mesa_function = FunctionDefinition.functions_dictionary().get(function_name, None)
        if not mesa_function:
            return _log.error('No function with ID {} found in MESA-ESS function config'.format(function_id))

        _log.debug('Sending all points for {}'.format(mesa_function))
        for step in mesa_function.steps:
            pdef = PointDefinition.output_point_named(step.name)
            if not pdef:
                _log.error('Unable to find PointDefinition for {}'.format(step.name))
            else:
                # To do here: Use each Step's fcodes to send select vs. operate -- see how send_function_test does this.
                if pdef.point_type == POINT_TYPE_ANALOG_OUTPUT:
                    _log.debug('Sending 10 for {} index {} ({})'.format(POINT_TYPE_ANALOG_OUTPUT, pdef.index, pdef.name))
                    self.write_integer_value(int(pdef.index), 10)
                elif pdef.point_type == POINT_TYPE_BINARY_OUTPUT:
                    _log.debug('Sending LATCH_ON for {} index {} ({})'.format(POINT_TYPE_BINARY_OUTPUT, pdef.index, pdef.name))
                    self.send_select_and_operate_command(int(pdef.index), opendnp3.ControlCode.LATCH_ON)
                else:
                    _log.error('Unexpected point type in function config: {} is {}'.format(pdef.name, pdef.point_type))

    def send_volt_var_curve(self):
        """Send a volt-VAr sequence of x/y points to the outstation."""
        _log.debug('Sending a volt-VAr curve.')
        self.send_curve(edit_selector=1, mode_type=2, point_count=10)

    def send_curve(self, edit_selector=None, mode_type=None, point_count=None):
        """Send a volt-VAr sequence of x/y points to the outstation."""
        _log.debug('Sending a volt-VAr curve.')
        self.write_integer_value(int(PointDefinition.output_point_named('Curve Edit Selector').index), edit_selector)
        self.write_integer_value(int(PointDefinition.output_point_named('Curve Mode Type').index), mode_type)
        self.write_integer_value(int(PointDefinition.output_point_named('Curve Number of Points').index), point_count)
        # Other curve metadata could also be sent at this point if desired.
        x_start_index = int(PointDefinition.output_point_named("CurveStart-X").index)
        y_start_index = int(PointDefinition.output_point_named("CurveStart-Y").index)
        for i in range(0, point_count):
            # Send an x-value and a y-value for each point in the curve.
            x_index = x_start_index + i * 2
            y_index = y_start_index + i * 2
            x_value = (x_index % (i + 10)) / float(x_index)
            y_value = (y_index % (i + 10)) / float(y_index)
            self.write_floating_point_value(x_index, x_value)
            self.write_floating_point_value(y_index, y_value)

    def send_function_test(self, **kwargs):
        """
        Sends a function test after validating the function test (as JSON).
        :param kwargs:
        :return:
        """
        ftest = FunctionTest(**kwargs)

        try:
            is_valid = ftest.is_valid()
        except Exception as e:
            raise e  # Function test is not valid

        #  At this point, we know function has all the mandatory steps

        OUTPUT_TYPES = {
            float: opendnp3.AnalogOutputFloat32,
            int: opendnp3.AnalogOutputInt32,
            bool: opendnp3.ControlRelayOutputBlock
        }

        COMMAND_TYPES = {
            DIRECT_OPERATE: self.send_direct_operate_command,
            SELECT: self.send_select_and_operate_command,
            OPERATE: self.send_select_and_operate_command,
        }

        def send_array(index, json_array, point_def):

            array_points = point_def.array_points
            for d in json_array:
                for array_point in array_points:
                    command = COMMAND_TYPES[DIRECT_OPERATE]
                    output_type = OUTPUT_TYPES[type(d[array_point["name"]])]  # or array_point['name']
                    command(output_type(d[array_point["name"]]), index)
                    index += 1
                    time.sleep(1)

        point_def_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'opendnp3_data.config'))
        pdefs = PointDefinitions(point_def_path)

        func_def = ftest.get_function_def()

        for func_step_def in func_def.steps:
            try:
                point_name = func_step_def.name
                point_value = ftest.points[point_name]
            except KeyError:
                continue
            pdef = pdefs.point_named(point_name)  # No need to test for valid point name, as that was done above
            print(point_name)
            try:
                output_type = OUTPUT_TYPES[type(point_value)]
                command = COMMAND_TYPES[func_step_def.fcodes[0] if func_step_def.fcodes else DIRECT_OPERATE]

            except (KeyError, IndexError):
                if type(point_value) == list:  # or check if the type is array
                    send_array(pdef.index, point_value, pdef)
                    continue
                else:
                    raise Exception("Unrecognized value type or command.")

            if pdef.point_type == POINT_TYPE_ANALOG_OUTPUT:
                command(output_type(point_value), pdef.index)
            elif pdef.point_type == POINT_TYPE_BINARY_OUTPUT:
                latch_bool = opendnp3.ControlCode.LATCH_ON if point_value else opendnp3.ControlCode.LATCH_OFF
                command(output_type(latch_bool), pdef.index)
            else:
                _log.error("Unrecognized point type")
            # Sleeping for debug purposes
            time.sleep(1)


def main():
    app = MesaMasterApplication()
    _log.debug('Initialization complete. In command loop.')
    # Ad-hoc tests can be performed at this point.
    app.shutdown()
    _log.debug('Exiting.')
    exit()


if __name__ == '__main__':
    main()
