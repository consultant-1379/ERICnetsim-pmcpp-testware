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
# Purpose       :  This script will contain the common functions which are used in the netsim_stub  
# Jira No       :  EQEV-47447 
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3311326/ 
# Description   :  OSS Emulator : Coding related to Stub
# Date          :  12/02/2018
# Last Modified :  sudheep.mandava@tcs.com 
####################################################

import sys
sys.path.append('/netsim_users/netsim_stub/commands/');
from string_constants import *

def generateNodelist(node_prefix,node_count):
    ''' This function will generate node names using node_prefix and node_count which will be provide by user in the network configuration file''' 
    node_list = []
    if "RNC" in node_prefix:
       node_list.append(node_prefix.split(COLON)[0])
       for node_num in range(1,int(node_count)+1):
           node_suffix = '{0:02d}'.format(node_num)
           node_name = node_prefix.split(COLON)[1] + str(node_suffix)
           node_list.append(node_name)
    else:
        for node_num in range(1,int(node_count)+1):
            node_suffix = '{0:05d}'.format(node_num)
            node_name = node_prefix + str(node_suffix)
            node_list.append(node_name)
    return node_list

