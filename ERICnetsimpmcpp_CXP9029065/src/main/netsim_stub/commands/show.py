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
# Purpose       :  The purpose of this script to replicate the netsim command ".show"
# Jira No       :  EQEV-46794
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3198599/
# Description   :  OSS Emulator : Coding related to Stub
# Date          :  22/01/2018
# Last Modified :  mahesh.lambud@tcs.com
####################################################

import sys
import ConfigParser
import xml.etree.ElementTree as ET
import re
from string_constants import *
from common_functions import * 
import subprocess
from subprocess import Popen, PIPE
from itertools import izip

def runShellCommand(input):
    """ This is the generic method, Which spawn a new shell process to get the job done
    """
    output = Popen(input, stdout=PIPE, shell=True).communicate()[0]
    return output

def getHostname():
    command = "hostname"
    hostname =  runShellCommand(command).strip()
    if "atvts" in hostname:
        return "netsim"
    else:
        return hostname


arg1 = sys.argv[1]

PM_MIBS = {"MSRBS-V2":[["17-Q4-RUI-V3", "MSRBS-V2_71-Q4_V3UPGMib.xml"]], "PRBS":[["16A-WCDMA-V1", "PRBS_16A_V1MIB.xml"], ["61A-UPGIND-LTE-ECIM-MSRBS-V1", "PRBS_61A_UPGIND_V1Mib.xml"], ["61AW-UPGIND-V2", "Fmpmmib.xml"]], "MTAS":[["17B-RUI-CORE-V3", "MTAS_71B-RUI_V3Mib.xml"], ["17B-RUI-CORE-V1", " MTAS_17B-RUI_V1Mib.xml"]], "CSCF":[["17B-RUI-CORE-V1", "CSCF_17B-RUI_V1Mib.xml"]], "SBG":[["1-6-CORE-V2", "vSBG_1-6_V1Mib.xml"], ["17B-RUI-CORE-V2",  "SBG_17B-RUI_V2Mib.xml"], ["17B-RUI-CORE-V1", "SBG_17B-RUI_V1Mib.xml"]], "EME":[["1-0-WCDMA-V3", "EME_1-0_V3Mib.xml"]], "MRSV":[["16A-CORE-V3", "MRSv_16A-CORE-v3_mib.xml"], ["1-7-CORE-V2", "MRSv-BGF_1-7-CORE-V2mib.xml"], ["1-9-CORE-V1", "MRSv-BGF_1-9-CORE-V1mib.xml"]] }

with open(USER_INPUT_XML, "r") as user_input_file:
    user_input_string = user_input_file.read()
user_input = ET.fromstring(user_input_string)

