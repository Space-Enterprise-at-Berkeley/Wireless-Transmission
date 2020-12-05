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
        2 : [[2,2,"Voltage"], [2,3,"Power"], [2,4,"Energy Consumed"]],
        4 : [[3,0,"Lox Tank Temp"], [3,1,"Chamber 1"], [3,2,"Chamber 2"], [3,3,"Chamber 2"]]
}

tab_graph_titles = [['LOX Tank', 'Prop Tank', 'LOX Injector', 'Prop Injector'],['High Pressure'],['LOX Tree', 'LOX Heater', 'Voltage', 'Power', 'Energy Consumed',''],['Lox Tank Temp','Chamber Temp 1','Chamber Temp 2','Chamber Temp 3']]

sensor_ids = sensor_id_to_name.keys()

valve_name_to_id = {
        "lox_2_way"     : 20,
        "lox_5_way"     : 21,
        "lox_gems"      : 22,
        "prop_2_way"    : 23,
        "prop_5_way"    : 24,
        "prop_gems"     : 25,
        "high_pressure" : 26,
        "both_5_way"    : 28

}
