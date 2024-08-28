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
# Version no    :  NSS 17.13
# Purpose       :  Take MiniLink sim argument and write it in /netsim/genstats/transport_sim_details file.
# Jira No       :  NSS-13216
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/2514896/
# Description   :  Handling for multi processing
# Date          :  24/07/2017
# Last Modified :  abhishek.mandlewala@tcs.com
####################################################

import os
from subprocess import Popen, PIPE
import subprocess
import sys
import datetime
from time import strftime, gmtime

TRANSPORT_FILE = "/netsim/genstats/transport_sim_details"
GENSTATS_SCRIPT = "/netsim_users/pms/bin/genStats"
MINILINK_MO_TYPE = None
ARG_SEPARATOR = ";"
DOUBLE_COLON_SEPARATOR = "::"
SAMPLE_FILESIZE = {'Small' : ['AMM2pB', 'CN510', 'CN810'], 'Medium' : ['AMM6pD', 'ML6691'], 'Large' : ['AMM20pB', 'LH']}
arg_map = {}

def run_shell_command(input):
    """ This is the generic method, Which spawn a new shell process to get the job done
    """
    output = Popen(input, stdout=PIPE, shell=True).communicate()[0]
    return output


def conf_file_permission(permission):
    """ This is the generic method to change the permission of files
    """
    command = "chmod " + permission + "  " + TRANSPORT_FILE
    run_shell_command(command)


def getCurrentDateTime():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def content_replacer(output_value, param_value):
    command = "sed -i '/" + output_value + "/d' " + TRANSPORT_FILE
    run_shell_command(command)
    command = "echo " + output_value + "=" + param_value + " >> " + TRANSPORT_FILE
    run_shell_command(command)


def argument_parser(input_args):
    """ Take input arguments and store attribute name and it's value in map by parsing it
            {arg_map} : {attr_name : attr_value}
    """
    arg_list = input_args.split(ARG_SEPARATOR)

    if not len(arg_list) > 2:
        print getCurrentDateTime() + ' ERROR : Invalid number of argument.' + '\n' + 'Exiting process.'
        sys.exit(1)

    sim_name = ""
    node_name = ""

    for arg_data in arg_list:
        attr_name = arg_data.split(DOUBLE_COLON_SEPARATOR)[0]
        attr_value = arg_data.split(DOUBLE_COLON_SEPARATOR)[1]

        if "sim_name" == attr_name:
            if not sim_name:
                arg_map[attr_name] = attr_value
            else:
                print getCurrentDateTime() + ' ERROR : Multiple simulation name given.' + '\n' + 'Exiting process.'
                sys.exit(1)
        elif "node_name" == attr_name:
            if not node_name:
                arg_map[attr_name] = attr_value
            else:
                print getCurrentDateTime() + ' ERROR : Multiple node name given in argument.' + '\n' + 'Exiting process.'
                sys.exit(1)
        elif "node_type" == attr_name:
            if not arg_map.has_key('nodeType'):
                arg_map["nodeType"] = attr_value
            else:
                print getCurrentDateTime() + ' ERROR : Multiple node type given in argument.' + '\n' + 'Exiting process.'
                sys.exit(1)
        else:
            arg_map[attr_name] = attr_value

    if arg_map.has_key('sim_name') and arg_map.has_key('node_name'):
        # Check for MiniLink simulation.
        if arg_map.has_key('nodeType') and 'Mini-Link' in arg_map.get('nodeType'):
            if arg_map.has_key('rcID'):
                global MINILINK_MO_TYPE
                if int(arg_map.get('rcID')) < 100:
                    MINILINK_MO_TYPE = 'ETHERNET'
                elif int(arg_map.get('rcID')) > 99:
                    MINILINK_MO_TYPE = 'SOAM'
                arg_map['file_name'] = getAttributeValue('filename')
                arg_map['start_time'] = arg_map.get('file_name')[1:][:18]
                arg_map['end_time'] = getEndInterval(arg_map.get('file_name'))
                arg_map['gran_period'] = getAttributeValue('gran_period')
            else:
                print getCurrentDateTime() + ' ERROR : rcID is not present. Exiting code.'
                sys.exit(1)

            arg_map["fileToBeAssembled"] = getFileSize(arg_map.get("fileToBeAssembled"))

            createGenstatsArgument()
        else:
            print getCurrentDateTime() + ' ERROR : Invalid node type. Exiting process.'
            sys.exit(1)

    else:
        print getCurrentDateTime() + ' ERROR : Simulation name or Node name is not present in input argument.' + '\n' + 'Exiting process.'
        sys.exit(1)


