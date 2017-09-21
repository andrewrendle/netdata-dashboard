# You will need to do the following before running this script:
# 	> pip install requests
# 	> npm install elasticdump -g

import requests
import sys
import os
import commands
# import StringIO
#
# hostname = "google.co.uk"
# with open ("node-frag.html", "r") as nodeFrag:
#     frag = nodeFrag.readlines()
#     frag.format(Hostname = hostname)

def getKey(node):
    return node[0]

if len(sys.argv) != 2:
    print("ERROR: Wrong number of args - must specify clustername (e.g. live)> " + ', '.join(sys.argv))
    sys.exit()

clusterName = sys.argv[1]

nodes = []

listNodesResult = commands.getstatusoutput('~/gitrepos/ansible/nodes.sh list | grep ' + clusterName)
for line in listNodesResult[1].splitlines():
    nodeName = line.split('|')[1].strip()
    nodeRole = line.split('|')[3].strip()
    hostname = line.split('|')[7].strip()

    nodes.append([ nodeName, nodeRole, hostname ])

    # with open ("node-frag.html", "r") as nodeFrag:
    #     frag = nodeFrag.read()
    #     nodeFrag = frag.format(Hostname=hostname, NodeName=nodeName)
    #     print(nodeFrag)

sortedNodes = sorted(nodes, key=getKey)
firstNode = sortedNodes[0]

# nodeFrags = []
orderedFrags = []
for node in sortedNodes:
    # print(node[0])
    if node[1] == "elasticsearch":
        nodeName = node[0]
        hostname = node[2]

        with open ("node-frag.html", "r") as nodeFrag:
            frag = nodeFrag.read()
            nodeFrag = frag.format(Hostname=hostname, NodeName=nodeName)
            orderedFrags.append(nodeFrag)

for node in sortedNodes:
    if node[1] != "elasticsearch":
        nodeName = node[0]
        hostname = node[2]

        with open ("node-frag.html", "r") as nodeFrag:
            frag = nodeFrag.read()
            nodeFrag = frag.format(Hostname=hostname, NodeName=nodeName)
            orderedFrags.append(nodeFrag)

leftNodes = ""
rightNodes = ""
left = True
print("Found " + str(len(orderedFrags)) + " nodes")
for node in orderedFrags:
    if left:
        leftNodes += node
    else:
        rightNodes += node

    left = not left

# leftNodes += orderedFrags[0]

with open ("dash-template.html", "r") as dashTemplate:
    dashTemplateText = dashTemplate.read()
    dash = dashTemplateText.format(ClusterName=clusterName.capitalize(), LeftNodes=leftNodes, RightNodes=rightNodes, FirstHost=firstNode[2])

    with open(clusterName.capitalize() + "Dash.html", "w") as dashFile:
        dashFile.write(dash)
