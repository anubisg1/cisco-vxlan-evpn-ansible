from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

import ipaddress
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
        KeyError if key is not found
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
    """
    validate some error scenarios in the yaml file
    Args:
        parsed_overlay: overlay yaml file converted to dict
    Returns:
        string : "Overlay YAML Validation done successfully"
    Raises:
        KeyError if key is not found
        ValueError if values are not of the correct type
    """

    # Check if all mandatory sections are present in the underlay
    if "anycastgateway_mac" not in parsed_overlay:
        raise KeyError ("Mandatory anycastgateway_mac section is missig in the overlay_db")

    # Check the VRFs section and all of it's mandatory components
    if "vrfs" not in parsed_overlay:
        raise KeyError ("Mandatory vrfs section is missig in the overlay_db")
    for vrf in parsed_overlay['vrfs'].keys() :
        if "afs" not in parsed_overlay['vrfs'][vrf] :
            raise KeyError ("Mandatory vrfs section is missig in the overlay_db")
        else :
            for afs in parsed_overlay['vrfs'][vrf]['afs'] :
                if afs == "ipv6" :
                    raise ValueError (f"Address Family IPv6 is not yet supported. vrf: {(vrf)}")
                elif afs != "ipv4" :
                    raise ValueError (f"Please configure a valid Address Family for vrf: {(vrf)}")
        if "id" not in parsed_overlay['vrfs'][vrf] :
            raise KeyError ("Mandatory id section is missig in the overlay_db")
        else : 
            if not (100 <= int(parsed_overlay['vrfs'][vrf]['id']) <= 999):
                raise ValueError (f"Invalid VRF ID for vrf: {(vrf)}. Valid values are between 100 and 999 included")   
        if "vlan" not in parsed_overlay['vrfs'][vrf] :
            raise KeyError (f"Mandatory vlan section is missig for vrf: {(vrf)}")
        else :
            if not ( (2 <= int(parsed_overlay['vrfs'][vrf]['vlan']) <= 1001) or (1006 <= int(parsed_overlay['vrfs'][vrf]['vlan']) <= 4094) ) :
                raise ValueError (f"Vlan section for vrf: {(vrf)} is out of range.\n Valid valies are 2-1001 and 1006-4094")

    # Check the Vlans section and all of it's mandatory components
    if "vlans" not in parsed_overlay:
        raise KeyError ("Mandatory vlans section is missig in the overlay_db")
    for vlan in parsed_overlay['vlans'].keys() :
        if not ( (2 <= int(vlan) <= 1001) or (1006 <= int(vlan) <= 4094) ) :
            raise ValueError (f"Vlan number {(vlan)} is out of range.\n Valid valies are 2-1001 and 1006-4094") 
        for vrf in parsed_overlay['vrfs'].keys() :
            if int(vlan) == int(parsed_overlay['vrfs'][vrf]['vlan']) :
                raise ValueError (f"Vlan number {(vlan)} has already been used as a L3VNI vlan for vrf {(vrf)}") 
        if "vrf" not in parsed_overlay['vlans'][vlan] :
            raise KeyError (f"Mandatory vrf section is missig for vlan: {(vlan)}")
        elif not parsed_overlay['vlans'][vlan]['vrf'] in parsed_overlay['vrfs'] :
            raise ValueError (f"Vrf configured for vlan {(vlan)} does not exist in the VRF section")
        # need to check also if only 1 isolated is mapped to a primary #
        # A primary can be mapped to multiple community vlans but only one isolated #
        if "pvlan" in parsed_overlay['vlans'][vlan] :
            if "type" not in parsed_overlay['vlans'][vlan]['pvlan'] :
                raise KeyError (f"Mandatory pvlan type is missig for vlan: {(vlan)}")
            else:
                if not ((parsed_overlay['vlans'][vlan]['pvlan']['type'] == "primary") or
                    (parsed_overlay['vlans'][vlan]['pvlan']['type'] == "community") or
                    (parsed_overlay['vlans'][vlan]['pvlan']['type'] == "isolated")) :
                    raise ValueError (f"Private Vlan Type configured for vlan {(vlan)} is invalid")
                if ((parsed_overlay['vlans'][vlan]['pvlan']['type'] == "community") or (parsed_overlay['vlans'][vlan]['pvlan']['type'] == "isolated")) :
                    if "primary" not in parsed_overlay['vlans'][vlan]['pvlan'] :
                        raise KeyError (f"Mandatory primary vlan association is missig for vlan: {(vlan)}")
                    else :
                        primary = parsed_overlay['vlans'][vlan]['pvlan']['primary']
                        if primary not in parsed_overlay['vlans'].keys() :
                            raise ValueError (f"Primary vlan {(primary)} configured for vlan {(vlan)} does not exist")
                        else :
                            if "pvlan" not in parsed_overlay['vlans'][primary] :
                                raise KeyError (f"Private Vlan section is missig for vlan: {(primary)} referenced by vlan {(vlan)} ")
                            if "type" not in parsed_overlay['vlans'][primary]['pvlan'] :
                                raise KeyError (f"Private Vlan Type is missig for vlan: {(primary)} referenced by vlan {(vlan)} ")
                            elif not ( parsed_overlay['vlans'][primary]['pvlan']['type'] == "primary" ):
                                raise ValueError (f"Vlan {parsed_overlay['vlans'][vlan]['pvlan']['primary']} is not configured as a primary pvlan")
            
        if "svi" in parsed_overlay['vlans'][vlan] :
            if "ipv4" not in parsed_overlay['vlans'][vlan]['svi'] :
                raise KeyError (f"Mandatory ipv4 section is missig for the svi in vlan: {(vlan)}")
            else :
                ip = ('/'.join(parsed_overlay['vlans'][vlan]['svi']['ipv4'].split(" ")))
                if ip != ipaddress.IPv4Interface(ip).with_netmask :
                    raise ValueError (f"IP address for {(vlan)} is invalid. Please specificy a valid ip and subnet mask") 
            if "status" not in parsed_overlay['vlans'][vlan]['svi'] :
                raise KeyError (f"Mandatory status section is missig for the svi in vlan: {(vlan)}")
            elif not ((parsed_overlay['vlans'][vlan]['svi']['status'] == "enabled") or (parsed_overlay['vlans'][vlan]['svi']['status'] == "disabled")) :
                raise KeyError (f"Wrong status the svi in vlan: {(vlan)}. Valid values are 'enabled' or 'disabled'")

    return ("Overlay YAML Validation done successfully")
        
def run_module():
    module = AnsibleModule(
        argument_spec=dict( 
          underlay_db=dict(type='dict', required=True),
          overlay_db=dict(type='dict', required=True)
        ),
        supports_check_mode=True
    )   

    result = {}

    result['yaml_precheck']= ( 
        yaml_underlay_validation(module.params['underlay_db']),
        yaml_overlay_validation(module.params['overlay_db'])
    )    
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
