#!/usr/bin/env python

import subprocess, sys
import time, datetime
import library.neutron as neutronlib
import library.nova as novalib
from colorama import Fore, Style


filename = time.strftime("%Y%m%d-%H%M%S")
target = open(filename, 'w')
target.truncate()

class Pinger(object):
    
    def ping(self, ip, build_duration):

        # vars
        ping_threshold_mid = 15.0
        ping_threshold_high = 45.0

        # Use the system ping command with count of 1 and wait time of 1.
        start_time = time.time()
        keepPinging = True
        while keepPinging:
            ret = subprocess.Popen(['ip','netns','exec','qrouter-176cab96-0da9-496e-bb51-ff1a715027e8','ping', '-c', '1', '-w', '1', ip], stdout=subprocess.PIPE)
            output = subprocess.check_output(('grep', 'received'), stdin=ret.stdout)
    

            if "1 received" in output: # Means ping was received
                end_time = time.time()
                keepPinging = False
                duration = round(end_time - start_time,4)

                # Write results to file
                line = ip, build_duration, duration
                target.write(str(line))
                target.write("\n")

                # Check ping response time and print to terminal
                if duration < ping_threshold_mid:
                    duration = Fore.GREEN + str(duration) + Style.RESET_ALL
                elif duration < ping_threshold_high:
                    duration = Fore.CYAN + str(duration) + Style.RESET_ALL
                else:
                    duration = Fore.YELLOW + str(duration) + Style.RESET_ALL
                print("Ping OK! Return time: ~%s seconds. Moving on...") % duration
                return ret == 0

        print(output)

def launch(hostname,network):
    
    security_group_id = '6916caf3-35df-40c8-a389-6ee16ec42f09'

    try:
        _base_info = {}
        _base_info['hostname'] = hostname
        _base_info['primary_port'] = neutronlib.create_port(network,hostname+"_MGMT",security_groups=[security_group_id])
        _base_info['primary_address'] = neutronlib.get_fixedip_from_port(_base_info['primary_port'])

        # Boot the instance
        print "Launching instance... IP address is %s" % _base_info['primary_address']
        ports = {'mgmt':_base_info['primary_port']}
        server,boot_start = novalib.boot_server(hostname,ports)
   
        return _base_info['primary_address'],server,boot_start
    except Exception:
        error = Fore.RED + str(sys.exc_info()[1]) + Style.RESET_ALL
        print "ERROR: %s" % error

if __name__ == '__main__':
    ping = Pinger()
#    ping.hosts = ['127.0.0.1', '8.8.8.8', '192.168.0.4', '192.168.0.5','192.168.0.6']

    #vars
    build_threshold_mid = 15.0
    build_threshold_high = 20.0

    for i in range(int(sys.argv[1])):    
        # Boot an instance. The IP will be returned.
        try:
            host_addr,server,build_start = launch(novalib.random_server_name(),sys.argv[2])
        except:
            # If there is any kind of exception, just break out
            break

        ip = host_addr

        # Check to see if VM state is ACTIVE. Start ping
        # (todo) Will want to put an ERROR check in here so we can move on
        print "Waiting for instance %s to go ACTIVE..." % server.id
        status = novalib.check_status(server.id)
        while not status == "ACTIVE":
#            print "DEBUG: Current status: %s +%s" % (status,round(time.time() - build_start,2))
            status = novalib.check_status(server.id)

        build_end = time.time()
        build_duration = round(build_end - build_start,4)

        # Print build duration
        if build_duration < build_threshold_mid:
            build_duration_fmt = Fore.GREEN + str(build_duration) + Style.RESET_ALL
        elif build_duration < build_threshold_high:
            build_duration_fmt = Fore.CYAN + str(build_duration) + Style.RESET_ALL
        else:
            build_duration_fmt = Fore.YELLOW + str(build_duration) + Style.RESET_ALL
        print "Instance status now ACTIVE. Total time until ACTIVE: ~%s seconds. Beginning PING" % build_duration_fmt
#        ping.start(build_duration)
        ping.ping(ip,build_duration)

    # Close the file
    target.close()