def ConfigSectionMap(section):
    Config = ConfigParser.ConfigParser()
    Config.read(ENVIRONMENT)
    env_dict = {}
    options = Config.options(section)
    for option in options:
        try:
            env_dict[option] = Config.get(section, option)
            if env_dict[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            env_dict[option] = None
    return env_dict

def getSimulationData(SimulationName):
    print("NE Name                  Type                 Server         In Address       Default dest.")
    try:
        node_type = user_input.findall(".//*[@name='%s']/node_type" % SimulationName)[0].text
        sim_mim_ver = user_input.findall(".//*[@name='%s']/sim_mim_ver" % SimulationName)[0].text
        sim_mim_ver = re.sub('[_]','',sim_mim_ver)
        network = user_input.findall(".//*[@name='%s']/network" % SimulationName)[0].text
        node_prefix = user_input.findall(".//*[@name='%s']/node_prefix" % SimulationName)[0].text
        no_of_nodes = user_input.findall(".//*[@name='%s']/no_of_nodes" % SimulationName)[0].text
        node_list = generateNodelist(node_prefix,no_of_nodes)
        for node_num,node in enumerate(node_list):
            if 'RNC' in node:
                if node_num == 0:
                    getOutput(node, node_type.split(":")[0], sim_mim_ver.split(":")[0], network)
                else:
                    getOutput(node, node_type.split(":")[1], sim_mim_ver.split(":")[1], network)
            else:
                getOutput(node, node_type, sim_mim_ver, network)
    except IndexError:
        print("Error while generating simdata")
        pass

def getOutput(node_name, node_type, sim_mim_ver, network):
    print(node_name + "\t\t " + network + " " + node_type + " " + sim_mim_ver + " " + getHostname())

def getStarted():
    node_prefix = user_input.findall(".//*/node_prefix")
    nodeprefix_list = [nodeprefix.text for nodeprefix in node_prefix]
    no_of_nodes = user_input.findall(".//*/no_of_nodes")
    nodecount_list = [nodecount.text for nodecount in no_of_nodes]
    sim_name = user_input.findall(".//*/sim_name")
    sim_list = [sim.text for sim in sim_name]
    prefix_count_list = zip(nodeprefix_list,nodecount_list)
    simnames_prefix_count_dict = {}
    sim_node_dict = {}
    for simnames,prefix_count_elements in izip(sim_list,prefix_count_list):
        simnames_prefix_count_dict[simnames] = prefix_count_elements 
    for simnames,prefix_count_elements in simnames_prefix_count_dict.iteritems():
        node_list = generateNodelist(prefix_count_elements[0],prefix_count_elements[1])
        sim_node_dict[simnames] = node_list
    for key, values in sim_node_dict.iteritems():
        keySplit = key.split(':')
        if 'RNC' in values[0]:
            network, rnc_netype, rbs_netype, rnc_mim_version, rbs_mim_version, simulation = keySplit[0], keySplit[1], keySplit[3], re.sub('[_]','',keySplit[2]), re.sub('[_]','',keySplit[4]), keySplit[6]
            getHeader(network, rnc_netype, rnc_mim_version)
            print("    " + values[0] + "\t\t/netsim/netsimdir/" + simulation)
            getHeader(network, rbs_netype, rbs_mim_version)
            for node_num,node in enumerate(values):
                if node_num == 0:
                    continue
                else:
                    print("    " + node + "\t\t/netsim/netsimdir/" + simulation)
        elif CORE in values[0]:
            network, netype, mim_version, simulation = keySplit[0], keySplit[1], re.sub('[_]','',keySplit[2]), keySplit[3]
            getHeader(network, netype, mim_version)
            for node in values:
                print("    " + node + "\t\t/netsim/netsimdir/" + simulation)
        else:
            network, netype, mim_version, simulation = key.split(":")[0], key.split(":")[1], re.sub('[_]','',key.split(":")[2]), key.split(":")[4]
            getHeader(network, netype, mim_version)
            for node in values:
                print("    " + node + "\t\t/netsim/netsimdir/" + simulation)

def getHeader(network, netype, mim_version):
    print("\n'server_" + network + "_" + netype + "_" + mim_version + "@netsim' for " + network + " " + netype + " " + mim_version)
    print("=================================================================")
    print("    NE                          Simulation/Commands")

def netypeFull(node_type, mim_ver):
    for netype in PM_MIBS:
        if netype == node_type:
            for mim in PM_MIBS[netype]:
                if mim_ver == mim[0]:
                    print ("pm_mib :  \"" + mim[1] + "\"")

def main():
    if arg1 == "simnes":
        SimulationName = ConfigSectionMap('Open')['sim_name']
        print(">> .show " + arg1)
        getSimulationData(SimulationName)
        print("OK")
    elif arg1 == "started":
        print(">> .show " + arg1)
        getStarted()
        print("OK")
    elif ' '.join(sys.argv[1:]).startswith("netype full"):
        print(">> .show " + ' '.join(sys.argv[1:]))
        netypeFull(sys.argv[3], sys.argv[4])
        print("OK")
    elif arg1 == "netypes":
        with open(NETYPES, 'r') as netypes:
            print netypes.read()
    else:
        print(sys.argv[1:])
        print("function not defined yet")

if __name__ == '__main__': main()
