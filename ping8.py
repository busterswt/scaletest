#!/usr/bin/env python

import subprocess, sys
import threading
import time, datetime
import myping
from colorama import Fore, Style
from library.nova import random_server_name,check_status
import cProfile
import re


filename = time.strftime("%Y%m%d-%H%M%S")
target = open(filename, 'w')
target.truncate()

class Pinger(object):
    status = {'alive': [], 'dead': []} # Populated while we are running
    hosts = [] # List of all hosts/ips in our input queue
    
    # How many ping process at the time.
    thread_count = 4

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()

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

    def pop_queue(self):
        ip = None

        self.lock.acquire() # Grab or wait+grab the lock.

        if self.hosts:
            ip = self.hosts.pop()

        self.lock.release() # Release the lock, so another thread could grab it.

        return ip

    def dequeue(self,build_duration):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'alive' if self.ping(ip,build_duration) else 'dead'
            self.status[result].append(ip)

    def start(self,build_duration):
        threads = []

        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue(build_duration))
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [ t.join() for t in threads ]

        return self.status

if __name__ == '__main__':
    ping = Pinger()
    ping.thread_count = 8
#    ping.hosts = ['127.0.0.1', '8.8.8.8', '192.168.0.4', '192.168.0.5','192.168.0.6']

    #vars
    build_threshold_mid = 15.0
    build_threshold_high = 20.0

    for i in range(int(sys.argv[1])):    
        # Boot an instance. The IP will be returned. Append the host array and start the ping test
        host_addr,server,build_start = myping.main(random_server_name(),sys.argv[2])
        #ping.hosts.insert(0,host_addr)
        ip = host_addr

        # Check to see if VM state is ACTIVE. Start ping
        # (todo) Will want to put an ERROR check in here so we can move on
        print "Waiting for instance %s to go ACTIVE..." % server.id
        status = check_status(server.id)
        while not status == "ACTIVE":
#            print "DEBUG: Current status: %s +%s" % (status,round(time.time() - build_start,2))
#            time.sleep(.25)
#            print "DEBUG: Checking status..."
            status = check_status(server.id)

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
