What the tests should do:

Control agents (DNP3TestAgent, MesaTestAgent):

-- whether or not Master is connected...
. Detect agent status
. Tell agent which functions are supported
. Test that functions are supported (get_point on support point)

-- when Master is connected...
. TBD

MesaAgent testing with combined Master and TestControlAgent resources -- sequence:

. Master reads point values (a FunctionTest)
. Master sends point values to Outstation/Agent
. Outstation publishes point values to ControlAgent
. ControlAgent asserts that correct point values are received

