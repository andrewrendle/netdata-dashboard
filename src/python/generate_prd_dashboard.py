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
    print "generate_prd_dashboard.py -c <cluster e.g cisdp> -f <hostsfile somefile.txt> <-h show this>";


def process(clustername, hostlist):
    
    recom = re.compile(r'(^ml-|^bldmp)([a-z]*)([0-9]*)?$')
        
    jazzmap = {'security': 7,
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
    
    banmap = {'sec': 7,
             'sql': 10,
             'mas': 1,
             'lan': 5,
             'edg': 2,
             'kaf': 4,
             'ign': 6,
             'dat': 11,
             'api' : 9,
             'cas': 8,
             'hdf': 3,
             'r': 12} 
    
    hostmap = { 'ml-' : jazzmap,
               'bldmp' : banmap}
    
    nodes = []
    
    # extract our hosts
    for entry in hostlist:
        ip = entry[0]
        host = entry[1] 
        
        parts = host.split('.')
        # bldmpdat05.banglalink.net
        # ml-hdpd1.mobilink.osa                
        result = recom.match(parts[0])  
                        
        prefix = result.group(1)
        hostkey = hostmap.get(prefix)
        htype = result.group(2)
        num = result.group(3) 
        
        print prefix + " " + htype + " " + str(num)
    
        if (num == ""):
          num = "1"

        nodes.append([hostkey.get(htype), htype, ('000' + num)[-4:], parts[0], host, ip]) 
        
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


def main(cluster, hostsfile):
                
    nodes = []
    with open(hostsfile) as f:
        content = f.readlines()  
              
    content = [x.strip() for x in content] 
    
    for node in content:
        nodes.append(node.split())
        
    process(cluster, nodes);
    
if __name__ == "__main__":

    try:    
        opts, args = getopt.getopt(sys.argv[1:], ':c:f:h', ['cluster=','hostsfile='])

        # print sys.argv[0]+' :', opts;

        for opt, arg in opts:
            if opt in ('-c', '--cluster'):
                cluster = arg.strip();
            elif opt in ('-f', '--hostsfile'):
                hostsfile = arg.strip();
            elif opt in ('-h', '--help'):
                usage();
                sys.exit(1);
            else:
                usage();
                sys.exit(1);
                
        main(cluster, hostsfile)
    
    except getopt.GetoptError:
        usage();
        sys.exit(1);
    
