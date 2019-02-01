from pydnp3 import opendnp3

DEFAULT_POINT_TOPIC = 'dnp3/point'
DEFAULT_OUTSTATION_STATUS_TOPIC = 'mesa/outstation_status'
DEFAULT_LOCAL_IP = "0.0.0.0"
DEFAULT_PORT = 20000

# StepDefinition.fcode values:
DIRECT_OPERATE = 'direct_operate'       # This is actually DIRECT OPERATE / RESPONSE
SELECT = 'select'                       # This is actually SELECT / RESPONSE
OPERATE = 'operate'                     # This is actually OPERATE / RESPONSE
READ = 'read'
RESPONSE = 'response'

# PointDefinition.action values:
PUBLISH = 'publish'
PUBLISH_AND_RESPOND = 'publish_and_respond'

# Some PointDefinition.type values
POINT_TYPE_ARRAY = 'array'
POINT_TYPE_SELECTOR_BLOCK = 'selector_block'
POINT_TYPE_ENUMERATED = 'enumerated'
POINT_TYPES = [POINT_TYPE_ARRAY, POINT_TYPE_SELECTOR_BLOCK, POINT_TYPE_ENUMERATED]

# Some PointDefinition.point_type values:
DATA_TYPE_ANALOG_INPUT = 'AI'
DATA_TYPE_ANALOG_OUTPUT = 'AO'
DATA_TYPE_BINARY_INPUT = 'BI'
DATA_TYPE_BINARY_OUTPUT = 'BO'

# PointDefinition.variation
# variation = 1: 32 bit, variation = 2: 16 bit
DEFAULT_VARIATION = 2

# PointDefinition.group
DEFAULT_GROUP_BY_DATA_TYPE = {
    DATA_TYPE_BINARY_INPUT:  1,
    DATA_TYPE_BINARY_OUTPUT: 10,
    DATA_TYPE_ANALOG_INPUT:  30,
    DATA_TYPE_ANALOG_OUTPUT: 40
}

# PointDefinition.event_class
DEFAULT_EVENT_CLASS = 2

# Default event group and variation for each of these types, in case they weren't spec'd for a point in the data file.
EVENT_DEFAULTS_BY_DATA_TYPE = {
    DATA_TYPE_ANALOG_INPUT: {'group': 32, 'variation': 3},
    DATA_TYPE_ANALOG_OUTPUT: {'group': 42, 'variation': 3},
    DATA_TYPE_BINARY_INPUT: {'group': 2, 'variation': 1},
    DATA_TYPE_BINARY_OUTPUT: {'group': 11, 'variation': 1}
}

EVENT_CLASSES = {
    0: opendnp3.PointClass.Class0,
    1: opendnp3.PointClass.Class1,
    2: opendnp3.PointClass.Class2,
    3: opendnp3.PointClass.Class3
}

