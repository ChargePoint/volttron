import logging
import time

from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
from visitors import *

_log = logging.getLogger(__name__)


class SOEHandler(opendnp3.ISOEHandler):
    """
        Override ISOEHandler in this manner to implement application-specific sequence-of-events behavior.

        This is an interface for SequenceOfEvents (SOE) callbacks from the Master stack to the application layer.
    """

    def __init__(self):
        super(SOEHandler, self).__init__()
        self.result = {
            "Binary": {},
            "DoubleBitBinary": {},
            "Counter": {},
            "FrozenCounter": {},
            "Analog": {},
            "BinaryOutputStatus": {},
            "AnalogOutputStatus": {},
            "TimeAndInterval": {}
        }

    def Process(self, info, values):
        """
            Process measurement data.

        :param info: HeaderInfo
        :param values: A collection of values received from the Outstation (various data types are possible).
        """
        visitor_class_types = {
            opendnp3.ICollectionIndexedBinary: VisitorIndexedBinary,
            opendnp3.ICollectionIndexedDoubleBitBinary: VisitorIndexedDoubleBitBinary,
            opendnp3.ICollectionIndexedCounter: VisitorIndexedCounter,
            opendnp3.ICollectionIndexedFrozenCounter: VisitorIndexedFrozenCounter,
            opendnp3.ICollectionIndexedAnalog: VisitorIndexedAnalog,
            opendnp3.ICollectionIndexedBinaryOutputStatus: VisitorIndexedBinaryOutputStatus,
            opendnp3.ICollectionIndexedAnalogOutputStatus: VisitorIndexedAnalogOutputStatus,
            opendnp3.ICollectionIndexedTimeAndInterval: VisitorIndexedTimeAndInterval
        }

        visitor_class = visitor_class_types[type(values)]
        visitor = visitor_class()
        values.Foreach(visitor)

        for index, value in visitor.index_and_value:
            self.result[type(values).__name__.split("ICollectionIndexed")[1]][index] = value

    def Start(self):
        pass

    def End(self):
        pass


class DNP3Master(opendnp3.IMasterApplication):
    """
        Interface for all master application callback info except for measurement values.
    """

    def __init__(self, log_levels=opendnp3.levels.NORMAL | opendnp3.levels.ALL_APP_COMMS, host_ip="127.0.0.1",
                 local_ip="0.0.0.0", port=20000):

        super(DNP3Master, self).__init__()

        # Root DNP3 object used to create channels and sessions
        self.manager = asiodnp3.DNP3Manager(1, asiodnp3.ConsoleLogger().Create())

        # Connect via a TCPServer socket to a server
        self.channel = self.manager.AddTCPClient("tcpclient",
                                                 log_levels,
                                                 asiopal.ChannelRetry(),
                                                 host_ip,
                                                 local_ip,
                                                 port,
                                                 asiodnp3.PrintingChannelListener().Create())

        self.stackConfig = asiodnp3.MasterStackConfig()
        self.stackConfig.master.responseTimeout = openpal.TimeDuration().Seconds(2)
        self.stackConfig.link.RemoteAddr = 10

        # Add an outstation to a communication channel
        self.soe_handler = SOEHandler()
        # soe_handler = asiodnp3.PrintingSOEHandler().Create()
        self.master = self.channel.AddMaster("master",
                                             self.soe_handler,
                                             asiodnp3.DefaultMasterApplication().Create(),
                                             self.stackConfig)

        self.master.Enable()

    def send_direct_operate_command(self, command, index, callback=asiodnp3.PrintingCommandCallback.Get(),
                                    config=opendnp3.TaskConfig().Default()):
        """
            Direct operate a single command

        :param command: command to operate
        :param index: index of the command
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.DirectOperate(command, index, callback, config)

    def send_direct_operate_command_set(self, command_set, callback=asiodnp3.PrintingCommandCallback.Get(),
                                        config=opendnp3.TaskConfig().Default()):
        """
            Direct operate a set of commands

        :param command_set: set of command headers
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.DirectOperate(command_set, callback, config)

    def send_select_and_operate_command(self, command, index, callback=asiodnp3.PrintingCommandCallback.Get(),
                                        config=opendnp3.TaskConfig().Default()):
        """
            Select and operate a single command

        :param command: command to operate
        :param index: index of the command
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.SelectAndOperate(command, index, callback, config)

    def send_select_and_operate_command_set(self, command_set, callback=asiodnp3.PrintingCommandCallback.Get(),
                                            config=opendnp3.TaskConfig().Default()):
        """
            Select and operate a set of commands

        :param command_set: set of command headers
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.SelectAndOperate(command_set, callback, config)

    def shutdown(self):
        """
            Shutdown manager and terminate the threadpool
        """
        self.manager.Shutdown()

def main():
    dnp3_master = DNP3Master()
    time.sleep(1000)
    # dnp3_master.shutdown()
    # exit()

if __name__ == '__main__':
    main()