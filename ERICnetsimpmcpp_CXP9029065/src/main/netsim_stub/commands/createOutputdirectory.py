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
# Purpose       :  This script will create required directories for netsim_stub  
# Jira No       :  EQEV-47447
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3311326/
# Description   :  OSS Emulator : Coding related to Stub
# Date          :  12/02/2018
# Last Modified :  sudheep.mandava@tcs.com
####################################################

import sys
import os
import xml.etree.ElementTree as ET
sys.path.append('/netsim_users/netsim_stub/commands/');
from string_constants import *
from common_functions import *
def createDirectories(root):
    '''This function will create the required directories for netsim_stub by using user configuration file''' 
    errorsimulations_list = []
    errorsimulations_str = ''
    for simulation in root.findall('Simulation'):
        try:
            os.system("mkdir -p " + NETSIM_DIR + simulation.get('name'))
            os.system("touch " + NETSIM_DIR + simulation.get('name') + "/simulation.netsimdb")
            node_prefix = simulation.find('node_prefix').text
            no_of_nodes = simulation.find('no_of_nodes').text
            node_list = generateNodelist(node_prefix,no_of_nodes) 
            stats_dir = "/c/pm_data"
            sim_name = simulation.get('name')
            for node in node_list:
                os.system("mkdir -p " + DB_DIR + sim_name + FILE_SEPERATOR + node + "/fs/" + stats_dir)
                if 'SGSN' not in sim_name:
                    if 'LTE' in sim_name or 'RNC' in sim_name:
                        cmd = "mkdir -p " + TMPFS_DIR + sim_name.split("-")[-1] + FILE_SEPERATOR + node + stats_dir
                        os.system(cmd)
                    else:
                         cmd = "mkdir -p " + TMPFS_DIR + sim_name + FILE_SEPERATOR + node + stats_dir
                         os.system(cmd)
        except:
                errorsimulations_list.append(simulation.get('name'))
                errorsimulations_str = ",".join([str(elem) for elem in errorsimulations_list])
    if errorsimulations_str == "" :
          errorsimulations_str = "0"
          errorsimulations_str = int(errorsimulations_str)
    print errorsimulations_str
    sys.exit(errorsimulations_str)
             

def main(argv):
    user_input = ET.parse(argv[1])
    root = user_input.getroot()
    createDirectories(root) 

if __name__ == "__main__":
   main(sys.argv)
