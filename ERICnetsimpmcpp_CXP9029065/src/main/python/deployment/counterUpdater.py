#!/usr/bin/python

import os, sys
import json

file_ = "/netsim_users/pms/bcp_templates/data_ecs_dir/ESC/22-Q3-V5/SDN_NODE_DATE.xml"
json_file = "/netsim_users/pms/etc/data.json"


MO_counter_list = { "SDN=0,PowerManager=1,PowerInput=grid" : [ "runTime", 0 ],
                    "SDN=0,PowerManager=1,PowerInput=gen" : [ "runTime", 0 ],
                    "SDN=0,PowerManager=1,PowerInput=gen,DieselGenerator=1,FuelTank=1" : [ "level", 100 ]
}

resultant_dict = []

def read_template():
    line_access = False
    attribute_dict = {}

    if not os.path.isfile(file_):
        print("Warning: "+file_+" not exist!")
        sys.exit()

    with open(file_, 'r') as fp:
        # read all lines in a list
        for num, line in enumerate(fp, 1):
            # check if string present on a current line
            if line_access:
                if attribute_dict[MO_counter_list[MO_key][0]] in line:
                    line_access = False
                    counter_value(MO_key,num)
                    attribute_dict = {}
            if "measValue" in line:
                for key in MO_counter_list.keys():
                    if key in line.split('"'):
                        line_access = True
                        MO_key = key
            if "measType" in line:
                attribute = line.split(">")[1].split("<")[0]
                p_id = line.split(">")[0].split()[-1]
                attribute_dict[attribute]=p_id
    create_JSON(resultant_dict)
    print("Info: /netsim_users/pms/etc/data.json was created")

def help_message():
    print '\npython /netsim_users/auto_deploy/bin/counterUpdater.py --showValues \n\nOR\n\npython /netsim_users/auto_deploy/bin/counterUpdater.py --updateCounter'
    sys.exit()

def show_values():
    if not os.path.isfile(json_file):
        print("Warning: "+json_file+" doesn't exists")
        sys.exit()

    with open(json_file) as f:
        resultant_dict = json.load(f)

    for item in resultant_dict:
        print("\""+item["MO"]+"\" current counter value : "+str(item["Value"]))


def counter_value(MO_key,num):
    resultant_dict.append({ "MO" : MO_key, "Attribute" : MO_counter_list[MO_key][0], "line" : num, "Value" : MO_counter_list[MO_key][1] })

def create_JSON(resultant_dict):
    jsonString = json.dumps(resultant_dict)
    jsonFile = open(json_file, "w")
    jsonFile.write(jsonString)
    jsonFile.close()

def update_counter():
    if not os.path.isfile(json_file):
        print("Warning: "+json_file+" doesn't exists")
        sys.exit()
    
    with open(json_file) as f:
        resultant_dict = json.load(f)
    update_dict = []
    reference_value = [ item["Value"] for item in resultant_dict if "FuelTank" in item["MO"] ][0]
    value_1 = abs(abs(abs(reference_value-1-100)%96)-100)
    value_2 = abs(((value_1+3)//4)-25)%24
    for key in resultant_dict:
        if "FuelTank" in key["MO"]:
            key["Value"] = value_1
        else:
            key["Value"] = value_2
        update_dict.append(key)
     
    create_JSON(update_dict)

def main():
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]

        for opt in arguments:
            if opt in ('-h', '--help'):
                help_message()
            elif opt in ('-u', '--updateCounter' ):
                update_counter()
            elif opt in ('-c', '--createJson' ):
                read_template()
            elif opt in ('-s', '--showValues'):
                show_values()
            else:
                help_message()
    else:
        help_message()

if __name__ == '__main__':
    main()
