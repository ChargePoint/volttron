from __future__ import absolute_import

import sys

from volttron.platform.vip.agent import Agent, Core
from volttron.platform.agent import utils

DEFAULT_AGENTID = "controlagent"
DEFAULT_HEARTBEAT_PERIOD = 5


class ControlAgent(Agent):

    def __init__(self, config_path, **kwargs):
        super(ControlAgent, self).__init__(**kwargs)
        self._agent_id = None
        self.function_message = None

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        self._agent_id = DEFAULT_AGENTID

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        self.vip.heartbeat.start_with_period(DEFAULT_HEARTBEAT_PERIOD)
        self.vip.pubsub.subscribe('pubsub', 'mesa/function', self.get_function_json)
        self.vip.pubsub.subscribe('pubsub', '', self.print_function_json)

        self.set_point("Supports Charge/Discharge Mode", True)

    def get_function_json(self, peer, sender, bus, topic, headers, message):
        if 'points' in message:
            self.function_message = message["points"]

    def print_function_json(self, peer, sender, bus, topic, headers, message):
        print self.function_message
    #     print self.get_point("DCHD.WinTms (out)")

    def set_point(self, point_name, point_value):
        return self.vip.rpc.call('mesaagent', 'set_point', point_name, point_value).get(timeout=10)

    def get_point(self, point_name):
        return self.vip.rpc.call('mesaagent', 'get_point', point_name).get(timeout=10)

    def get_point_by_index(self, group, index):
        return self.vip.rpc.call('mesaagent', 'get_point_by_index', group, index).get(timeout=10)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(agent_class=ControlAgent,
                       identity='controlagent')
    except Exception as e:
        print('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
