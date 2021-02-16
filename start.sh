#!/bin/bash
set -v
cd /home/ubuntu/nsm/
python3 /home/ubuntu/nsm/start_tcpserver.py &
python3 /home/ubuntu/nsm/start_broadcast.py &
cd /home/ubuntu/nsm/webserver
/home/ubuntu/nsm/webserver/start_web.sh &
exit 0
