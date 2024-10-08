#!/usr/bin/python
################################################################################
# COPYRIGHT Ericsson 2017
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 17.15
# Purpose       :  Script generates stats templates for CPP and COM/ECIM nodes
# Jira No       :  NSS-14660
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/2686691/
# Description   :  Removing dirSetup functionality
# Date          :  09/11/2017
# Last Modified :  mathur.priyank@tcs.com
####################################################

"""
Generates GenStats templates for both CPP and COM/ECIM nodes. MIM/MIB files are
extracted from NETSim installation on VM.

edits EutranCellFDD MO within the template configuration files with the predefined
Cell size for both CPP and COM/ECIM nodes

edits the NE configuration files MO content based on NE type for MSRBS-V2 nodes
"""
import os
import re
import math
import logging
import sys, getopt
from _collections import defaultdict
from confGenerator import getCurrentDateTime, run_shell_command
from DataAndStringConstants import EUTRANCELL_DATA_FILE as GEN_EUTRANCELL_DATA_FILE
from DataAndStringConstants import PMS_ETC_DIR
from GenericMethods import exit_logs

LOG_FILE = "/netsim/genstats/logs/genstats_templateGen.log"
format = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(filename=LOG_FILE, format=format, level=logging.INFO)


GSM = "GSM"
LTE = "LTE"
WCDMA = "WCDMA"
MIM_FILE_DIR = "/netsim/inst/zzzuserinstallation/mim_files/"
ECIM_FILE_DIR = "/netsim/inst/zzzuserinstallation/ecim_pm_mibs/"
CFG_FILE_DIR = "/netsim/genstats/xml_cfg/"
TEMPLATES_FILES_1MIN_DIR = "/netsim_users/pms/xml_templates/1/"
TEMPLATE_FILES_15MIN_DIR = "/netsim_users/pms/xml_templates/15/"
TEMPLATE_FILES_1440MIN_DIR = "/netsim_users/pms/xml_templates/1440/"
PM_COUNTERS_SCRIPT = "/netsim_users/pms/bin/getPmCounters"
CPPXMLGEN_SCRIPT = "/netsim_users/pms/bin/cppXmlgen"
ECIMXMLGEN_SCRIPT = "/netsim_users/pms/bin/ecimXmlgen"
SIM_DATA_FILE = "/netsim/genstats/tmp/sim_data.txt"
XML_FILE_DIR = "/netsim/genstats/xml_templates/1/"
ECIM_NODES_TYPES = ["CSCF", "MTAS", "SBG", "SGSN", "SPITFIRE", "MSRBS_V1", "MSRBS_V2", "ESAPC", "PRBS", "TCU03", "TCU04", "MRSV", "HSS_FE", "IPWORKS", "MRFV", "UPG", "WCG", "DSC", "VPP", "VRC", "RNNODE", "EME", "VTFRADIONODE", "5GRADIONODE", "R6274", "R6672", "R6675", "R6371", "R6471_1", "R6471_2"]
CPP_NODE_TYPES = ["ERBS", "RNC", "RBS", "RXI", "M_MGW"]
MSRBS_NE_TYPES = ["GSM", "LTE", "WCDMA"]
LTE_CELLS_PER_NODE = ["1", "3", "6", "12"]
EPG_FILE_TYPES = ['node', 'pgw', 'sgw']
EPG_RELEASE = ['16A', '16B']
WMG_RELEASE = ['16B']
RNC_CONFIGURATION = {0 : [1, 2, 3, 5, 7], 1 : [4, 6, 8, 9, 10], 2 : [11, 12, 13, 14, 15], 3: [16, 17, 18, 19, 20]}
node_cell_relation_file = "/netsim_users/pms/etc/.node_cell_relation_file"
TOPOLOGY_DATA_FILE = "/netsim_users/pms/etc/topology_info.txt"
relation_file = "/netsim_users/pms/etc/.cell_relation_file"
NODE_CELL_MAPPING = defaultdict(list)
sim_node_map = defaultdict(list)
sim_data_list = []
MO_CSV_FILE = "/netsim_users/reference_files/mo_cfg.csv"
mo_csv_map = defaultdict(lambda : defaultdict(list))
nrm_type = ''
core_nodes_mapping = False


def clear_existing_log_file(LOG_FILE):
    """ removes existing log entries

        Args:
           param1 (string): log file path
    """
    with open(LOG_FILE, 'w'):
        logging.info("starting template generation process")


def remove_directories(directories):
    """ deletes directories containing genstats config and template files

       Args:
          param1 (list): list of directories
    """
    for delete_dir in directories:
        logging.info("deleting " + delete_dir)
        os.system("rm -rf " + delete_dir)

def copy_files(source_file, destination_path, destination_file):
    if os.path.isdir(destination_path):
        print getCurrentDateTime() + ' INFO: Copying ' + source_file + ' >> ' + destination_path + destination_file
        logging.info('Copying ' + source_file + ' >> ' + destination_path + destination_file)
        os.system("cp -r " + source_file + " " + destination_path + destination_file)
    else:
        print getCurrentDateTime() + ' WARN: ' + destination_path + ' does not exist. Unable to copy ' + source_file + ' file.'
        logging.warn(destination_path + ' does not exist. Unable to copy ' + source_file + ' file.')


def create_directories(directories):
    """ creates directories required for genstats config and template files

        Args:
           param1 (list): list of directories
    """
    for create_dir in directories:
        logging.info("creating " + create_dir)
        os.system("mkdir -p " + create_dir)


