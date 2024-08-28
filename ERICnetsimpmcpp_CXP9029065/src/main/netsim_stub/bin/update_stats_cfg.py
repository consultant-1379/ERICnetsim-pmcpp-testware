#!/usr/bin/python

################################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 18.1
# Purpose       :  The script is responsible for updating eniq_stats_cfg
# Jira No       :  EQEV-45082
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3375564/ 
# Description   :  Handling for filename for OSS Simulator.
# Date          :  07/03/2018
# Last Modified :  sudheep.mandava@tcs.com
####################################################


import os
import xml.etree.ElementTree as ET
from eniq_stats_cfg import *
from string_constants import *


def main():
    user_input = ET.parse(USER_INPUT_XML)
    root = user_input.getroot()
    with open(PATH_CONFUGURATION, 'a') as f:
        for Simulation in root.findall('Simulation'):
            network = Simulation.find('network').text
            simulationName = Simulation.get('name')
            oss_dir = Simulation.find('oss_dir').text
            node_type = Simulation.find('node_type').text
            node_type = node_type.replace('-', '_')
            if "WCDMA" in network:
                if "RNC" in simulationName:
                    simulationName = simulationName.split("-")[-1]
                node_list = node_type.split(":")
                for node_type in node_list:
                    try:
                        link_var = network + "_" + node_type + "_LINK_PATH_OSS"
                        link_dir = eval(link_var)
                        if "RNC" in node_type:
                            #LINK_DIR_OSS variable describes path where symlinks will be made and REAL_FILE_OSS describes path where the link will point
                            data = simulationName + "_LINK_DIR_OSS=\""  + LINK_DIR + "/" + link_dir + "\"" + "\n" + simulationName + "_REAL_FILE_OSS=\"" + MOUNT_PATH + oss_dir + "/\""
                        else:
                            data = simulationName + "_" + node_type + "_LINK_DIR_OSS=\""  + LINK_DIR + "/" + link_dir + "\"" + "\n" + simulationName + "_" + node_type + "_REAL_FILE_OSS=\"" + MOUNT_PATH + oss_dir + "/\""
                        os.system("mkdir -p " + LINK_DIR + "/" + link_dir)
                        f.write(data + "\n")
                    except:
                        print("Unable to create link dir for" + simulationName)     
            else:
                try:
                    if "LTE" in simulationName:
                        simulationName = simulationName.split("-")[-1]
                    else:
                        simulationName = simulationName.replace('-','_') #FOR CORE NODES
                    if node_type == "PRBS":
                        node_type = "MSRBS_V1"
                    elif node_type == "M_MGw":
                        node_type = "MGW"
                    elif node_type == "MRFv":
                        node_type = "MRFV"
                    elif node_type == "ESAPC":
                        node_type = "SAPC"
                    elif node_type == "VBGF":
                        node_type = "MRSV"
                    if CORE in simulationName:
                        link_var = node_type + "_LINK_PATH_OSS"
                        realfile_path = node_type + "_REALFILE_PATH"
                        real_dir = eval(realfile_path)
                        os.system("mkdir -p " + real_dir)
                         
                    else:
                        link_var = network + "_" + node_type + "_LINK_PATH_OSS"
                    link_dir = eval(link_var)
                    data = simulationName + "_LINK_DIR_OSS=\""  + LINK_DIR + "/" + link_dir + "\"" + "\n" + simulationName + "_REAL_FILE_OSS=\"" + MOUNT_PATH + oss_dir + "/\""
                    os.system("mkdir -p " + LINK_DIR + "/" + link_dir)
                    f.write(data + "\n")
                except:
                    print("Unable to create link dir for" + simulationName)
            os.system(PERMISSION_COMMAND + "/ossrc/")
if __name__ == "__main__":
    main()
