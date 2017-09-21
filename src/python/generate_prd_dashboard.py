# You will need to do the following before running this script:
# 	> pip install requests
# 	> npm install elasticdump -g

import requests
import sys
import os
import commands
import re

import json, sys, copy, urllib2, base64, getopt, getpass, ssl;
from flatten_json import flatten_json;
from urlparse import urlparse;
import paramiko
from compiler.ast import nodes

from operator import itemgetter, attrgetter, methodcaller

# import StringIO
#
# hostname = "google.co.uk"
# with open ("node-frag.html", "r") as nodeFrag:
#     frag = nodeFrag.readlines()
#     frag.format(Hostname = hostname)

#
# display usage text
#
def usage():
    print "generate_prd_dashboard.py -c <cluster e.g cisdp> <-h show this>";


def process(clustername, hostlist):
        
    group = {'security': 7,
             'mysqlmd': 10,
             'master': 1,
             'landing': 5,
             'edge': 2,
             'kafka': 4,
             'ignite': 6,
             'hdpd': 11,
             'api' : 9,
             'cassandra': 8,
             'hdf': 3,
             'rsrv': 12} 
    
    nodes = []
    
    # extract our hosts
    for entry in hostlist:
        ip = entry[0]
        host = entry[1] 
        
        parts = host.split('.')
        name = parts[0].split('-')[1]        
        htype = re.search(r'(^[a-zA-Z]*)([0-9]*)$', name).group(1) 
        num = '000' + re.search(r'(^[a-zA-Z]*)([0-9]*)$', name).group(2)
        
        nodes.append([group.get(htype), htype, num[-4:], name, host, ip]) 

    sortednodes = sorted(nodes, key=itemgetter(0, 2))
    
    print sortednodes    
 
    orderedFrags = []
    firsthost = nodes[0][4]

    for node in sortednodes:
    
        with open ("../web/node-frag.html", "r") as nodeFrag:
            frag = nodeFrag.read()
            nodeFrag = frag.format(hostname=node[5], nodename=node[3])
            orderedFrags.append(nodeFrag)
  
    divs = [] 
    for number in range(5):
        divs.append("")
        
    count = len(orderedFrags)
    print("Found " + str(count) + " nodes")
    
    for number in range(count):
        node = orderedFrags[number]
        mod = number % len(divs)
        divs[mod] += node
            
    with open ("../web/dash-template.html", "r") as dashTemplate:
        dashTemplateText = dashTemplate.read()
        dash = dashTemplateText.format(cluster=clustername.capitalize(), zero=divs[0], one=divs[1], two=divs[2], three=divs[3], four=divs[4], FirstHost=firsthost, cellwidth=20)
    
        with open("../" + cluster + "dash.html", "w") as dashFile:
            dashFile.write(dash)


def main(cluster):
                
    nodes = []
    with open('../data/dashboard-prd-hosts.txt') as f:
        content = f.readlines()        
    content = [x.strip() for x in content] 
    
    for node in content:
        nodes.append(node.split())

    process(cluster, nodes);
    
if __name__ == "__main__":

    try:    
        opts, args = getopt.getopt(sys.argv[1:], ':c:h', ['cluster='])

        # print sys.argv[0]+' :', opts;

        for opt, arg in opts:
            if opt in ('-c', '--cluster'):
                cluster = arg.strip();
            else:
                usage();
                sys.exit(1);
                
        main(cluster)
    
    except getopt.GetoptError:
        usage();
        sys.exit(1);
    