def copy_template_files(source_dir, destination_dir):
    """ copies files from the specified source directory to the specified
            destination directory

        Args:
           param1 (string): source file path
           param2 (string): destination file path

    """
    os.system("cp -rp " + source_dir + ".  " + destination_dir)


def get_sim_data():
    """ retrieves simulation data from /netsim/genstats/tmp/sim_data.txt file

        Returns:
           list: sim data
    """
    try:
       sim_data_file = open(SIM_DATA_FILE, "r")
    except:
       logging.error("cannot find " + SIM_DATA_FILE)
    sim_data_list = sim_data_file.readlines()
    return sim_data_list


def get_eutran_nbiot_relation_for_node(sim_name):
    if NODE_CELL_MAPPING.has_key(sim_name):
        return NODE_CELL_MAPPING[sim_name]
    else:
        return LTE_CELLS_PER_NODE


def generate_ecim_cfg_map():
    """ maps ECIM cfg file names to associated MIM & MIB file names

        Args:
            param1 (list): simulation information

        Returns:
            dictionary : <cfg_file name, [MIM file name, MIB file name]>
    """
    ecim_cfg_map = {}
    cfg_file = ""
    for sim in sim_data_list:
         LTE_CELLS_CONF = []
         sim_data = sim.split();
         node_name = sim_data[3]
         sim_name = create_sim_name(sim_data, node_name)
         node_type = sim_data[5].upper()
         node_type = node_type.replace("-", "_")
         if node_type in ECIM_NODES_TYPES:
             mim_file = sim_data[13]
             mib_file = sim_data[15]
             mim_ver = sim_data[7].split("-")[0]

             if "SGSN" in node_type or "MSRBS_V2" in node_type or "PRBS" in node_type:
                 mim_ver = sim_data[7]

             if "SAPC" in node_type:
                 cfg_file = "sapc_counters_" + mim_ver + ".cfg"
                 ecim_cfg_map[cfg_file] = [mim_file, mib_file, sim_name]

             elif "PRBS" in node_type:
                 LTE_CELLS_CONF = get_eutran_nbiot_relation_for_node(sim_name)
                 for cell_size in LTE_CELLS_CONF:
                      cfg_file = "msrbs_v1_counters_" + mim_ver + "_" + cell_size.split('=')[-1] + "CELLS.cfg"
                      if len(cell_size.split('=')) > 1:
                          ecim_cfg_map[cfg_file] = [mim_file, mib_file, cell_size.split('=')[0]]
                      else:
                          ecim_cfg_map[cfg_file] = [mim_file, mib_file, sim_name]
                 cfg_file = "msrbs_v1_counters_" + mim_ver + ".cfg"
                 ecim_cfg_map[cfg_file] = [mim_file, mib_file, sim_name]

             elif "MSRBS_V2" in node_type:
                 for msrbs_type in MSRBS_NE_TYPES:
                     if "LTE" in msrbs_type:
                         LTE_CELLS_CONF = get_eutran_nbiot_relation_for_node(sim_name)
                         for cell_size in LTE_CELLS_CONF:
                             cfg_file = msrbs_type.lower() + "_" + node_type.lower() + "_counters_" + mim_ver + "_" + cell_size.split('=')[-1] + "CELLS.cfg"
                             if len(cell_size.split('=')) > 1:
                                 ecim_cfg_map[cfg_file] = [mim_file, mib_file, cell_size.split('=')[0]]
                             else:
                                 ecim_cfg_map[cfg_file] = [mim_file, mib_file, sim_name ]
                     cfg_file = msrbs_type.lower() + "_" + node_type.lower() + "_counters_" + mim_ver + ".cfg"
                     ecim_cfg_map[cfg_file] = [mim_file, mib_file, sim_name]
             else:
                 cfg_file = node_type.lower() + "_counters_" + mim_ver + ".cfg"
                 if not cfg_file:
                     continue
                 ecim_cfg_map[cfg_file] = [mim_file, mib_file, sim_name]
    return ecim_cfg_map


def create_sim_name(sim_data, node_name):
    sim_check = sim_data[1].split('-')[-1]
    if 'LTE' in sim_check and 'ERBS' in node_name:
        return sim_check
    elif 'RNC' in sim_check:
        return sim_check
    else:
        return sim_data[1]


def generate_cpp_cfg_map():
    """ maps CPP cfg file names to associated MIM file names

        Args:
            param1 (list): simulation information

        Returns:
            dictionary : <cfg_file name, MIM file name>
    """
    cpp_cfg_map = {}
    cfg_file = ""
    for sim in sim_data_list:
         LTE_CELLS_CONF = []
         sim_data = sim.split();
         node_name = sim_data[3]
         sim_name = create_sim_name(sim_data, node_name)
         node_type = sim_data[5].upper()
         node_type = node_type.replace("-", "_")

         if node_type in CPP_NODE_TYPES:
             mim_file = sim_data[13]
             mim_pattern = re.compile("([^_]\S?)_(\d+)_(\d+)")
             mim_ver_old = mim_pattern.search(mim_file).group()
             mim_ver = mim_ver_old.replace("_", ".")

             if "RNC" in node_type:
                 node_type = "TYPE_C_RNC"
             if "MGW" in node_type:
                 node_type = "MGW"
                 mim_ver = sim_data[7].split("-")[0]
             if "ERBS" in node_type:
                 LTE_CELLS_CONF = get_eutran_nbiot_relation_for_node(sim_name)
                 for cell_size in LTE_CELLS_CONF:
                     cfg_file = node_type.lower() + "_counters_" + mim_ver + "_" + cell_size.split('=')[-1] + "CELLS.cfg"
                     if len(cell_size.split('=')) > 1:
                         cpp_cfg_map[cfg_file] = [mim_file, cell_size.split('=')[0]]
                     else:
                         cpp_cfg_map[cfg_file] = [mim_file, sim_name ]
             cfg_file = node_type.lower() + "_counters_" + mim_ver + ".cfg"
             if not cfg_file:
                 continue
             cpp_cfg_map[cfg_file] = [mim_file, sim_name]
    return cpp_cfg_map


