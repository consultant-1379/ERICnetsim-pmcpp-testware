#!/usr/bin/python

################################################################################
# COPYRIGHT Ericsson 2019
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
################################################################################

###################################################
# Version no    :  NSS 24.07
# Purpose       :  To generate events file for simulation based on configurable values.
# Jira No       :  NSS-47713
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/17553134/
# Description   :  Genstats support to create Small NRM6.2.1 with 12 CBRS devices for SADC in CDL
# Date          :  07/03/2024
# Last Modified :  g.shashikumar@tcs.com
####################################################
from _collections import defaultdict
from multiprocessing import Pool
import sys
import traceback

from utilityFunctions import Utility


# Creating Objects
util = Utility()

start_date_local, start_date_utc, end_date_local, end_date_utc = '', '', '', ''
start_time_local, start_time_utc, end_time_local, end_time_utc = '', '', '', ''
start_offset, end_offset = '', ''
conf_celltrace_ne_map = {'FIVEGRADIONODE' : ['EventFileType', 'EventHandler'], 'GNODEBRADIO' : ['EventFileType', 'EventHandler']}
concurrent_process_count = util.getActualMpInstance()
specificNratNodeGeneration = False
specificNratNodeFileName = None
specificNratNodeName = None
depl_type=''
ne_conf_map = { 1: ['old_nrm_type' ], 2: ['NRM6.2', 'NRM6.2.1', 'NRM6.3'], 3: ['NRM6.4'], 4: ['NSS'] } 
depl_key = None

def getFilesBasedOnCellTracePriority(priority, template_location, ne): 
    """ select file from given priority
    """
    try:
        if not util.checkDirectoryExistance(template_location):
            util.printStatements(template_location + ' not found. Not able to generate cell trace file.', 'ERROR', False)
            return 'False', False        
        if depl_key in util.ne_to_events_file:
           if ne in util.ne_to_events_file[depl_key]:
             if priority.lower() in util.ne_to_events_file[depl_key][ne]:
                return util.ne_to_events_file[depl_key][ne][priority.lower()], True
             else:
                return 'False', True
           else:
                return 'False', True
        else:
            util.printStatements(depl_key + ' not present.', 'ERROR')
            sys.exit()
    except:
        traceback.print_exc()

def createFileName(node_type, fileType):
    """ This method returns file name from sample file name """
    try:
        fileConf = util.events_file_format_mapping[node_type][fileType]
        if node_type == 'FIVEGRADIONODE' or node_type == 'GNODEBRADIO':
            return fileConf[0].replace('<START_DATE>.<START_TIME>-<END_TIME>', start_date_utc + '.' + start_time_utc + '-' + end_time_utc) + fileConf[1]
    except:
        traceback.print_exc()


def modifyEventsFileNameAccordingToNE(tmpName, dir, ne):
    if ne == 'FIVEGRADIONODE':
        return tmpName.replace('<EventProducer>', filter(None, dir.split('/'))[-1]), (filter(None, dir.split('/'))[-1]).strip()
    elif ne == 'GNODEBRADIO':
        return tmpName.replace('<EventProducer>', filter(None, dir.split('/'))[-1].split('_')[-1]), (filter(None, dir.split('/'))[-1].split('_')[-1]).strip()


def generateCellTraceFor5gNodes(inMap, ne, dir_List):
    """ This method will generate cell trace data for 5GRADIONODE and GNODEBRADIO""" 
    try:
        eventFile, eventHandler = inMap['EventFileType'], int(inMap['EventHandler'])
        manifest_file_map = defaultdict(list)
        for file_conf in eventFile.split():
            file_conf = file_conf.split(':')
            if util.validateStringForBoolCheck(file_conf[2]):
                fileBasedOnPriority, processGeneration = getFilesBasedOnCellTracePriority(file_conf[1], util.celltrace_file_location, ne)
                if type(fileBasedOnPriority) is dict:
                    for handlerId in range(1, eventHandler + 1):
                        tempFileName = createFileName(ne, 'CELLTRACE').replace('<FILE_ID>', file_conf[0] + '_' + str(handlerId))
                        for dirName in dir_List:
                            newFileName, prod = modifyEventsFileNameAccordingToNE(tempFileName, dirName, ne)
                            if not prod or prod not in fileBasedOnPriority.keys():
                               prod = 'default'
                            template_file = fileBasedOnPriority[prod]
                            if specificNratNodeGeneration and file_conf[1].lower() == 'low': 
                                if dirName.split('/')[3] == specificNratNodeName:
                                    template_file = specificNratNodeFileName
                            if util.checkFileExistance(util.celltrace_file_location + template_file):
                                util.copyFileSourceToDest(util.celltrace_file_location + template_file, dirName + newFileName, True, 0775)
                                manifest_file_map[dirName].append('./' + newFileName)
                            else:
                               util.printStatements('File ' + util.celltrace_file_location + template_file + ' does not exists for network function ' + prod + '.', 'ERROR')
                else:
                    if processGeneration:
                        util.printStatements('Invalid node type or file priority name given in netsim_cfg file for cell trace file for node type : ' + ne + '.', 'ERROR')
                    else:
                        return False                    
        if manifest_file_map:
            util.createManifestFile(manifest_file_map)
        return True
    except:
        traceback.print_exc()


