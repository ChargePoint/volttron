MESA-ESS data converter
-----------------------

This directory contains source data and scripts for building
a point definition file (mesa_points.config) and a function
definition file (mesa_functions.config) based on information
published on the MESA-ESS standards web page,
http://mesastandards.org/mesa-ess-2016/.

The source data, scraped from the MESA-ESS point spreadsheet and
the Draft MESA-ESS Specification, lives in **mesa_points.xlsx**
and **mesa_functions.xlsx**. 

To run a script that processes this source data, producing 
**mesa_points.config** and **mesa_functions.yaml** files for use by 
DNP3Agent and MesaAgent, use:

    $ python data_converter.py

After running the script to build the files (and then editing the
files to satisfy specific project needs, if necessary), the definitions
can be put to use by loading them into the agent's VOLTTRON config 
store as follows (this example uses the agent ID of a MesaAgent):

    $ volttron-ctl config store mesaagent mesa_points <path>/mesa_points.config
    $ volttron-ctl config store mesaagent mesa_functions <path>/mesa_functions.config

Observed issues with MESA-ESS data
----------------------------------

The source data scraped from the MESA-ESS standards web page included 
various issues that had to be addressed and/or worked around by the data
converter, including:

1. The worksheets in the DNP3 Point Spreadsheet use multi-line formatting 
in the "Point Index" header cell -- i.e., a soft carriage return has been 
inserted in it. This defeats software attempts to convert the data to 
properly-headed CSV format. The scraped worksheets were hand-edited to 
remove the soft carriage returns.

2. Function definitions have been created based on the contents of
tables in the MESA-ESS Specification (and each function has a "reference" 
property identifying that spec's table number). The spec lacks tables defining
two essential MESA elements: curves and schedules. New function 
definitions have been created to define curve and schedule behavior.

3. The "Unique String" column in the DNP3 Point Spreadsheet often contains
an IEC 61850 field ID that serves as a point's unique name. Due to the
following limitations, data_converter often must adjust or substitute for
this Unique String in order to produce a unique DNP3 point name:
    - The Unique String column is empty for many rows.
    - The contents of the Unique String column are not always unique.
    - The contents of the Unique String column are not always an IEC 61850
      field ID.

4. The tables in the MESA-ESS Specification's function definitions have an
"IEC 61850" column. It often contains an IEC 61850 field ID linking the function step
to a DNP3 point's Unique String in the DNP3 Point Spreadsheet. Due to the 
following limitations, data_converter must often adjust a given step's
point name:
    - The IEC 61850 column sometimes contains a phrase instead of a field ID.
    - The IEC 61850 column sometimes contains a non-unique field ID.
    - The IEC 61850 column often contains a field ID that is missing from the spreadsheet.
    - The IEC 61850 column sometimes contains the field ID of an input point.
      In the 8minutenergy/Kisensum implementation, all function steps should 
      reference output point names.

5. data_converter makes certain assumptions about the MESA-ESS source data.
All point definitions that it produces are assigned the following properties:
    - All analog input points are configured as DNP3 group 30, variation 2.
    - All analog output points are configured as DNP3 group 40, variation 2.
    - All binary input points are configured as DNP3 group 1, variation 2.
    - All binary output points are configured as DNP3 group 2, variation 2.
    - All points are configured as DNP3 event level 2.
    - All array points are configured with a maximum of 100 rows (i.e., 100
      is the number of DNP3 index offsets that are reserved for point values
      belonging to each column of the array).

6. The 8minutenergy/Kisensum MESA implementation extends function definitions 
to include an "action" property on each function step, causing an outstation to 
perform certain additional operations when a function step is received. The most 
important of these "action" values is "publish". If a step with a "publish" action 
is received by the outstation, it publishes all of the function's
contents (so far) to other agents in its environment. data_converter
sets the "publish" action for one step in each defined function.

7. The 8minutenergy/Kisensum MESA implementation supports array and selector-block
functionality by defining extra properties on certain point definitions. This
includes setting each array's dimensions and column headers as well as each
selector block's range of point indexes. data_converter sets these 
special point properties as it converts the data in the spreadsheet.