def edit_EUtranCellFDD_cell_size(cfg_file, node_name, topo_check, ne_type):
    """ Edits the EUtranCellFDD MO within the specified cfg_file with the associated
            cell size as defined in cfg_file name

        Args:
           param1 (string): cfg file name

    """
    EUTRAN_FILE = ''
    LTE_NODE_TYPE_LIST = ['ERBS', 'dg2ERBS', 'pERBS']
    LTE_RELATION_LIST = ['Cdma20001xRttCellRelation', 'EUtranCellRelation', 'GeranCellRelation', 'UtranCellRelation']

    cfg_file_path = CFG_FILE_DIR + cfg_file
    try:
        read_cfg_file = open(cfg_file_path, "r")
    except:
        logging.error("cannot find " + cfg_file_path)

    managed_objects = read_cfg_file.readlines()
    write_cfg_file = open(cfg_file_path, "w")

    if os.path.isfile(GEN_EUTRANCELL_DATA_FILE):
        EUTRAN_FILE = GEN_EUTRANCELL_DATA_FILE

    for managed_object in managed_objects:
        total_cell_count = 0
        cell_type = managed_object.split(',')[0]
        new_cell_value = '1'

        if cell_type == 'EUtranCellFDD':
            tdd_value = 0
            # if check for nbiot identification, if nbiot conf, then node name value comes in node_name variable else sim name value will come in variable
            if 'ERBS' in node_name:
                cmd = "cat " + EUTRAN_FILE + " | grep " + node_name + " | grep 'EUtranCellTDD=' | wc -l"
                tdd_value = int(run_shell_command(cmd).strip())
            new_cell_value = str(int(cfg_file.split("_")[-1].replace('CELLS.cfg', '').split(':')[0]) - tdd_value)

        elif cell_type == 'NbIotCell':
            if ":" in cfg_file:
                new_cell_value = cfg_file.split("_")[-1].replace('CELLS.cfg', '').split(':')[1]
            else:
                new_cell_value = '0'

        # This block only work when we need to map topology.
        elif topo_check:
            if any(cell_type == rel for rel in LTE_RELATION_LIST):
                if ':' in cfg_file:
                    total_cell_count = int(cfg_file.split('_')[-1].replace('CELLS.cfg', '').split(':')[0]) + int(cfg_file.split('_')[-1].replace('CELLS.cfg', '').split(':')[1])
                    new_cell_value = str(find_relation_count_for_cfg(relation_file, node_name, cell_type))
                else:
                    fdd_count = cfg_file.split('_')[-1].replace('CELLS.cfg', '')
                    total_cell_count = int(fdd_count)
                    node_list = get_uniq_node_list(EUTRAN_FILE)
                    for node in node_list:
                        if any(node_name + ne in node for ne in LTE_NODE_TYPE_LIST):
                            cmd = "cat " + EUTRAN_FILE + " | grep " + node + "- | wc -l"
                            node_cell_cnt = run_shell_command(cmd).strip()
                            if fdd_count == node_cell_cnt:
                                new_cell_value = str(find_relation_count_for_cfg(relation_file, node, cell_type))

                if ne_type == 'CPP':
                    new_cell_value = str(math.ceil(int(new_cell_value)/(total_cell_count * 1.0))).split('.')[0]

            elif cell_type != 'EUtranCellTDD':
                if NODE_CELL_MAPPING:
                    new_cell_value = str(find_mo_info_from_csv_map(retrieve_lte_sim_name(node_name), cell_type, cell_count_in_cfg_file(cfg_file)))
                else:
                    new_cell_value = str(find_mo_info_from_csv_map(node_name, cell_type, cell_count_in_cfg_file(cfg_file)))

        if new_cell_value != '1':
            if ne_type == 'CPP':
                new_cell_value = ',' + new_cell_value + ','
                managed_object = managed_object.replace(',1,', new_cell_value)
            else:
                new_cell_value = ',' + new_cell_value
                managed_object = managed_object.replace(',1', new_cell_value)


# Need to include TDD code in future
        write_cfg_file.write(managed_object)

    write_cfg_file.close()


def find_mo_info_from_csv_map(sim_name, cell_type, cfg_cell_count):
    mim_ver = ''
    node_type = ''
    index = 0
    key = ''
    other_mo_key = ''
    check = False

    for sim_info in sim_data_list:
        sim_data = sim_info.split()
        if 'LTE' in sim_name:
            if sim_name == sim_data[1].split('-')[-1]:
                index = retrieve_csv_index('LTE', cfg_cell_count)
                check = True
        elif 'RNC' in sim_name:
            if sim_name == sim_data[1].split('-')[-1]:
                if sim_data[5] == 'RNC':
                    index = retrieve_csv_index('RNC', sim_name)
                    check = True
        else:
            if sim_name == sim_data[1]:
                check = True

        if check:
            node_type = sim_data[5]
            mim_ver = sim_data[7]
            if 'RNC' in sim_name:
                if 'RBS' in node_type:
                    node_type += '(RNC)'
            break

    other_mo_key = node_type + ':Other_MO'

    if mo_csv_map.has_key(node_type + ':' + mim_ver):
        key = node_type + ':' + mim_ver
        return (return_value_from_csv_for_mo(key, other_mo_key, cell_type, index))
    elif mo_csv_map.has_key(node_type + ':default'):
        key = node_type + ':default'
        return (return_value_from_csv_for_mo(key, other_mo_key, cell_type, index))
    elif mo_csv_map.has_key(other_mo_key):
        if mo_csv_map.get(other_mo_key).has_key(cell_type):
            return int(mo_csv_map.get(other_mo_key).get(cell_type)[0])
        else:
            return 1
    else:
        return 1


