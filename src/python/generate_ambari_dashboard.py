# You will need to do the following before running this script:
# 	> pip install requests
# 	> npm install elasticdump -g

import requests
import sys
import os
import commands

import json, sys, copy, urllib2, base64, getopt, getpass, ssl;
from flatten_json import flatten_json;
from urlparse import urlparse;
import paramiko

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
    print "generate-dashboard.py -a <ambari url host:port> -c <cluster e.g cisdp> -u <username> <-h show this>";

def get_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

#
# package the request
#
def get(url, username, password):
    response = None
    try:
        raw = "%s:%s" % (username, password)
        auth = 'Basic %s' % base64.b64encode(raw.encode("utf-8"))
        request = urllib2.Request(url);
        request.add_unredirected_header("Authorization", auth);
        response = urllib2.urlopen(request, context=get_context());
        return json.load(response);
    except IOError, e:
        if hasattr(e, 'code'):  # HTTPError
            print 'http error code: ', e
        elif hasattr(e, 'reason'):  # URLError
            print "can't connect, reason: ", e.reason
        else:
            raise
        sys.exit(1);
    finally:
        if response is not None:
            try:
                response.close()
            except:
                pass
    


def getKey(node):
    return node[0]

def process(clustername, config):
        
    # get the ambari url
    href = config['href'];
    urlparts = urlparse(href)
    ambarihost = urlparts.hostname;
    
    nodes = []
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys() 
    ssh.connect(ambarihost,
            username='ec2-user',
            key_filename='hdp_veon-openssh')

    # extract our hosts
    for item in config.get('items'):
        
        href = item.get('href');
        hosts = item.get('Hosts');
        
        privateHost = hosts['host_name']
        # 2> /dev/null
        
        # execute command on ambari host to resolve public hostnames
        cmd = "ssh -o ConnectTimeout=2 ec2-user@" + privateHost + " 'curl http://169.254.169.254/latest/meta-data/public-hostname'";
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.flush()
        status = stdout.channel.recv_exit_status()
        print "host: [%s] exit status: [%s]" % (privateHost, status)

        if status == 0:
            publicHost = stdout.read()
            nodes.append([ publicHost, privateHost])
        
    ssh.close()
    
    orderedFrags = []
    
    for node in nodes:
    
        with open ("node-frag.html", "r") as nodeFrag:
            frag = nodeFrag.read()
            nodeFrag = frag.format(hostname=node[0], nodename=node[1].split('.')[0])
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
        
    with open ("dash-template.html", "r") as dashTemplate:
        dashTemplateText = dashTemplate.read()
        dash = dashTemplateText.format(cluster=clustername.capitalize(), LeftNodes=leftNodes, RightNodes=rightNodes, FirstHost=ambarihost)
    
        with open("../" + cluster.capitalize() + "Dash.html", "w") as dashFile:
            dashFile.write(dash)


def main(host, cluster, username):
                   
    endpoint = host + '/api/v1/clusters/' + cluster + '/hosts';
    process(cluster, get(endpoint, username, getpass.getpass().strip()));
    
if __name__ == "__main__":

    try:    
        opts, args = getopt.getopt(sys.argv[1:], 'a:c:u:h', ['ambari=', 'cluster=', 'username='])

        # print sys.argv[0]+' :', opts;

        for opt, arg in opts:
            if opt in ('-a', '--ambari'):
                ambari = arg.strip();
            elif opt in ('-h', '--help'):
                usage();
                sys.exit(1);
            elif opt in ('-c', '--cluster'):
                cluster = arg.strip();
            elif opt in ('-u', '--username'):
                username = arg;
            else:
                usage();
                sys.exit(1);
                
        main(ambari, cluster, username)
    
    except getopt.GetoptError:
        usage();
        sys.exit(1);
    
