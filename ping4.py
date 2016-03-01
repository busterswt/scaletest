#!/usr/bin/env python

import subprocess
import threading
import time, datetime

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

    def ping(self, ip):
        # Use the system ping command with count of 1 and wait time of 1.
        start_time = time.time()

        keepPinging = True
        while keepPinging:
            ret = subprocess.Popen(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.PIPE)
            output = subprocess.check_output(('grep', 'received'), stdin=ret.stdout)
            if "1 received" in output:
                end_time = time.time()        
                keepPinging = False

                duration = round(end_time - start_time, 2)
                # Write to file
                line = ip, start_time, end_time, duration
                target.write(str(line))
                target.write("\n")
                print line

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

    def dequeue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'alive' if self.ping(ip) else 'dead'
            self.status[result].append(ip)

    def start(self):
        threads = []

        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [ t.join() for t in threads ]

        # Close the file
        target.close()
        return self.status

if __name__ == '__main__':
    ping = Pinger()
    ping.thread_count = 8
    ping.hosts = ['127.0.0.1', '8.8.8.8', '192.168.0.4', '192.168.0.5','192.168.0.6']
#    ping.hosts = [
#        '10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4', '10.0.0.0', '10.0.0.255', '10.0.0.100',
#        'google.com', 'github.com', '127.0.0.1', '127.0.1.2', '1.2.3.4', '8.8.8.8'
#        ]

    print ping.start()
