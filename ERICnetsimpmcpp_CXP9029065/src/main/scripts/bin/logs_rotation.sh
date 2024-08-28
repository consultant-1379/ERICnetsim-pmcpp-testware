#!/bin/bash


# This script is responsible for rotating the logs

logs_path="/netsim_users/pms/logs/"


logs_rotator() {
    line_number=`grep -w -n $2 $1 | tail -1 | cut -d ':' -f1`
    sed -i -e 1,"${line_number}d" $1 > /dev/null 2>&1
};

export -f logs_rotator;

time_=`date --date="15 days ago" +%Y-%m-%d`

##greps each file and removes before 15 days logs data

find $logs_path -type f \( -name '*min.log' -o -name '*rec.log' -o -name 'limitbw.log' -o -name '*service*.log' -o -name 'scanners.log' -o -name 'rmFiles.log' -o -name 'sim_pm_path.log' -o -name 'minilink_precook_data.log' \) -exec bash -c 'logs_rotator "$0" "$1"' {} ${time_} \;

