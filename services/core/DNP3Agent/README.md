DNP3Agent is a VOLTTRON agent that handles DNP3 outstation communications.

DNP3Agent models a DNP3 outstation, communicating with a DNP3 master.

For further information about this agent and DNP3 communications, please see the VOLTTRON
DNP3 specification, located in VOLTTRON readthedocs 
under http://volttron.readthedocs.io/en/develop/specifications/dnp3_agent.html.

This agent can be installed from a command-line shell as follows:

    $ export VOLTTRON_ROOT=<your volttron install directory>
    $ export DNP3_ROOT=$VOLTTRON_ROOT/services/core/DNP3Agent
    $ cd $VOLTTRON_ROOT
    $ python scripts/install-agent.py -s $DNP3_ROOT -i dnp3agent -c $DNP3_ROOT/dnp3agent.config -t dnp3agent -f
