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

# I may want to keep "parsed_sec_output" to validate if an SVI is shutdown.
#def compare(userinput:dict,parsed_output:dict,parsed_sec_output:dict ,access_input:dict , tocompare:dict , overlay_intf:dict)->dict:
def compare(userinput:dict, parsed_output:dict, tocompare:dict, overlay_intf:dict)->dict:

    # Compare Vrfs
    for comp_vrfs in userinput['vrfs'] :
        try :
          if comp_vrfs == "all" :
              for vrf in tocompare['vrfs'].keys() :
                  if "vrf" not in parsed_output :
                      mul_list_dict['vrf'].append(vrf)
                  elif vrf not in parsed_output['vrf'].keys() :
                      mul_list_dict['vrf'].append(vrf)
          elif comp_vrfs in tocompare['vrfs'].keys() and "vrf" not in parsed_output :
            mul_list_dict['vrf'].append(comp_vrfs)
          elif comp_vrfs in tocompare['vrfs'].keys() :
            mul_list_dict['vrf'].append(comp_vrfs)
        except :
            pass

    # Compare Overlay Interfaces
    for overlay_inft in overlay_intf['overlay_interfaces'] :
        try :
            if (overlay_intf['overlay_interfaces'][overlay_inft]['vrf'] in mul_list_dict['vrf'] and overlay_inft not in parsed_output['overlay_interfaces'].keys()) :
                mul_list_dict['overlay_inft'].append(str(overlay_inft))
        except :
            mul_list_dict['overlay_inft'].append(str(overlay_inft))

    # Compare Vlans, we Ignore "core" vlans (i.e. L3 VNIs)
    for comp_vlans in userinput['vlans'] :
        try :
          if comp_vlans == "all" :
              for vlan in tocompare['vlans'].keys() :
                  if "vlans" not in parsed_output :
                      mul_list_dict['vlan'].append(vlan)
                  elif vlan not in parsed_output['vlans'].keys() :
                      mul_list_dict['vlan'].append(vlan)
          elif str(comp_vlans) in tocompare['vlans'].keys() and "vlans" not in parsed_output :
            mul_list_dict['vlan'].append(str(comp_vlans))
          elif str(comp_vlans) in tocompare['vlans'].keys() :
            mul_list_dict['vlan'].append(str(comp_vlans))
        except :
            pass

    # Compare SVIs, we Ignore "core" vlans (i.e. L3 VNIs)
    # Only type access is allowed in "tocompare['vlans']"
    for comp_vlans in userinput['vlans'] :
        try :
          if comp_vlans == "all" :
             for vlan in tocompare['vlans'].keys() :
                if "svi" in tocompare['vlans'][vlan] :
                   if "svis" not in parsed_output :
                      mul_list_dict['svi'].append(vlan)
                   elif vlan not in parsed_output['svis'].keys() :
                      mul_list_dict['svi'].append(vlan)
          else :
             if str(comp_vlans) in tocompare['vlans'].keys() and "svi" in tocompare['vlans'][str(comp_vlans)]:
                mul_list_dict['svi'].append(str(comp_vlans))
        except :
            pass

    yml_dict_output =  {
       'vrf_cli' : mul_list_dict['vrf'],
       'vlan_cli' : [ int(x) for x in mul_list_dict['vlan']],
       'svi_cli' : [ int(x) for x in mul_list_dict['svi']],
       'ovrl_intf_cli' : mul_list_dict['overlay_inft']
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
