"""
GUI.py
Define import numberical and text ids, and relate them to "printable" names, for valves and sensors
on Eureka-1. Based on Packet definitions in E-1 Components (https://docs.google.com/spreadsheets/d/1xNmjrb5a28FfVg-MG9jUBRiPyfdkjo7HiqPWP41N_IQ/edit#gid=998950668)

Classes:

    N/A

Functions:

    N/A

Misc variables:

    sensor_name_to_text
    sensor_name_to_id
    valve_name_to_id

"""


sensor_name_to_text = {
        "low_pt"    : "Low Pressure",
        "high_pt"   : "High Pressure",
        "temp"      : "Temperature",
        "load_cell" : "Load Cell"
}


sensor_name_to_id = {
            "temperature"               : 0,
            "pressure"                  : 1,
            "battery"                   : 2,
}

sensor_id_to_name = {
        0 : "temperature",
        1: "pressure",
        2: "battery"
}

sensor_graph_mapping = {
        "temperature" : [[2,0,"LOX Tree"], [2,1,"LOX Heater"]],
        "pressure" : [[0,0,"LOX Tank"], [0,1,"Prop Tank"], [0,2,"Lox Injector"], [0,3,"Prop Injector"], [0,4,"High Pressure"]],
        "battery" : [[2,2,"Voltage"], [2,3,"Power"], [2,4,"Energy Consumed"]]
}

sensor_id_graph_mapping = {
        0 : [[2,0,"LOX Tree"], [2,1,"LOX Heater"]],
        1 : [[0,0,"LOX Tank"], [0,1,"Prop Tank"], [0,2,"Lox Injector"], [0,3,"Prop Injector"], [1,0,"High Pressure"]],
        2 : [[2,2,"Voltage"], [2,3,"Power"], [2,4,"Energy Consumed"]]
}

tab_graph_titles = [['LOX Tank', 'Prop Tank', 'LOX Injector', 'Prop Injector'],['High Pressure'],['LOX Tree', 'LOX Heater', 'Voltage', 'Power', 'Energy Consumed','']]

sensor_name_to_id = {
            "lox_injector"              : 1,
            "prop_injector"             : 2,
            "lox_tank"                  : 3,
            "prop_tank"                 : 4,
            "pressurant"                : 5,
            "temp"                      : 6,
            "GPS"                       : 7,
            "GPS Aux"                   : 8,
            "barometer"                 : 9,
            "load_cell_left"             : 10,
            "load_cell_right"            : 11,
            "board"                     : 12,
            "radio"                     : 13,
            "temp1"                     : 14,
            "temp2"                     : 15,
            "temp3"                     : 16,
            "temp4"                     : 17,
            "temp5"                     : 18,
            "temp6"                     : 19,
}

sensor_id_to_name = {
        1 : "lox_injector" ,
        2 : "prop_injector" ,
        3 : "lox_tank" ,
        4 : "prop_tank" ,
        5 : "high_pt",
        6 : "temp",
        7 : "GPS",
        8 : "GPS Aux",
        9 : "barometer",
        10 : "load_cell_left" ,
        11 : "load_cell_right",
        12 : "board",
        13 : "radio",
        14 : "temp1",
        15 : "temp2",
        16 : "temp3",
        17 : "temp4",
        18 : "temp5",
        19 : "temp6",
        40 : "load_cell_1",
        41 : "load_cell_2"
}

sensor_ids = sensor_id_to_name.keys()

valve_name_to_id = {
        "lox_2_way"     : 20,
        "lox_5_way"     : 21,
        "lox_gems"      : 22,
        "prop_2_way"    : 23,
        "prop_5_way"    : 24,
        "prop_gems"     : 25,
        "high_pressure" : 26
}
