# validate the vlans,svis,vrfs and overlay_interfaces and configures if not present in the host

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

#import re
#from genie.utils import Dq
from genie.conf.base import Device
import yaml, json
import collections

mul_list_dict = collections.defaultdict(list)

DOCUMENTATION = r'''
---
module: create_incremental_yml

short_description: This module is used for getting the extra values by comparing all.yml and show run nve parser  
                   configurations and return the modified dictionary
'''

# I may want to use "parsed_sec_output" to validate if an SVI is shutdown.
#def compare(userinput:dict, parsed_output:dict, parsed_sec_output:dict, access_input:dict, tocompare:dict, overlay_intf:dict)->dict:
def compare(userinput:dict, parsed_output:dict, tocompare:dict, overlay_intf:dict)->dict:

    # Compare Vrfs names and find missing ones
    for vrf_name in userinput['vrfs'] :
      try :
        if vrf_name == "all" :
          for vrf in tocompare['vrfs'].keys() :
            if "vrf" not in parsed_output or vrf not in parsed_output['vrf'].keys() :
              mul_list_dict['vrf'].append(vrf)
        elif vrf_name in tocompare['vrfs'].keys() :
          if "vrf" not in parsed_output or vrf_name not in parsed_output['vrf'].keys()  :
            mul_list_dict['vrf'].append(vrf_name)
      except :
        pass

    # Compare Overlay Interfaces and find missing ones
    for overlay_inft in overlay_intf['overlay_interfaces'] :
      try :
        if (overlay_intf['overlay_interfaces'][overlay_inft]['vrf'] in mul_list_dict['vrf'] and overlay_inft not in parsed_output['overlay_interfaces'].keys()) :
          mul_list_dict['overlay_inft'].append(str(overlay_inft))
      except :
        mul_list_dict['overlay_inft'].append(str(overlay_inft))

    # Compare Vlans, we Ignore "core" vlans (i.e. L3 VNIs) and find missing ones
    for vlan_number in userinput['vlans'] :
      try :
        if vlan_number == "all" :
          for vlan in tocompare['vlans'].keys() :
            if "vlans" not in parsed_output or vlan not in parsed_output['vlans'].keys() :
              mul_list_dict['vlan'].append(vlan)
        elif str(vlan_number) in tocompare['vlans'].keys() :
          if "vlans" not in parsed_output or str(vlan_number) not in parsed_output['vlans'].keys() :
            mul_list_dict['vlan'].append(str(vlan_number))
      except :
        pass

    # Compare SVIs, we Ignore "core" vlans (i.e. L3 VNIs) and find missing ones
    for vlan_number in userinput['vlans'] :
      try :
        if vlan_number == "all" :
          for vlan in tocompare['vlans'].keys() :
            if "svi" in tocompare['vlans'][vlan] :
              if "svis" not in parsed_output or vlan not in parsed_output['svis'].keys() :
                mul_list_dict['svi'].append(vlan)
        elif str(vlan_number) in tocompare['vlans'].keys() and "svi" in tocompare['vlans'][str(vlan_number)] :
          if "svis" not in parsed_output or str(vlan_number) not in parsed_output['svis'].keys() :
            mul_list_dict['svi'].append(str(vlan_number))                
      except :
        pass

    '''
    # Filter all vlans that belong to a vrf we are going to work on
    for vlan in tocompare['vlans'] :
      #if tocompare['vlans'][vlan]['vrf'] in mul_list_dict['vrf'] :
        mul_list_dict['tocompare_vlan'].append(int(vlan))

    # Evaluate Trunk interfaces
    for intf in access_input['access_interfaces']['trunks']:
      if type(intf) != dict :
        if 'switchport_trunk_vlans' in parsed_sec_output['interfaces'][intf].keys() :
          if parsed_sec_output['interfaces'][intf]['switchport_trunk_vlans'] != "none" :
            mul_list_dict['sec_output_vlan'].append(parsed_sec_output['interfaces'][intf]['switchport_trunk_vlans'])

    # Split vlans separated by commas
    if mul_list_dict['sec_output_vlan'] :
      for trunk_vlan in mul_list_dict['sec_output_vlan'] :
        vlan_list = trunk_vlan.split(',')

    # Break down vlan ranges
      for vlan_split in vlan_list :
        if "-" in vlan_split :
          vlans_after_split = vlan_split.split("-")
          for range_vlan in range(int(vlans_after_split[0]),int(vlans_after_split[1]) + 1) :
            mul_list_dict['range'].append(range_vlan)
        else :
            mul_list_dict['range'].append(int(vlan_split))

    # find the diff between to compare and configured range 
    if mul_list_dict['range'] :
      diff = list(set(mul_list_dict['tocompare_vlan']) - set(mul_list_dict['range']))
    else :
      for vlan in tocompare['vlans'] :
         mul_list_dict['trunk_none'].append(vlan)
      diff =  mul_list_dict['trunk_none']

    for access_vlan in diff :
      mul_list_dict['access_vlan'].append(int(access_vlan))
    '''

    # Return all data to ansible
    yml_dict_output =  {
       'vrf_cli' : mul_list_dict['vrf'],
       'ovrl_intf_cli' : mul_list_dict['overlay_inft'],
       'vlan_cli' : [ int(x) for x in mul_list_dict['vlan']],
       'svi_cli' : [ int(x) for x in mul_list_dict['svi']]
  #     'access_inft_cli' : [ int(x) for x in mul_list_dict['access_vlan']]
    }
    
    yml_dict = {}
    
    for keys,values in yml_dict_output.items() :
        if values != [] :
            yml_dict[keys] = values
        
    compare_op = json.loads(json.dumps(yml_dict))

    return yaml.dump(json.loads(json.dumps(compare_op)), sort_keys=True, default_flow_style=False)
 
  
def run_module():
    
    module = AnsibleModule(
        argument_spec=dict(
            userinput=dict(required=False,type='dict'),
            hostvars=dict(required=False,type='list'),
#            access_input=dict(required=False,type='dict'),
#            sec_output=dict(required=False,type='list'),
            tocompare=dict(required=False,type='dict'),
            overlay_intf=dict(required=False,type='dict'),     
    ),
        supports_check_mode=True
    )   
    
    result = {}

    show_run_nve = '\n'.join(module.params['hostvars'])
#    show_run_int = '\n'.join(module.params['sec_output'])

    device = Device("Switch", os="iosxe")
    device.custom.abstraction = {'order':["os"]}

    parsed_output = device.parse('show run nve', output=show_run_nve)
#    parsed_sec_output = device.parse('show run | sec ^int', output=show_run_int)

    result['yaml'] = compare(
       module.params['userinput'],
       parsed_output,
#       parsed_sec_output,
#       module.params['access_input'],
       module.params['tocompare'],
       module.params['overlay_intf']
       )
    module.exit_json(**result)


def main():
    run_module()

if __name__ == "__main__":
    main()
