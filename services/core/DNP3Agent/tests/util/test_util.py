import json
import os

from mesa import agent as MA

# FUNCTION_DEF_PATH = "/Users/natehill/repos/volttron/services/core/DNP3Agent/mesa_functions.yaml"
# SAMPLE_FUNC_TEST_PATH = "/Users/natehill/repos/volttron/services/core/DNP3Agent/tests/nate/sample_json/format.config"

FUNCTION_DEF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'mesa_functions.yaml'))
SAMPLE_FUNC_TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sample_json', 'format.config'))


class FunctionTest(object):

    def __init__(self, **kwargs):
        func_test_json = kwargs.pop('func_test_json', None)
        func_test_path = kwargs.pop('func_test_path', SAMPLE_FUNC_TEST_PATH)

        if func_test_json:
            self.ftest = json.loads(func_test_json)
        else:
            self.ftest = json.load(open(func_test_path))

        self.function_id = self.ftest.get('function_id', None)
        self.function_name = self.ftest.get('function_name', None)
        self.name = self.ftest.get('name', None)
        self.non_points = ["name", "function_id", "function_name"]
        self.points = {k: v for k, v in self.ftest.items() if k not in self.non_points}

    def get_function_def(self):
        """
        Gets the function definition for the function test. Returns None if
        no definition is found.
        :return:
        """
        return MA.FunctionDefinitions(FUNCTION_DEF_PATH).function_for_id(self.function_id)

    @staticmethod
    def get_mandatory_steps(func_def):
        """
        Returns list of mandatory steps for the given function definition.
        :param func_def:
        :return:
        """
        return [step.name for step in func_def.steps if step.optional == 'M']

    def has_mandatory_steps(self, fdef=None):
        """
        Returns True if the instance has all required steps, and raises
        an exception if not.
        :param m_steps: mandatory steps
        :param fdef: Function definition
        :return:
        """
        f_def = fdef or self.get_function_def()
        if f_def:
            m_steps = self.get_mandatory_steps(f_def)
        else:
            raise Exception("Function definition not found")
        if not all(step in self.ftest.keys() for step in m_steps):
            raise Exception("Function Test missing mandatory steps")
        return True

    def points_resolve(self, func_def):
        """
        Returns true if all the points in the instance resolve to point names in the function definition,
        and raises an exception if not.
        :param func_def: function definition of the given instance
        :return:
        """
        if not all(step_name in [step.name for step in func_def.steps] for step_name in self.points.keys()):
            raise Exception("Not all points resolve")
        return True

    def is_valid(self):
        """
        Returns True if the function test passes two validation steps:
            1. it has all the mandatory steps
            2. its point names resolve to point names in the function definition
        If the function test is invalid, an exception is raised.
        :return:
        """

        f_def = self.get_function_def()
        if not f_def:
            raise Exception("Function definition not found")
        try:
            has_steps = self.has_mandatory_steps(f_def)
            pts_resolve = self.points_resolve(f_def)
            return True
        except Exception as e:
            raise Exception("Validation error: {}".format(e.message))








