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
# Version no    :  OSS
# Purpose       :  The purpose of this script to generate "EUtranCellData.txt" file for LTE nodes
# Jira No       :  EQEV-47447 
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3311326/ 
# Description   :  Created the script as a part of the netsim stub
# Date          :  08/02/2018
# Last Modified :  sudheep.mandava@tcs.com 
####################################################

import os
import sys
from subprocess import Popen
import xml.etree.ElementTree as ET
sys.path.append('/netsim/bin/')
from eniq_stats_cfg import *
from string_constants import *
from common_functions import *
sys.path.append('/netsim_users/auto_deploy/bin/')
from confGenerator import getCurrentDateTime, run_shell_command
from collections import defaultdict, OrderedDict
from itertools import islice, izip
import logging
from datetime import datetime
logfilename =  __file__.split("/")
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(name)-12s %(levelname)s:%(message)s',datefmt = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),filename='/netsim_users/pms/logs/netsim_stub_logs/' + logfilename[-1] + '.log',filemode='w')
logger = logging.getLogger(__file__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)s:%(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

mo_csv_map = defaultdict(lambda : defaultdict(list))


def createCsvfilemap():
    ne_type_with_mim_ver = ""
    cmd = "cat " + MO_CSV_FILE + " | sed 's/ //g' | sed -n '1!p'"
    csv_data_list = filter(None, run_shell_command(cmd).strip())
    csv_data_list = csv_data_list.split()
    for data in csv_data_list:
        attrs = data.split(',')
        if attrs[0]:
            ne_type_with_mim_ver = attrs[0] + COLON + attrs[1]
        if len(attrs) > 3:
            for index in range(3, len(attrs)):
                mo_csv_map[ne_type_with_mim_ver][attrs[2]].append(attrs[index])


def writeTopology(topology_file, eutran_file, node_list, node_type, sim_ver, nb_iot_cell):
    cmd = "cat " +  eutran_file + " > " + topology_file
    os.system(cmd)
    cell_list = [1,3,6,12]
    with open(topology_file, 'a') as topology:
        node_list.sort()
        for ne_type_with_mim_ver, relation_dict in mo_csv_map.iteritems():
            if node_type == "PRBS":
                node_type = "MSRBS-V1"
            if node_type in ne_type_with_mim_ver and sim_ver in ne_type_with_mim_ver:
                for relation, instances in relation_dict.iteritems():
                    for node_name in node_list:
                        cmd = "cat " + eutran_file + " | grep " + node_name + " | wc -l"
                        node_cell_count = filter(None, run_shell_command(cmd).strip())
                        for cell_number in range(1, int(node_cell_count)+1):
                            for cell in cell_list:
                                if int(node_cell_count) == cell:
                                    if cell_number == 1 and nb_iot_cell == "Yes" and int(node_cell_count) != 1:
                                        continue
                                    for mo_value in range(1, int(instances[cell_list.index(cell)])+1):
                                        updated_mo_value = int(node_cell_count)
                                        updated_mo_value += mo_value
                                        data = "ManagedElement=" + node_name + ",ENodeBFunction=1,EUtranCellFDD=" + node_name + "-" + str(cell_number) + ",EUtranFreqRelation=123,"+ relation + "=" + str(updated_mo_value)
                                        topology.write(data + "\n")

def writeEUtranCellData(eutran_file, cell_node_map, nb_iot_cell, node_type): 
    '''This method is used generate Eutrandata file for LTE Nodes by reading parameters simulation 
       name , node_type , nodes_ON etc ... from the user_input.xml and generate the file in /netsim/netsimdir/<LTE Simulation>/SimNetRevision/EUtranCellData.txt'''
    with open(eutran_file, 'w') as f:
        for cellcategory , nodes in cell_node_map.iteritems():  
            for node_name in nodes:
                for current_cell in range(1,cellcategory+1):
                    cell_type = ",ENodeBFunction=1,EUtranCellFDD="
                    if current_cell == 1 and nb_iot_cell == "Yes" and cellcategory != 1:
                        cell_type = ",ENodeBFunction=1,NbIotCell="
                    if node_type == "ERBS":
                        eutranCellData =  ERBS_FDN_OSS + node_name + ',ManagedElement=' + node_name + cell_type + node_name + "-" + str(current_cell)
                    elif node_type == "PRBS":
                        eutranCellData =  LTE_MSRBS_V1_FDN_OSS + node_name + ',ManagedElement=' + node_name + cell_type + node_name + "-" + str(current_cell)
                    elif node_type == "MSRBS-V2":
                        eutranCellData =  LTE_MSRBS_V2_FDN_OSS  + node_name + ',ManagedElement=' + node_name + cell_type + node_name + "-" + str(current_cell)        
                    f.write(eutranCellData + "\n")

def cellNodeDictonary(node_list,node_per_cells_list):
    '''This function returns a cellnode map which contains cellcategory as key and no of nodes per category is value'''
    cell_category = [1,3,6,12]
    node_per_cells_list = map(int,node_per_cells_list)
    slicednodelist = iter(node_list)
    node_cells_list = [list(islice(slicednodelist, 0, i)) for i in node_per_cells_list]
    cell_map = dict(izip(cell_category,node_cells_list))
    cell_map_ordered = OrderedDict(sorted(cell_map.items()))
    return cell_map_ordered

def main():
    logger.info('Creating CSV File Map for mo_cfg.csv')
    createCsvfilemap()

    if not os.path.exists(USER_INPUT_XML):
        logger.error(USER_INPUT_XML + ' does not exist. Exiting the program')
        sys.exit(1)
    user_input = ET.parse(USER_INPUT_XML)
    root = user_input.getroot()
    for Simulation in root.findall('Simulation'):
        try:
            simulationName = Simulation.get('name')
            if "RNC" in simulationName and "LTE" in simulationName:
                 continue
            if "LTE" in simulationName:
                 logger.info('Parsing User input xml for this' + simulationName)
                 eutranCellFilePath = NETSIM_DIR + simulationName + "/SimNetRevision/"
                 if not os.path.exists(eutranCellFilePath):
                     cmd = "mkdir -p " + eutranCellFilePath
                     os.system(cmd)
                 eutran_file = eutranCellFilePath + EUTRANCELLDATAFILE
                 topology_file = eutranCellFilePath + TOPOLOGYFILE
                 node_type = Simulation.find('node_type').text
                 sim_ver = Simulation.find('sim_mim_ver').text
                 sim_ver = sim_ver.replace("_" , "").upper()
                 node_prefix = Simulation.find('node_prefix').text
                 no_of_nodes = Simulation.find('no_of_nodes').text
                 node_list = generateNodelist(node_prefix,no_of_nodes)  
                 nb_iot_cell = Simulation.find('nb_iot_cell').text
                 node_per_cells = Simulation.find('node_per_cell').text
                 node_per_cells_list = node_per_cells.split(',')
                 cell_node_map = cellNodeDictonary(node_list,node_per_cells_list)
                 writeEUtranCellData(eutran_file, cell_node_map, nb_iot_cell, node_type)
                 writeTopology(topology_file, eutran_file, node_list, node_type, sim_ver, nb_iot_cell)
        except:
             logger.error("This simulation " + simulationName + " " + EUTRANCELLDATAFILE + " and " + TOPOLOGYFILE + " were not created")
             pass 

if __name__ == '__main__': main()