def return_value_from_csv_for_mo(key, other_mo_key, cell_type, index):
    if mo_csv_map.get(key).has_key(cell_type):
        return int(mo_csv_map.get(key).get(cell_type)[index])
    elif mo_csv_map.has_key(other_mo_key):
        if mo_csv_map.get(other_mo_key).has_key(cell_type):
            return int(mo_csv_map.get(other_mo_key).get(cell_type)[0])
        else:
            return 1
    else:
        return 1


def retrieve_csv_index(sim_type, param):
    if sim_type == 'LTE':
        if param == '1':
            return 0
        elif param == '3':
            return 1
        elif param == '6':
            return 2
        else:
            return 3
    elif sim_type == 'RNC':
        number = int("{0:0=1d}".format(int(param.replace('RNC', ''))))
        for key_index, values in RNC_CONFIGURATION.iteritems():
            for value in values:
                if number == value:
                    return key_index
        return 4


def retrieve_lte_sim_name(node_name):
    for key, values in sim_node_map.iteritems():
        for value in values:
            if value == node_name:
                return key


def cell_count_in_cfg_file(cfg_file):
    ratio = cfg_file.split('_')[-1].replace('CELLS.cfg', '')
    if ':' in cfg_file:
        return str(int(ratio.split(':')[0]) + int(ratio.split(':')[1]))
    else:
        return ratio


def get_uniq_node_list(EUTRANCELL_DATA_FILE):
    """ This method will fetch unique LTE nodes from eutrancellfdd_list.txt.

        Arg : < text file >

        return : <uniq_node_list = ['node_1','node_2',..]>

    """
    uniq_node_list = "cat " + EUTRANCELL_DATA_FILE + " | rev | cut -d= -f1 | rev | cut -d- -f1 | sort -u | sed 's/ //g'"
    uniq_node_list = filter(None, run_shell_command(uniq_node_list).split())
    return uniq_node_list


def find_relation_count_for_cfg(relation_file, node_name, cell_type):
    rel_val = 0
    cmd = "cat " + relation_file + " | grep " + node_name + "- | grep -w " + cell_type + " | cut -d= -f4 | sed 's/ //g'"
    result = filter(None, run_shell_command(cmd).split())
    for value in result:
        rel_val += int(value)
    return rel_val


def generate_cpp_cfg_file(cfg_file, mim_file, node_name, topo_check):
    """ maps CPP cfg file names to associated MIM file names

        Args:
            param1 (string): MIM file name

        Returns:
            dictionary : <cfg_file name, MIM file name>
    """
    mim_file_path = MIM_FILE_DIR + mim_file
    cfg_file_path = CFG_FILE_DIR + cfg_file
    os.system(PM_COUNTERS_SCRIPT + " --xml " + mim_file_path + " --outputCfg " + cfg_file_path)

    if "CELLS" in cfg_file and "LTE" in node_name:
        edit_EUtranCellFDD_cell_size(cfg_file, node_name, topo_check, 'CPP')
    elif 'LTE' not in node_name and 'RBS' != cfg_file.split('_')[0].upper() and core_nodes_mapping:
        edit_cfg_file_for_core_nodes(cfg_file, node_name, 'CPP')

    try:
        os.path.isfile(cfg_file_path)
        logging.info(cfg_file + " created successfully")
    except:
        logging.error("Failed to create config file for: " + mim_file)


def generate_cpp_template_files(cfg_file, mim_file):
    """ generates CPP template files

        Args:
           param1 (string): cfg file name
           param2 (string): MIM file name

    """
    counter_file = cfg_file.replace(".cfg", ".xml")
    if os.path.isfile(TEMPLATE_FILES_15MIN_DIR + counter_file):
        logging.info(counter_file + " already exists")
        print counter_file + " already exists"
    else:
        cntrprop_file = cfg_file.replace(".cfg", ".cntrprop")
        mim_file_path = MIM_FILE_DIR + mim_file
        cfg_file_path = CFG_FILE_DIR + cfg_file
        counter_file_path = TEMPLATE_FILES_15MIN_DIR + counter_file
        cntrprop_file_path = TEMPLATE_FILES_15MIN_DIR + cntrprop_file
        os.system(CPPXMLGEN_SCRIPT + " -cfg " + cfg_file_path + " -mom " + mim_file_path + " -out " + counter_file_path + " -prop " + cntrprop_file_path)

    try:
        os.path.isfile(counter_file_path)
    except:
        logging.error("Failed to create config file for: " + mim_file)


def get_MSRBS_NE_MO_list(mib_file, node_type):
    """ get MO associated with a specfic node_type within  a given MIB file

        Args:
           param1 (string): mib_file name
           param2 (string): node_type

        Returns:
               list : MO list associated with the specified node_type
    """
    mib_file_path = ECIM_FILE_DIR + mib_file
    MSRBS_V2_MO_file_path = "/tmp/MSRBS_V2_MO.txt"
    os.system(ECIMXMLGEN_SCRIPT + " -mode m -mom " + mib_file_path + " -outCfg " + MSRBS_V2_MO_file_path)

    if node_type == GSM:
        mo_type = ",1,Grat"
    if node_type == LTE:
        mo_type = ",1,Lrat"
    if node_type == WCDMA:
        mo_type = ",1,Wrat"

    parse_file_command = "grep \"" + mo_type + "\" " + MSRBS_V2_MO_file_path
    managed_objects = os.popen(parse_file_command).read()
    managed_objects = managed_objects.replace(mo_type, "")
    node_type_MO_list = managed_objects.strip().split()
    return node_type_MO_list


