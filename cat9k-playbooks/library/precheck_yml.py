#Validate overlay_db.yml for any errors

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import yaml, json
import ipaddress
from netaddr import IPAddress
import collections

mul_list_dict = collections.defaultdict(list)

def yaml_error_validation(parsed_underlay, parsed_overlay, debug) :
    """
    validate some error scenarios in the yaml file
    Args:
        parsed_underlay: underlay yaml file converted to dict
        parsed_overlay: overlay yaml file converted to dict
        debug: for completed output 
    Returns:
        string : "partial validation for vlan and svi is done successfully"
    Raises:
        KeyError if key not founds
    Error_senarios :
        vni duplication,evi duplication,svi_type core duplication
    """

    # check if all mandatory sections are present in the underlay
    if "stp" not in parsed_underlay :
        raise KeyError ("Mandatory stp section is missig in the underlay_db")
    if "priority" not in parsed_underlay['stp'] :
        raise KeyError ("Mandatory stp.priority section is missig in the underlay_db")
    else :
        valid_priorities = [ "0", "4096", "8192", "12288", "16384", "20480", "24576", "28672", "32768", "36864", "40960", "45056", "49152", "53248", "57344", "61440"]
        if parsed_underlay['stp']['priority'] not in valid_priorities :
            raise ValueError (f"Configure STP priority is not a valid value.\n supported values are: {', '.join(valid_priorities)}")


    if "domain" not in parsed_underlay :
        raise KeyError ("Mandatory domain section is missig in the underlay_db")
    if "name" not in parsed_underlay['domain'] :
        raise KeyError ("Mandatory domain.name section is missig in the underlay_db")


    if "underlay" not in parsed_underlay:
        raise KeyError ("Mandatory underlay section is missig in the underlay_db")
    if "router_id" not in parsed_underlay['underlay']:
        raise KeyError ("Mandatory underlay.router_id section is missig in the underlay_db")
    elif not parsed_underlay['underlay']['router_id'].startswith('Loopback') :
        raise ValueError ("underlay.router_id must be a Loopback interface")
    if "vtep_name" not in parsed_underlay['underlay']:
        raise KeyError ("Mandatory underlay.vtep_name section is missig in the underlay_db")
    elif not parsed_underlay['underlay']['vtep_name'].startswith('Loopback') :
        raise ValueError ("underlay.vtep_name must be a Loopback interface")
    if parsed_underlay['underlay']['router_id'] == parsed_underlay['underlay']['vtep_name'] :
        raise ValueError ("underlay.router_id and underlay.vtep_name must be different Loopbacks")


    if "ospf" not in parsed_underlay:
        raise KeyError ("Mandatory ospf section is missig in the underlay_db") 
    if "area" not in parsed_underlay['ospf']:
        raise KeyError ("Mandatory ospf.area section is missig in the underlay_db")
    else :
        try :
            ipaddress.IPv4Address(parsed_underlay['ospf']['area'])
        except :
            raise ValueError ("OSPF area must be in dotted format")


    if "bgp" not in parsed_underlay:
        raise KeyError ("Mandatory bgp section is missig in the underlay_db")
    if "as_number" not in parsed_underlay['bgp']:
        raise KeyError ("Mandatory bgp.as_number section is missig in the underlay_db")
    if "password" not in parsed_underlay['bgp']:
        raise KeyError ("Mandatory bgp.password section is missig in the underlay_db")
    if "leafs_range" not in parsed_underlay['bgp']:
        raise KeyError ("Mandatory bgp.leafs_range section is missig in the underlay_db")
    else :
        try :
            ipaddress.IPv4Network(parsed_underlay['bgp']['leafs_range'])
        except :
            raise ValueError ("BGP Leaf Range must be a valid IPv4 Network")
        

    if "spines" not in parsed_underlay['bgp']:
        raise KeyError ("Mandatory bgp.spines section is missig in the underlay_db")
    else :
        for spine_ip in parsed_underlay['bgp']['spines'] :
            try :
                ipaddress.IPv4Address(spine_ip)
            except :
                raise ValueError ("BGP Spine IP must be a valid IPv4 address")
        spines = parsed_underlay['bgp']['spines']
        unique_spines = set(spines)
        if len(spines) != len(unique_spines) or not (2 <= len(spines) <= 4):
            raise ValueError ("BGP Spine IPs must be different and must be at least 2 and max 4")


    # check if all mandatory sections are present in the underlay
    if "anycastgateway" not in parsed_overlay:
        raise KeyError ("Mandatory anycastgateway section is missig in the underlay_db")
    
    if "vrfs" not in parsed_overlay:
        raise KeyError ("Mandatory vrfs section is missig in the underlay_db")

    if "vlans" not in parsed_overlay:
        raise KeyError ("Mandatory vlans section is missig in the underlay_db")

    return ("partial validation for underlay and overlay is done successfully")
    
def vlan_svi_validation(parsed_overlay, debug) :
    return ("partial validation for vlan and svi is done successfully")
    
def vrf_validation(parsed_overlay, debug) :
    return ("partial validation for VRFs is done successfully")

        
def run_module():
    module = AnsibleModule(
        argument_spec=dict( 
          underlay_db=dict(type='dict', required=True),
          overlay_db=dict(type='dict', required=True),
          debug=dict(type='str', required=True)
        ),
        supports_check_mode=True
    )   

    result = {}

    #result['precheck'] = parsed_yaml
    result['yaml_precheck']= ( 
        yaml_error_validation(module.params['underlay_db'], module.params['overlay_db'], module.params['debug']),
        vlan_svi_validation(module.params['overlay_db'], module.params['debug']),
        vrf_validation(module.params['overlay_db'], module.params['debug']),
    )    
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