def getAttributeValue(str_):
    attr = ''
    value = ''
    if MINILINK_MO_TYPE == 'ETHERNET':
        if 'filename' == str_:
            attr = 'xfPMFileName'
        elif 'gran_period' == str_:
            attr = 'xfPMFileGranularityPeriod'
    elif MINILINK_MO_TYPE == 'SOAM':
        if 'filename' == str_:
            attr = 'xfServiceOamPmFileName'
        elif 'gran_period' == str_:
            attr = 'xfServiceOamPmFileGranularityPeriod'
    value = arg_map.get(attr)
    del arg_map[attr]
    return value


def createGenstatsArgument():
    if os.path.isfile(GENSTATS_SCRIPT):
        script_argument = ''

        for arg_name, arg_value in arg_map.iteritems():
            script_argument = script_argument + arg_name + ':' + arg_value + ';'
        script_argument = '"' + script_argument[:-1] + '"'

        if arg_map.get('gran_period') == '2':
            script_argument = GENSTATS_SCRIPT + ' -r 1440 -l "' + arg_map.get('nodeType') + '" -n ' + script_argument
        else:
            script_argument = GENSTATS_SCRIPT + ' -r 15 -l "' + arg_map.get('nodeType') + '" -n ' + script_argument

        subprocess.call(script_argument, shell=True)
    else:
        print getCurrentDateTime() + ' ERROR: Genstats scripts not found.'


def getEndInterval(file_name):
    end_date = ""
    end_time = ""
    end_date_time = ""
    node_index_number = 39
    start_date = file_name[1:][:8]
    start_time = file_name[10:][:4]
    offset = file_name[14:][:5]
    arg_map["fileType"] = file_name[:1]

    if arg_map.get('fileType') == 'A':
        node_index_number = 30
        end_time = file_name[20:][:4]
        if start_time == end_time or int(end_time) < int(start_time):
            end_date = datetime.datetime.strptime(start_date, "%Y%m%d") + datetime.timedelta(days=1)
            end_date = datetime.datetime.strftime(end_date, "%Y%m%d")
        else:
            end_date = start_date
        end_date_time = end_date + "." + end_time + offset
    elif arg_map.get('fileType') == 'C':
        end_date_time = file_name[20:][:18]
    else:
        print getCurrentDateTime() + ' ERROR : Invalid file type.' + '\n' + 'Exiting process.'
        sys.exit(1)

    node_info = file_name[node_index_number:].replace('-', '_').split('_')
    if node_info[5]:
        arg_map["userLabel"] = node_info[5]
        arg_map["localDn"] = node_info[1] + "-" + node_info[2] + "-" + node_info[3] + "-" + node_info[4] + "_" + node_info[5]
    else:
        arg_map["userLabel"] = node_info[0] + "-" + node_info[1] + "-" + node_info[2] + "-" + node_info[3] + "-" + node_info[4]
        arg_map["localDn"] = node_info[1] + "-" + node_info[2] + "-" + node_info[3] + "-" + node_info[4] + "_"

    return end_date_time


def getFileSize(_filesize):
    default_filesize = "Small"
    for key, values in SAMPLE_FILESIZE.iteritems():
        for value in values:
            if _filesize == value:
                return key
    print getCurrentDateTime() + ' INFO : Default file size is selected.'
    return default_filesize


def main():
    argument_parser(sys.argv[1])


if __name__ == "__main__":
    main()