def remove_multi_standard_MO_in_cfg_file(cfg_file, mib_file):
    """ removes the unnecessary MO's based on the NE type as specified in cfg_file
            i.e. if LTE NE type removes all WCDMA & GSM MO's defined in cfg_file

        Args:
           param1 (string): cfg file name

    """
    WCDMA_MO_list = get_MSRBS_NE_MO_list(mib_file, WCDMA)
    LTE_MO_list = get_MSRBS_NE_MO_list(mib_file, LTE)
    GSM_MO_list = get_MSRBS_NE_MO_list(mib_file, GSM)

    if LTE in cfg_file:
        excluded_MO_list = WCDMA_MO_list + GSM_MO_list
    if WCDMA in cfg_file:
        excluded_MO_list = LTE_MO_list + GSM_MO_list
    if GSM in cfg_file:
        excluded_MO_list = LTE_MO_list + WCDMA_MO_list

    cfg_file_path = CFG_FILE_DIR + cfg_file

    try:
        ecim_cfg_file = open(cfg_file_path, "r")
    except:
        logging.error("cannot find " + cfg_file_path)

    managed_objects = ecim_cfg_file.readlines()
    ecim_cfg_file.close()
    ecim_cfg_file = open(cfg_file_path, "w")

    for managed_object in managed_objects:
        if any(x in managed_object for x in excluded_MO_list):
            continue
        ecim_cfg_file.write(managed_object)
    ecim_cfg_file.close()

    try:
        os.path.isfile(cfg_file_path)
    except:
        logging.error("Failed to create config file: " + cfg_file)


def edit_cfg_file_for_core_nodes(cfg_file, sim_name, ne_type):

    cfg_file_path = CFG_FILE_DIR + cfg_file
    try:
        read_cfg_file = open(cfg_file_path, "r")
    except:
        logging.error("cannot find " + cfg_file_path)

    managed_objects = read_cfg_file.readlines()
    write_cfg_file = open(cfg_file_path, "w")

    for managed_object in managed_objects:

        attr_name = managed_object.split(',')[0]
        new_attr_value = '1'

        new_attr_value = str(find_mo_info_from_csv_map(sim_name, attr_name, '0'))

        if new_attr_value != '1':
            if ne_type == 'CPP':
                new_attr_value = ',' + new_attr_value + ','
                managed_object = managed_object.replace(',1,', new_attr_value)
            else:
                new_attr_value = ',' + new_attr_value
                managed_object = managed_object.replace(',1', new_attr_value)

        write_cfg_file.write(managed_object)

    write_cfg_file.close()


def generate_ecim_cfg_file(cfg_file, mib_file, node_name, topo_check):
    """ generates ECIM template file

        Args:
           param1 (string): cfg file name
           param2 (string): MIB file name

    """
    mib_file_path = ECIM_FILE_DIR + mib_file
    cfg_file_path = CFG_FILE_DIR + cfg_file
    os.system(ECIMXMLGEN_SCRIPT + " -mode c -mom " + mib_file_path + " -outCfg " + cfg_file_path)

    if "MSRBS_V2" in cfg_file:
        remove_multi_standard_MO_in_cfg_file(cfg_file, mib_file)

    if "CELLS" in cfg_file and "LTE" in node_name:
        edit_EUtranCellFDD_cell_size(cfg_file, node_name, topo_check, 'ECIM')
    elif 'RNC' not in node_name and 'LTE' not in node_name and core_nodes_mapping:
        edit_cfg_file_for_core_nodes(cfg_file, node_name, 'ECIM')

    try:
        os.path.isfile(cfg_file_path)
        logging.info(cfg_file + " created successfully")
    except:
        logging.error("Failed to create config file for: " + mib_file)


def generate_ecim_template_file(cfg_file, mim_file, mib_file):
    """ maps ECIM cfg file names to associated MIM file names

        Args:
           param1 (string): cfg_file name
           param2 (string): MIM file name
           param3 (string): MIB file name

    """
    counter_file = cfg_file.replace(".cfg", ".xml")
    if os.path.isfile(TEMPLATE_FILES_15MIN_DIR + counter_file):
        logging.info(counter_file + " already exists")
        print counter_file + " already exists"
    else:
        cntrprop_file = cfg_file.replace(".cfg", ".cntrprop")
        mim_file_path = MIM_FILE_DIR + mim_file
        mib_file_path = ECIM_FILE_DIR + mib_file
        cfg_file_path = CFG_FILE_DIR + cfg_file
        counter_file_path = TEMPLATE_FILES_15MIN_DIR + counter_file
        cntrprop_file_path = TEMPLATE_FILES_15MIN_DIR + cntrprop_file
        os.system(ECIMXMLGEN_SCRIPT + " -mode t -mom " + mib_file_path + " -inCfg " + cfg_file_path + " -inRelFile " + mim_file_path + " -outFile " + counter_file_path + " -prop " + cntrprop_file_path)

    try:
        os.path.isfile(counter_file_path)
    except:
        logging.error("Failed to create config file for: " + mib_file)