GROUP_AND_VARIATIONS = {
    '1.1': opendnp3.StaticBinaryVariation.Group1Var1,
    '1.2': opendnp3.StaticBinaryVariation.Group1Var2,
    '2.1': opendnp3.EventBinaryVariation.Group2Var1,
    '2.2': opendnp3.EventBinaryVariation.Group2Var2,
    '2.3': opendnp3.EventBinaryVariation.Group2Var3,
    '3.2': opendnp3.StaticDoubleBinaryVariation.Group3Var2,
    '4.1': opendnp3.EventDoubleBinaryVariation.Group4Var1,
    '4.2': opendnp3.EventDoubleBinaryVariation.Group4Var2,
    '4.3': opendnp3.EventDoubleBinaryVariation.Group4Var3,
    '10.2': opendnp3.StaticBinaryOutputStatusVariation.Group10Var2,
    '11.1': opendnp3.EventBinaryOutputStatusVariation.Group11Var1,
    '11.2': opendnp3.EventBinaryOutputStatusVariation.Group11Var2,
    '20.1': opendnp3.StaticCounterVariation.Group20Var1,
    '20.2': opendnp3.StaticCounterVariation.Group20Var2,
    '20.5': opendnp3.StaticCounterVariation.Group20Var5,
    '20.6': opendnp3.StaticCounterVariation.Group20Var6,
    '21.1': opendnp3.StaticFrozenCounterVariation.Group21Var1,
    '21.2': opendnp3.StaticFrozenCounterVariation.Group21Var2,
    '21.5': opendnp3.StaticFrozenCounterVariation.Group21Var5,
    '21.6': opendnp3.StaticFrozenCounterVariation.Group21Var6,
    '21.9': opendnp3.StaticFrozenCounterVariation.Group21Var9,
    '21.10': opendnp3.StaticFrozenCounterVariation.Group21Var10,
    '22.1': opendnp3.EventCounterVariation.Group22Var1,
    '22.2': opendnp3.EventCounterVariation.Group22Var2,
    '22.5': opendnp3.EventCounterVariation.Group22Var5,
    '22.6': opendnp3.EventCounterVariation.Group22Var6,
    '23.1': opendnp3.EventFrozenCounterVariation.Group23Var1,
    '23.2': opendnp3.EventFrozenCounterVariation.Group23Var2,
    '23.5': opendnp3.EventFrozenCounterVariation.Group23Var5,
    '23.6': opendnp3.EventFrozenCounterVariation.Group23Var6,
    '30.1': opendnp3.StaticAnalogVariation.Group30Var1,
    '30.2': opendnp3.StaticAnalogVariation.Group30Var2,
    '30.3': opendnp3.StaticAnalogVariation.Group30Var3,
    '30.4': opendnp3.StaticAnalogVariation.Group30Var4,
    '30.5': opendnp3.StaticAnalogVariation.Group30Var5,
    '30.6': opendnp3.StaticAnalogVariation.Group30Var6,
    '32.1': opendnp3.EventAnalogVariation.Group32Var1,
    '32.2': opendnp3.EventAnalogVariation.Group32Var2,
    '32.3': opendnp3.EventAnalogVariation.Group32Var3,
    '32.4': opendnp3.EventAnalogVariation.Group32Var4,
    '32.5': opendnp3.EventAnalogVariation.Group32Var5,
    '32.6': opendnp3.EventAnalogVariation.Group32Var6,
    '32.7': opendnp3.EventAnalogVariation.Group32Var7,
    '32.8': opendnp3.EventAnalogVariation.Group32Var8,
    '40.1': opendnp3.StaticAnalogOutputStatusVariation.Group40Var1,
    '40.2': opendnp3.StaticAnalogOutputStatusVariation.Group40Var2,
    '40.3': opendnp3.StaticAnalogOutputStatusVariation.Group40Var3,
    '40.4': opendnp3.StaticAnalogOutputStatusVariation.Group40Var4,
    '42.1': opendnp3.EventAnalogOutputStatusVariation.Group42Var1,
    '42.2': opendnp3.EventAnalogOutputStatusVariation.Group42Var2,
    '42.3': opendnp3.EventAnalogOutputStatusVariation.Group42Var3,
    '42.4': opendnp3.EventAnalogOutputStatusVariation.Group42Var4,
    '42.5': opendnp3.EventAnalogOutputStatusVariation.Group42Var5,
    '42.6': opendnp3.EventAnalogOutputStatusVariation.Group42Var6,
    '42.7': opendnp3.EventAnalogOutputStatusVariation.Group42Var7,
    '42.8': opendnp3.EventAnalogOutputStatusVariation.Group42Var8,
    '50.4': opendnp3.StaticTimeAndIntervalVariation.Group50Var4,
    '121.1': opendnp3.StaticSecurityStatVariation.Group121Var1,
    '122.1': opendnp3.EventSecurityStatVariation.Group122Var1,
    '122.2': opendnp3.EventSecurityStatVariation.Group122Var2
}

