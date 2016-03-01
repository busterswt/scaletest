import requests, json, sys
from pprint import pprint
#from neutronclient.v2_0 import client
#from prettytable import PrettyTable
from library.neutron import create_port,create_network,get_fixedip_from_port,add_address_pair,get_macaddr_from_port
from library.neutron import get_gateway_from_port,get_netmask_from_subnet,create_subnet
from library.config import generate_base_config,generate_failover_config
from library.nova import boot_server,random_server_name

network_id = 'b415ae07-97fb-4515-b03e-0f9bed2267b2'
image_id = '3e173a82-64a8-4954-a992-34eebf7ad023'
flavor_id = '1'

def main(hostname,network):

    #
    # Create management interface and base configuration

    _base_info = {}
    _base_info['hostname'] = hostname
    _base_info['primary_port'] = create_port(network,hostname+"_MGMT")
    _base_info['primary_address'] = get_fixedip_from_port(_base_info['primary_port'])

    # Boot the primary ASA
    print "Launching instance... IP address is %s" % _base_info['primary_address']
    ports = {'mgmt':_base_info['primary_port']}
    server = boot_server(hostname,ports)

    return _base_info['primary_address'],server

if __name__ == "__main__":
        hostname = random_server_name()
        main(hostname,network=network_id)