def copy_nexus_templates_file():
    for sim in sim_data_list:
        node_type = sim.split()[5].upper().strip()
        if 'EPG-SSR' in node_type or 'EPG-EVR' in node_type:
            if not os.path.isdir(XML_FILE_DIR):
                print getCurrentDateTime() + ' ERROR: ' + XML_FILE_DIR + ' does not exist. Unable to copy EPG templates.'
                logging.error(XML_FILE_DIR + ' does not exist. Unable to copy EPG templates.')
                return
            print getCurrentDateTime() + ' INFO: Copying EPG templates.'
            logging.info('Copying EPG templates.')
            for release in EPG_RELEASE:
                for type in EPG_FILE_TYPES:
                    SOURCE_FILE = XML_FILE_DIR + "EPG_" + release + "_" + type + ".template"
                    TARGET_FILE = "epg_counters_" + type + "_" + release + ".xml"
                    if os.path.isfile(SOURCE_FILE):
                        copy_files(SOURCE_FILE, TEMPLATES_FILES_1MIN_DIR, TARGET_FILE)
                        copy_files(SOURCE_FILE, TEMPLATE_FILES_15MIN_DIR, TARGET_FILE)
                        copy_files(SOURCE_FILE, TEMPLATE_FILES_1440MIN_DIR, TARGET_FILE)
                    else:
                        print getCurrentDateTime() + ' ERROR: ' + SOURCE_FILE + ' does not exist.'
                        logging.error(SOURCE_FILE + ' does not exist.')
        elif 'WMG' in node_type:
            if not os.path.isdir(XML_FILE_DIR):
                print getCurrentDateTime() + ' ERROR: ' + XML_FILE_DIR + ' does not exist. Unable to copy WMG templates.'
                logging.error(XML_FILE_DIR + ' does not exist. Unable to copy WMG templates.')
                return
            print getCurrentDateTime() + ' INFO: Copying WMG templates.'
            logging.info('Copying WMG templates.')
            for wmg_release in WMG_RELEASE:
                SOURCE_FILE = XML_FILE_DIR + "WMG_" + wmg_release + ".template"
                TARGET_FILE = "wmg_counters_" + wmg_release + ".xml"
                if os.path.isfile(SOURCE_FILE):
                        copy_files(SOURCE_FILE, TEMPLATES_FILES_1MIN_DIR, TARGET_FILE)
                        copy_files(SOURCE_FILE, TEMPLATE_FILES_15MIN_DIR, TARGET_FILE)
                        copy_files(SOURCE_FILE, TEMPLATE_FILES_1440MIN_DIR, TARGET_FILE)
                else:
                    print getCurrentDateTime() + ' ERROR: ' + SOURCE_FILE + ' does not exist.'
                    logging.error(SOURCE_FILE + ' does not exist.')

def get_nodes_for_sim(sim_data_list, uniq_node_list):
    """ This method will map node names with it's simulation.
        Args : <list, list>

        return : sim_node_map = { 'sim_name' : ['node_1', 'node_2', ...] }
    """
    for sim in sim_data_list:
        sim_name = sim.split()[1].split('-')[-1]
        if 'LTE' in sim_name:
            node_pattern = sim.split()[3].replace(sim_name, '')[:-5]
            if 'ERBS' in node_pattern:
                node_pattern = sim_name + node_pattern
                for node in uniq_node_list:
                    if node_pattern in node:
                        sim_node_map[sim_name].append(node)


def get_eutran_nbiot_cell_data(EUTRANCELL_DATA_FILE):
    """ This method will check for single instance of nbiot cell in eutrancellfdd_list.txt, if exists than templates will be created wityh new configuration.
        or else it will create template with old filename format.

        Args : <list, file>

        create : NODE_CELL_MAPPING = { 'sim_name' : ['node=1:2', 'node=2:1'] }

    """
    print getCurrentDateTime() + ' INFO: Reading ' + EUTRANCELL_DATA_FILE + ' file.'
    nbiot_avail_check = "cat " + EUTRANCELL_DATA_FILE + " | grep 'NbIotCell=' | wc -l"
    result = run_shell_command(nbiot_avail_check).strip()
    uniq_node_list = get_uniq_node_list(EUTRANCELL_DATA_FILE)
    get_nodes_for_sim(sim_data_list, uniq_node_list)
    if int(result) < 1:
        print getCurrentDateTime() + ' INFO: No NbIoTCell available in ' + EUTRANCELL_DATA_FILE + ' file.'
        return
    print getCurrentDateTime() + ' INFO: NbIoTCell available in ' + EUTRANCELL_DATA_FILE + ' file.'
    for sim_name, node_list in sim_node_map.iteritems():
        for node_name in node_list:
            cmd = "cat " + EUTRANCELL_DATA_FILE + " | grep " + node_name + " | egrep 'EUtranCellTDD=|EUtranCellFDD=' | wc -l"
            eutran_cnt = run_shell_command(cmd).strip()
            cmd = "cat " + EUTRANCELL_DATA_FILE + " | grep " + node_name + " | grep 'NbIotCell=' | wc -l"
            nbiot_cnt = run_shell_command(cmd).strip()
            NODE_CELL_MAPPING[sim_name].append(node_name + '=' + eutran_cnt + ':' + nbiot_cnt)
    write_temp_mapping_file()


def write_temp_mapping_file():
    print getCurrentDateTime() + ' INFO: Writing ' + node_cell_relation_file + ' file.'
    write_node_cfg_file = open(node_cell_relation_file, "a+")
    for sim, node_details in NODE_CELL_MAPPING.iteritems():
        for detail in node_details:
            write_node_cfg_file.write(sim + '=' + detail + '\n')
    write_node_cfg_file.close()