DATA_TYPES_BY_GROUP = {
    # Single-Bit Binary: See DNP3 spec, Section A.2-A.5 and Table 11-17
    1: DATA_TYPE_BINARY_INPUT,    # Binary Input (static): Reporting the present value of a single-bit binary object
    2: DATA_TYPE_BINARY_INPUT,    # Binary Input Event: Reporting single-bit binary input events and flag bit changes
    # Double-Bit Binary: See DNP3 spec, Section A.4 and Table 11-15
    3: 'Double Bit Binary',       # Double-Bit Binary Input (static): Reporting present state value
    4: 'Double Bit Binary',       # Double-Bit Binary Input Event: Reporting double-bit binary input events and flag bit changes
    # Binary Output: See DNP3 spec, Section A.6-A.9 and Table 11-12
    10: DATA_TYPE_BINARY_OUTPUT,  # Binary Output (static): Reporting the present output status
    11: DATA_TYPE_BINARY_OUTPUT,  # Binary Output Event: Reporting changes to the output status or flag bits
    12: DATA_TYPE_BINARY_OUTPUT,  # Binary Output Command: Issuing control commands
    13: DATA_TYPE_BINARY_OUTPUT,  # Binary Output Command Event: Reporting control command was issued regardless of its source
    # Counter: See DNP3 spec, Section A.10-A.13 and Table 11-13
    20: 'Counter',                # Counter: Reporting the count value
    21: 'Counter',                # Frozen Counter: Reporting the frozen count value or changed flag bits
    22: 'Counter',                # Counter Event: Reporting counter events
    23: 'Counter',                # Frozen Counter Event: Reporting frozen counter events
    # Analog Input: See DNP3 spec, Section A.14-A.18 and Table 11-9
    30: DATA_TYPE_ANALOG_INPUT,   # Analog Input (static): Reporting the present value
    31: DATA_TYPE_ANALOG_INPUT,   # Frozen Analog Input (static): Reporting the frozen value
    32: DATA_TYPE_ANALOG_INPUT,   # Analog Input Event: Reporting analog input events or changes to the flag bits
    33: DATA_TYPE_ANALOG_INPUT,   # Frozen Analog Input Event: Reporting frozen analog input events
    34: DATA_TYPE_ANALOG_INPUT,   # Analog Input Reporting Deadband (static): Reading and writing analog deadband values
    # Analog Output: See DNP3 spec, Section A.19-A.22 and Table 11-10
    40: DATA_TYPE_ANALOG_OUTPUT,  # Analog Output Status (static): Reporting present value of analog outputs
    41: DATA_TYPE_ANALOG_OUTPUT,  # Analog Output (command): Controlling analog output values
    42: DATA_TYPE_ANALOG_OUTPUT,  # Analog Output Event: Reporting changes to the analog output or flag bits
    43: DATA_TYPE_ANALOG_OUTPUT,  # Analog Output Command Event: Reporting output points being commanded from any source
    # Time and Date: See DNP3 spec, Section A.23-A.25
    50: 'Time And Date',
    51: 'Time And Date',          # Time and Date Common Time-of-Occurrence
    52: 'Time And Date',          # Time Delay
    # Class Objects: See DNP3 spec, Section A.26
    60: 'Class Objects',
    # File-Control: See DNP3 spec, Section A.27
    70: 'File-Control',
    # Information Objects: See DNP3 spec, Section A.28-A.31
    80: 'Internal Indications',
    81: 'Device Storage',
    82: 'Device Profile',
    83: 'Data Set Registration',
    # Data Set Objects: See DNP3 spec, Section A.32-A.35
    85: 'Data Set Prototype',
    86: 'Data Set Descriptor',
    87: 'Data Set',
    88: 'Data Set Event',
    # Application & Status of Operation Information Objects: See DNP3 spec, Section A.36-A.37
    90: 'Application',
    91: 'Status of Requested Operation',
    # Floating-Point (Obsolete): See DNP3 spec, Section A.38
    100: 'Floating-Point',
    # Numeric Static Objects: See DNP3 spec, Section A.39-A.40
    101: 'BCD',                         # Device-dependent values in Binary-Coded Decimal form (Table 11-11)
    102: 'Unsigned Integer',
    # Octet String: See DNP3 spec, Section A.41-A.42 and Table 11-16
    110: 'Octet String',         # To convey the present value
    111: 'Octet String',         # Reporting an octet string event
    # Virtual Terminal: See DNP3 spec, Section A.43-A.44 and Table 11-18
    112: 'Virtual Terminal',     # Conveying data to the command interpreter at the outstation
    113: 'Virtual Terminal',     # Conveying data from the command interpreter at the outstation
    # Security: See DNP3 spec, Section A.45
    120: 'Authentication',
    # Security Statistic: See DNP3 spec, Section A.46-A.47 and Table 11-20
    121: 'Security Statistic',   # Reporting the current value of the statistics
    122: 'Security Statistic'    # Reporting changes to the statistics
}
