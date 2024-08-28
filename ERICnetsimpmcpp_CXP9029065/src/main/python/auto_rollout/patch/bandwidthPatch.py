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
# Version no    :  NSS 18.9
# Purpose       :  Script to support bandwidth patching
# Jira No       :  NSS-17779 
# Gerrit Link   :  https://gerrit.ericsson.se/#/c/3594298/
# Description   :  Introduction of patching mechanism for Bandwidth updation
# Date          :  30/04/2018 
# Last Modified :  r.t2@tcs.com 
####################################################

'''
fabtasks is a script to rollout Genstats automatically

@author:     xrahtri

@copyright:  2018 Ericsson. All rights reserved.

@license:    Ericsson

@contact:    r.t2@tcs.com
'''

from __future__ import print_function
import sys
from shutil import move
from tempfile import mkstemp
from os import fdopen, remove

def update_values(**kwargs):
    """ This function updates the valued in /netsim/netsim_cfg file as per inputs provided. """
    filename="/netsim/netsim_cfg"
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(filename) as old_file:
            for line in old_file:
                new_line = line
                for key in list(kwargs):
                    if key in line:
                        keys, value = line.split("=")
                        print ("Patching: " + keys)
                        print ("Replacing: " + str(value))
                        new_line = keys + "=" + kwargs[keys] + "\n"
                        print ("Final val: " + new_line)
                if line != new_line:
                    new_file.write(new_line)
                else:
                    new_file.write(line)
    #Remove original file
    remove(filename)
    #Move new file
    move(abs_path, filename)

def main(**args):
    """ This function calls update_values function"""
    update_values(**args)

if __name__ == '__main__':
    main(**dict(arg.split('=') for arg in sys.argv[1:]))