def create_topology_data():
    """ This method will map the topology and cell relation with node's cell and write it in text file.
        It will only work for DG2 and ERBS nodes.
        Args : list
    """
    print getCurrentDateTime() + ' INFO: Mapping cell relation for sims.'
    topology_data = ''
    write_relation_file = open(relation_file, 'a+')
    for sim_info in sim_data_list:
         sim_data = sim_info.split()
         sim_name = sim_data[1]
         node_name = sim_data[3]
         if "LTE" in sim_name and 'ERBS' in node_name:
             topology_data = "/netsim/netsimdir/" + sim_name + "/SimNetRevision/TopologyData.txt"
             if os.path.isfile(topology_data):
                 os.system("cat " + topology_data + " | egrep ',Cdma20001xRttCellRelation=|,EUtranCellRelation=|,UtranCellRelation=|,GeranCellRelation=' | sed 's/\"//g' >> " + TOPOLOGY_DATA_FILE)
                 # Making LTE sim name like netsim_cfg, e.g : LTE01
                 sim_name = sim_name.split('-')[-1]
                 if NODE_CELL_MAPPING.has_key(sim_name):
                     relation_writer_for_nbiot_conf(sim_name, write_relation_file)
                 else:
                     relation_writer_for_lagacy_conf(sim_name, topology_data, write_relation_file)
             else:
                 print getCurrentDateTime() + " WARN: cannot find " + topology_data
    write_relation_file.close()


def find_relation(sim_name, node_name, cnt, total_cell_count, write_relation_file):
    """ This method will fetch no of instance of relation_type from topology file.
    """
    cnt = str(cnt)
    relation_type = [',Cdma20001xRttCellRelation=', ',EUtranCellRelation=', ',UtranCellRelation=', ',GeranCellRelation=']
    for relation in relation_type:
        cmd_1 = "cat " + TOPOLOGY_DATA_FILE + " | grep " + node_name + "-" + cnt + ", | grep " + relation + " | wc -l"
        count_value = run_shell_command(cmd_1).strip()
        if count_value == '0':
            write_relation_file.write(sim_name + "=" + node_name + "-" + cnt + "=" + relation.replace(',', '') + count_value)
        elif int(count_value) > 0:
            cell_type = relation.replace(',', '').replace('=', '')
            count_value = str(math.ceil(find_mo_info_from_csv_map(retrieve_lte_sim_name(node_name), cell_type, str(total_cell_count)) / (total_cell_count * 1.0))).split('.')[0]
            if int(count_value) < 1:
                write_relation_file.write(sim_name + "=" + node_name + "-" + cnt + "=" + relation.replace(',', '') + count_value + "\n")
                continue
            write_relation_file.write(sim_name + "=" + node_name + "-" + cnt + "=" + relation.replace(',', '') + count_value + "=")
            cmd_2 = "cat " + TOPOLOGY_DATA_FILE + " | grep " + node_name + "-" + cnt + ", | grep " + relation + " | rev | cut -d= -f1 | rev | sed 's/ //g' | head -" + count_value
            _list = filter(None, run_shell_command(cmd_2).split())
            check = False
            for value in _list:
                if check:
                    write_relation_file.write("," + value)
                else:
                    write_relation_file.write(value)
                    check = True
        write_relation_file.write('\n')


def relation_writer_for_nbiot_conf(sim_name, write_relation_file):
    """ This method will calculate the total number of cell and extract the node name from NODE_CELL_MAPPING map.
        And based on that it will call other method to find out the cell-relation for that node's cell. This method will be
        called only if nbiot node is available.
    """
    for node_details in NODE_CELL_MAPPING[sim_name]:
        node_name = node_details.split('=')[0]
        total_cell = int(node_details.split('=')[1].split(':')[0]) + int(node_details.split('=')[1].split(':')[1])
        for cnt in range(1, total_cell + 1):
            find_relation(sim_name, node_name, cnt, total_cell, write_relation_file)


def relation_writer_for_lagacy_conf(sim_name, topology_data, write_relation_file):
    """ This method will fetch node with it's cell count from topology data files which is in SimnetRevision folder from sim_name.
        And after that it will create a map with 1 3 6 12 configuration.
        create : lagacey_map : {'cell_count' : ['sim_name,node_name',..]}
    """
    lagacey_map = defaultdict(list)
    cmd = "cat " + topology_data + " | sed 's/\"//g' | rev | cut -d, -f1 | rev | egrep 'FDD=|TDD=' | cut -d= -f2 | cut -d- -f1 | uniq -c| sed 's/ //g' | sed 's/L/-L/g'"
    node_list = filter(None, run_shell_command(cmd).split())
    for node_info in node_list:
        cell_cnt = node_info.split('-')[0]
        node = node_info.split('-')[1]
        lagacey_map[cell_cnt].append(sim_name + "," + node)
    for key, values in lagacey_map.iteritems():
        for value in values:
            for cnt in range(1, int(key) + 1):
                find_relation(value.split(',')[0], value.split(',')[1], cnt, int(key), write_relation_file)


def create_csv_file_map():
    ne_type_with_mim_ver = ""
    cmd = "cat " + MO_CSV_FILE + " | sed 's/ //g' | sed -n '1!p'"
    csv_data_list = filter(None, run_shell_command(cmd).strip())
    csv_data_list = csv_data_list.split()
    for data in csv_data_list:
        attrs = data.split(',')
        if attrs[0]:
            ne_type_with_mim_ver = attrs[0] + ':' + attrs[1]
        if len(attrs) > 3:
            for index in range(3, len(attrs)):
                mo_csv_map[ne_type_with_mim_ver][attrs[2]].append(attrs[index])


