import time
import subprocess

def ping(ip):
    start_time = time.time()     

    # Use the system ping command with count of 1 and wait time of 1.
    ret = subprocess.call(['ping', '-c', '1', ip],
                 stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

    #return ret == 0 # Return True if our ping command succeeds
    elapsed_time = time.time() - start_time
    return elapsed_time

if __name__ == "__main__":
    pingtime = ping('192.168.0.3')
    print('Time to ping: %s' % pingtime)