def findRequiredDirectoryStaructure(inputMap, inputSim, node_type):
    """ This method will gather/make required directory structure """
    try:
        status, pm_path_list = util.getEnrichedJsonDataFromKey(util.getJsonMapObjectFromFile(util.celltrace_json), inputSim + '|' + node_type)
        if not status and pm_path_list == 'False':
            util.printStatements('No info available in celltrace JSON file.', 'WARNING')
            return False
        if status:
            pm_dirs = util.getherNodeList(util.getPmsPathForSim(inputSim, node_type), inputSim)
            if not pm_dirs:
                util.printStatements('Node dirs not found in ' + util.getPmsPathForSim(inputSim, node_type) + ' path for sim : ' + inputSim + '.', 'WARNING')
                return True
            node_path_list = util.filterNodePathListFromStartedNodeFile(pm_dirs)
            if node_path_list:
                full_pms_path_list = [ node_path + str(pm_path) for node_path in node_path_list for pm_path in pm_path_list]
                if node_type == 'FIVEGRADIONODE' or node_type == 'GNODEBRADIO':
                    return generateCellTraceFor5gNodes(inputMap, node_type, full_pms_path_list)
            else:
                util.printStatements('Not a single node started for sim : ' + inputSim + '.', 'WARNING')
                return True
        else:
            if node_type == 'GNODEBRADIO':
                util.printStatements('Provided simulation ' + inputSim + ' is not of NRAT simulation. Configurable celltrace not required.', 'INFO')
                return True
            else:
                util.printStatements('No info found in Json data for cell trace key : ' + inputSim + '|' + node_type, 'ERROR')
            return False
    except:
        traceback.print_exc()
    
    
def gatherParameterValues(node_type, sim_name):
    """ This method gathers required parameters values """
    try:
        util.printStatements('Configurable cell trace generation for sim : ' + sim_name + ' has been started', 'INFO')
        enrichedMap = {}
        with open(util.netsim_cfg, 'r') as net_cfg:
            params = conf_celltrace_ne_map[node_type]
            for line in net_cfg:
                for param in params:
                    if line.startswith(node_type.replace('-','_') + '_' + param + '='):
                        enrichedMap[param] = line.split('"')[1]
        if enrichedMap:
            if findRequiredDirectoryStaructure(enrichedMap, sim_name, node_type):
                util.printStatements('Conf cell trace generation for sim : ' + sim_name + ' has been completed.', 'INFO')
        else:
            util.printStatements('No configuration found in ' + util.netsim_cfg + ' file for node type : ' + node_type + '.', 'ERROR')
            util.printStatements('Skipping conf cell trace file generation for sim : ' + sim_name, 'ERROR')
    except:
        traceback.print_exc()


def defineSimEligibility(sim, sim_id, ne, sim_list):
    if ne in conf_celltrace_ne_map:
        if sim in sim_list:
            return True
        else:
            return False
    return False


def setSpecificNodeInformation():
    global specificNratNodeName, specificNratNodeGeneration, specificNratNodeFileName
    success, specificNratNodeName, specificNratNodeFileName = util.getSpecificNratNodeInformtion()
    if success:
        specificNratNodeGeneration = True


def processSimulationList():
    """ This method starts the Execution """
    if util.checkFileExistance(util.netsim_cfg):
        server_sims = util.getSimListFromNetsimCfg('LIST')
        global depl_type
        depl_type = util.getDeploymentVersionInformation()
        global depl_key
        depl_key = get_depl_key()
        if depl_type not in ['NRM1.2', 'NRM3', 'NRM4', 'NRM4.1', 'NRM5', 'NRM5.1', 'NSS']:
            setSpecificNodeInformation()
        if util.checkFileExistance(util.sim_data_file):
            sim_pool_size = Pool(concurrent_process_count)
            with open(util.sim_data_file, 'r') as f:
                for line in f:
                    line = line.split()
                    sim_id = line[1].split('-')[-1]
                    if line[5] == '5GRADIONODE':
                        line[5] = 'FIVEGRADIONODE'
                    if defineSimEligibility(line[1], sim_id, line[5], server_sims):
                        sim_pool_size.apply_async(gatherParameterValues, args=(line[5], line[1],))
            sim_pool_size.close()
            sim_pool_size.join()
        else:
            util.printStatements(util.sim_data_file + ' file not present. Skipping conf cell trace file generation.', 'WARNING', True)
    else:
        util.printStatements(util.netsim_cfg + ' file not present. Skipping conf cell trace file generation.', 'ERROR', True)


def get_depl_key():
    """ This method finds the key from ne_conf_map according to NRM Type """
    for key,depl_list in ne_conf_map.iteritems():
           if depl_type in depl_list:
               return key
    return 1
            


def main(argv):
    """
    argv : startDateTime, endDateTime, startOffset, endOffset
    """
    if argv:
        global start_date_local, start_date_utc, end_date_local, end_date_utc
        global start_time_local, start_time_utc, end_time_local, end_time_utc
        global start_offset, end_offset
        start_date_utc, start_time_utc, end_time_utc = argv[0], argv[1], argv[2]
        processSimulationList()
    else:
        util.printStatements('Invalid arguments given.', 'ERROR', True)



if __name__ == '__main__':
    main(sys.argv[1:])