def topology_creation_check():
    # fetch eutran and nbiot cell info if eutrancellfdd.txt file exists.
    if os.path.isfile(GEN_EUTRANCELL_DATA_FILE) and os.path.getsize(GEN_EUTRANCELL_DATA_FILE) > 0:
        get_eutran_nbiot_cell_data(GEN_EUTRANCELL_DATA_FILE)
        if nrm_type == 'NRM3':
            if os.path.isfile(MO_CSV_FILE):
                return True
            else:
                print getCurrentDateTime() + ' WARN: ' + MO_CSV_FILE + ' file not found.'
                return False
        else:
            return False
    else:
        if nrm_type == 'NRM1.2':
            print getCurrentDateTime() + ' WARN: ' + GEN_EUTRANCELL_DATA_FILE + ' file is empty or not found.'
            return False
        else:
            print getCurrentDateTime() + ' ERROR: ' + GEN_EUTRANCELL_DATA_FILE + ' file is empty or not found for deployment type ' + nrm_type
            exit_logs(1)


def get_nrm_type():
    NETSIM_CFG_FILE = '/tmp/' + get_hostname()
    if os.path.isfile(NETSIM_CFG_FILE):
        with open(NETSIM_CFG_FILE, 'r') as netsim_cfg_file:
            for line in netsim_cfg_file:
                if line.startswith('TYPE=') and line.replace('TYPE=','').strip()[1:][:-1]:
                    return line.replace('TYPE=','').strip()[1:][:-1]
        print getCurrentDateTime() + ' ERROR: Deployment type is not defined in ' + NETSIM_CFG_FILE + ' file.'
        exit_logs(1)
    else:
        print getCurrentDateTime() + ' ERROR: ' + NETSIM_CFG_FILE + ' not found.'
        exit_logs(1)


def check_LTE_sims_existance():
    for sim_data in sim_data_list:
        sim_name = sim_data.split()[1]
        node_name = sim_data.split()[3]
        if 'LTE' in sim_name and 'ERBS' in node_name:
            return True
    return False


def get_hostname():
    command = "hostname"
    return run_shell_command(command).strip()


def core_node_mapping_check():
    global core_nodes_mapping
    if nrm_type == 'NRM3':
        if os.path.isfile(MO_CSV_FILE):
            core_nodes_mapping = True
            if not mo_csv_map:
                create_csv_file_map()
        else:
            print getCurrentDateTime() + ' WARN: ' + MO_CSV_FILE + ' file not found.'


def main(argv):

    isDeletion = True
    isTopology = False
    isLTEpresent = False

    try:
        opts, args = getopt.getopt(argv, "d", ["d="])
    except getopt.GetoptError:
        print "Cleanup of " + TEMPLATE_FILES_15MIN_DIR + " required"
    for opt, arg in opts:
        if opt == '-h':
            print "TemplateGenerator.py -d <If cleanup of older templates is required> "
            sys.exit()
        elif opt in ("-d", "--d"):
            print "Cleanup of " + TEMPLATE_FILES_15MIN_DIR + " not required"
            isDeletion = False

    # clear any existing log file entries
    clear_existing_log_file(LOG_FILE)

    # remove existing template files
    directories = [TEMPLATES_FILES_1MIN_DIR, TEMPLATE_FILES_15MIN_DIR, TEMPLATE_FILES_1440MIN_DIR, CFG_FILE_DIR]
    if isDeletion:
        remove_directories(directories)
        create_directories(directories)

    # generate ecim cfg and template files
    global sim_data_list
    sim_data_list = get_sim_data()

    isLTEpresent = check_LTE_sims_existance()

    if not os.path.isdir(PMS_ETC_DIR):
        os.system("mkdir -p " + PMS_ETC_DIR)

    # remove old files.
    if isDeletion:
        os.system("rm -rf " + node_cell_relation_file)
        os.system("rm -rf " + TOPOLOGY_DATA_FILE)
        os.system("rm -rf " + relation_file)
    

    global nrm_type
    nrm_type = get_nrm_type()

    if isLTEpresent:

        isTopology = topology_creation_check()

        # map topology based on check
        if isTopology:
            print getCurrentDateTime() + ' INFO: Reading ' + MO_CSV_FILE + ' file.'
            create_csv_file_map()
            create_topology_data()

    core_node_mapping_check()

    print getCurrentDateTime() + ' INFO: Generating templates.'

    # generate ecim cfg and template files
    ecim_cfg_map = generate_ecim_cfg_map()
    for cfg_file in ecim_cfg_map:
        mim_file = ecim_cfg_map[cfg_file][0]
        mib_file = ecim_cfg_map[cfg_file][1]
        generate_ecim_cfg_file(cfg_file, mib_file, ecim_cfg_map[cfg_file][2], isTopology)
        generate_ecim_template_file(cfg_file, mim_file, mib_file)

    # generate cpp cfg and template files
    cpp_cfg_map = generate_cpp_cfg_map()
    for cfg_file in cpp_cfg_map:
        mim_file = cpp_cfg_map[cfg_file][0]
        generate_cpp_cfg_file(cfg_file, mim_file, cpp_cfg_map[cfg_file][1], isTopology)
        generate_cpp_template_files(cfg_file, mim_file)

    # manipulate EPG templates
    copy_nexus_templates_file()

    # copy templates
    copy_template_files(TEMPLATE_FILES_15MIN_DIR, TEMPLATES_FILES_1MIN_DIR)
    copy_template_files(TEMPLATE_FILES_15MIN_DIR, TEMPLATE_FILES_1440MIN_DIR)

if __name__ == "__main__":
    main(sys.argv[1:])
