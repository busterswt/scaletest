import requests, json, sys
from library.neutron import create_port,get_fixedip_from_port
from library.nova import boot_server,random_server_name

network_id = '276140a7-d6c6-47b2-a48e-40b25cda10d3'
image_id = 'f9cffd1e-b07f-42d0-9595-857bbd59cc26'
flavor_id = '1'

def main(hostname,network):

    security_group_id = '6916caf3-35df-40c8-a389-6ee16ec42f09'

    _base_info = {}
    _base_info['hostname'] = hostname
    _base_info['primary_port'] = create_port(network,hostname+"_MGMT",security_groups=[security_group_id])
    _base_info['primary_address'] = get_fixedip_from_port(_base_info['primary_port'])

    # Boot the instance
    print "Launching instance... IP address is %s" % _base_info['primary_address']
    ports = {'mgmt':_base_info['primary_port']}

    server,boot_start = boot_server(hostname,ports)

    return _base_info['primary_address'],server,boot_start


