import sys
import time
import pyping
import threading
import datetime

class MyThread(threading.Thread):
    def __init__(self,threadID ,ip):
        threading.Thread.__init__(self)
        self.threadID  = threadID
        self.ip = ip
    def run(self):
        #here do ping
#        self.a = pyping.ping(self.ip)
        threadLock.acquire()        
        print_date(self.threadID)
        self.a = pyping.ping(self.ip)
        print(self.ip , '->' ,self.a.destination_ip , '->' , self.a.ret_code)
        threadLock.release()

def print_date(threadID):
    datefields = []
    today = datetime.datetime.today()
    datefields.append(today)
    print "%s: %s" % ( threadID, datefields[0] )


#here create a thread lock
threadLock = threading.Lock()
threads = []

#collect ips 
ips = ['192.168.1.20','127.0.0.1','4.3.2.1','8.8.8.8','172.29.200.1','1.2.3.4']

i = 1
for ip in ips:
    #here create thread
    th = MyThread(i , ip)
    threads.append(th)
    th.start()
    i = i + 1


for t in threads:
    t.join()
