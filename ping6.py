#!/usr/bin/env python

import subprocess, sys
import threading
import time, datetime
import myping
from library.nova import random_server_name,check_status

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
        # Use the system ping command with count of 1 and wait time of 1.
#        start_time = time.localtime()
        start_time = time.time()
        keepPinging = True
        while keepPinging:
            ret = subprocess.Popen(['ip','netns','exec','qrouter-176cab96-0da9-496e-bb51-ff1a715027e8','ping', '-c', '1', '-w', '1', ip], stdout=subprocess.PIPE)
            output = subprocess.check_output(('grep', 'received'), stdin=ret.stdout)
            if "1 received" in output:
#                end_time = time.localtime()        
                end_time = time.time()
                keepPinging = False
                duration = round(end_time - start_time,4)
#                duration = (time.mktime(end_time) - time.mktime(start_time)) 
                # Write to file
                line = ip, build_duration, duration
#                line = ip, start_time, end_time, duration
                target.write(str(line))
                target.write("\n")
#                print("Build Duration: %s") % build_duration
                print("Ping OK! Time: %s seconds. Moving on...") % duration

                return ret == 0
#        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
#                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        print(output)
#        return ret == 0 # Return True if our ping command succeeds

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

    for i in range(int(sys.argv[1])):    
        # Boot an instance. The IP will be returned. Append the host array and start the ping test
        build_start = time.time()
        host_addr,server = myping.main(random_server_name(),sys.argv[2])
        ping.hosts.insert(0,host_addr)

        # Check to see if VM state is ACTIVE. Start ping
        # (todo) Will want to put an ERROR check in here so we can move on
        print "Waiting for instance to go ACTIVE..."
        status = check_status(server)
        while not status == "ACTIVE":
            time.sleep(0.5)
            status = check_status(server)
        build_end = time.time()
        build_duration = round(build_end - build_start,4)
        print "Instance status now ACTIVE. Build time: %s seconds. Beginning PING" % build_duration
        ping.start(build_duration)

    # Close the file
    target.close()
