from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import re
import yaml, json
import ipaddress
from netaddr import IPAddress
import collections

mul_list_dict = collections.defaultdict(list)

def yaml_underlay_validation(parsed_underlay) :
    """
    validate some error scenarios in the yaml file
    Args:
        parsed_underlay: underlay yaml file converted to dict
    Returns:
        string : "Underlay YAML Validation done successfully"
    Raises:
        KeyError if key not founds
        ValueError if values are not of the correct type
    """

    # Validate that the STP section exists and has the correct values
    if "stp" not in parsed_underlay :
        raise KeyError ("Mandatory stp section is missig in the underlay_db")
    if "priority" not in parsed_underlay['stp'] :
        raise KeyError ("Mandatory stp.priority section is missig in the underlay_db")
    else :
        valid_priorities = [ "0", "4096", "8192", "12288", "16384", "20480", "24576", "28672", "32768", "36864", "40960", "45056", "49152", "53248", "57344", "61440"]
        if parsed_underlay['stp']['priority'] not in valid_priorities :
            raise ValueError (f"Configure STP priority is not a valid value.\n supported values are: {', '.join(valid_priorities)}")

    # Validate that the domain_name exists and has the correct values
    if "domain_name" not in parsed_underlay :
        raise KeyError ("Mandatory domain_name section is missig in the underlay_db")


    # Validate that the Underlay section exists and has the correct values
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

    # Validate that the OSPF section exists and has the correct values
    if "ospf" not in parsed_underlay:
        raise KeyError ("Mandatory ospf section is missig in the underlay_db") 
    if "area" not in parsed_underlay['ospf']:
        raise KeyError ("Mandatory ospf.area section is missig in the underlay_db")
    else :
        try :
            ipaddress.IPv4Address(parsed_underlay['ospf']['area'])
        except :
            raise ValueError ("OSPF area must be in dotted format")

    # Validate that the BGP section exists and has the correct values
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
            if ipaddress.IPv4Address(spine_ip) not in ipaddress.IPv4Network(parsed_underlay['bgp']['leafs_range']) :
                raise ValueError ("BGP Spine IPs must be in the same network as bgp.leafs_range") 
        spines = parsed_underlay['bgp']['spines']
        unique_spines = set(spines)
        if len(spines) != len(unique_spines) or not (2 <= len(spines) <= 4):
            raise ValueError ("BGP Spine IPs must be different and must be at least 2 and max 4")

    return ("Underlay YAML Validation done successfully")

def yaml_overlay_validation(parsed_overlay) :
    # check if all mandatory sections are present in the underlay
    if "anycastgateway_mac" not in parsed_overlay:
        raise KeyError ("Mandatory anycastgateway_mac section is missig in the overlay_db")
        
    if "vrfs" not in parsed_overlay:
        raise KeyError ("Mandatory vrfs section is missig in the overlay_db")
    for vrf in parsed_overlay['vrfs'].keys() :
        if "afs" not in parsed_overlay['vrfs'][vrf] :
            raise KeyError ("Mandatory vrfs section is missig in the overlay_db")
        else :
            for afs in parsed_overlay['vrfs'][vrf]['afs'] :
                if afs == "ipv6" :
                    raise KeyError (f"Address Family IPv6 is not yet supported. vrf: {(vrf)}")
                elif afs != "ipv4" :
                    raise KeyError (f"Please configure a valid Address Family for vrf: {(vrf)}")
        if "id" not in parsed_overlay['vrfs'][vrf] :
            raise KeyError ("Mandatory id section is missig in the overlay_db")
        else : 
            if not (100 <= int(parsed_overlay['vrfs'][vrf]['id']) <= 999):
                raise ValueError (f"Invalid VRF ID for vrf: {(vrf)}. Valid values are between 100 and 999 included")   

    if "vlans" not in parsed_overlay:
        raise KeyError ("Mandatory vlans section is missig in the overlay_db")

    return ("partial validation for underlay and overlay is done successfully")
    
def vlan_svi_validation(parsed_overlay) :
    return ("partial validation for vlan and svi is done successfully")
    
def vrf_validation(parsed_overlay) :
    return ("partial validation for VRFs is done successfully")

        
def run_module():
    module = AnsibleModule(
        argument_spec=dict( 
          underlay_db=dict(type='dict', required=True),
          overlay_db=dict(type='dict', required=True)
        ),
        supports_check_mode=True
    )   

    result = {}

    #result['precheck'] = parsed_yaml
    result['yaml_precheck']= ( 
        yaml_underlay_validation(module.params['underlay_db']),
        yaml_overlay_validation(module.params['overlay_db']),
        vlan_svi_validation(module.params['overlay_db']),
        vrf_validation(module.params['overlay_db']),
    )    
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
