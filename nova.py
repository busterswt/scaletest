import base64, os, tempfile, commands, time
from library.clients import nova
import uuid

#print nova.servers.list()

hostname = uuid.uuid1()
server = nova.servers.create(name=hostname,
                    image="3e173a82-64a8-4954-a992-34eebf7ad023",
                    flavor="1",
                    nics=[{"net-id":"b415ae07-97fb-4515-b03e-0f9bed2267b2"}]
                   )

server = nova.servers.find(id=server.id)

# Only continue when IP is set
print("The IP is: %s" % server.accessIPv4)
while not server.accessIPv4 == '':
    time.sleep(1)    
    server = nova.servers.find(id=server.id)
    print("The IP is: %s" % server.accessIPv4)

print("The IP is: %s" % server.accessIPv4)
