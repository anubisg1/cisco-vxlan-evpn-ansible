Inputs
######

Inventory.yml
*************

 In the inventory file, roles (Spine or Leaf), names, and management IP addresses of the nodes are
 described.

.. code-block:: yaml

    all:
      children:
        leaf:
          hosts:
            Leaf-01:
              ansible_host: 10.1.1.1
            Leaf-02:
              ansible_host: 10.1.1.2
            
        spine:
          hosts:
            Spine-01:
              ansible_host: 10.1.1.3
            Spine-02:
              ansible_host: 10.1.1.4

``leaf`` and ``spine`` are two roles. Each node should be placed under one of these roles.

``Leaf-01`` , ``Spine-01`` are the hostnames (nodes). Keep in mind that the names should be with the name of the configuration files 
in the directory ``host_vars/node_vars``.

``ansible_host`` is the IP address of the management interface.

group_vars
**********

This directory contains the configurations which are common to all or most of devices.

all.yml
=======

The parameters defined in the file ``all.yml`` are applicable to all devices in the network.

General access
--------------

This section defines access parameters of the remote devices.

.. code-block:: yaml

    ansible_connection: ansible.netcommon.network_cli
    ansible_network_os: cisco.ios.ios
    ansible_python_interpreter: "python"
    ansible_user: cisco
    ansible_ssh_pass: cisco123

    <...skip...>

.. table::
   :widths: auto

   ================================ ==========================================================================
     **Parameter**                  **Comments**
   ================================ ==========================================================================
   **ansible_connection**           This option defines thetype for connection to the remote devices. 
   
                                    In this project, connection via SSH with implementation of CLI is used:

                                    * **ansible.netcommon.network_cli**

   **ansible_network_os**           This option defines the operation system of the remote device. 
                                    This option is needed if “network_cli” is used for 'ansible_connection'. 
                                    
                                    In this project, Cat9k with IOS-XE is used, so this option is set to:

                                    * **cisco.ios.ios** 

   **ansible_python_interpreter**   This option instruct Ansible to use defined python interpreter. 
   
                                    This option is set to:
    
                                    * **python**
    
   **ansible_user**                 This option defines a username which is used for access remote devices 
    
                                    over SSH. In this project, user must have privilege level 15. 
                                    
                                    This option is set to:
    
                                    * **cisco**
    
   **ansible_password**             This option defines a password for the user in 'ansible_user'.
    
                                    In this project, the password is set to:
    
                                    * **cisco123**                                
   ================================ ==========================================================================

.. warning::

   ``ansible_user`` must have privildge level 15. Example of the configuration is below 

   .. code-block::

       username cisco privilege 15 password 0 cisco123

In this example, unencrypted password is used. Feel free to use HIDDEN (7)

If ``enable`` password should be used, check the `Enable Mode <https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html>`_ documentation.

underlay_db.yml
==============

In this file information about the underlay is stored.
Let's check this file gradually step-by-step.

STP definition
--------------

This section defines spanning-tree parameters which are true globally for all Leaf switches.

.. code-block:: yaml
    
    stp:
      priority: '0'
    
    <...snip...>

.. table::
   :widths: auto

================================================ ==========================================================================
**Parameter**                                                            **Comments**
================================================ ==========================================================================
**stp** / :red:`mandatory`                       This option defines the stp section.

**priority** / :red:`mandatory`                  This option defines stp priority. Only valid STP priority values are allowed

================================================ ==========================================================================

Domain Name definition
----------------------

This section defines domain name for all the switches.

.. code-block:: yaml

    domain_name: 'mylab.lab'

    <...snip...>

.. table::
   :widths: auto

=============================================== ========================================================================== 
**Parameter**                                                            **Comments**
=============================================== ==========================================================================
**domain_name** / :orange:`optional`            This option defines the domain name for all the switches
=============================================== ==========================================================================

Underlay definition
-------------------

This section defines which loopbacks should be used for the underlay configurations.

.. code-block:: yaml
    
    underlay:
      router_id: 'Loopback0'
      vtep_name: 'Loopback1'
    
    <...snip...>

.. table::
   :widths: auto

================================================ ==========================================================================
**Parameter**                                                            **Comments**
================================================ ==========================================================================
**underlay** / :red:`mandatory`                  This option defines the underlay section.

**router_id** / :red:`mandatory`                 This option defines the name of the interface used as a Router ID.

                                                 The interface defined here will be used on all switches.

**vtep_name** / :red:`mandatory`                 This option defines the name of the interface used as the source VTEP.

                                                 The interface defined here will be used on all leaf switches.

================================================ ==========================================================================

OSPF definition
---------------

This section defines all OSPF details required for the underlay.

.. code-block:: yaml
    
    ospf:
      password: 'cisco123'
      area: '0.0.0.10'
    
    <...snip...>

.. table::
   :widths: auto

================================================ ==========================================================================
**Parameter**                                                            **Comments**
================================================ ==========================================================================
**ospf** / :red:`mandatory`                       This option defines the ospf section.

**password** / :red:`mandatory`                   This option defines the ospf password used to authenticate neighbors.

**area** / :red:`mandatory`                       This option defines the ospf area used in the underlay.

                                                  It accepts dotted format areas. In this example, area 10 is 0.0.0.10

================================================ ==========================================================================

BGP definition
--------------

This section defines all BGP details required for the configuration of the underlay.

.. code-block:: yaml
    
    bgp:
      as_number: '65010'
      password: 'cisco123'
      leafs_range: '192.168.210.0/24'
      spines:
      - '192.168.210.1'
      - '192.168.210.2'
    
    <...snip...>

.. table::
   :widths: auto

================================================ ==========================================================================
**Parameter**                                                            **Comments**
================================================ ==========================================================================
**bgp** / :red:`mandatory`                       This option defines the bgp section.

**as_number** / :red:`mandatory`                 This option defines the bgp ASN number.

**password** / :red:`mandatory`                  This option defines the bgp password used to authenticate neighbors.

**leafs_range** / :red:`mandatory`               This option defines the prefix range the spines will listen to when
                                                 forming peerings with the leafs.
                                                 
                                                 It must be in the same range as the IPs configured under the interface
                                                 defined as router_id in the section underlay.
                                                
**spines** / :red:`mandatory`                    This option defines a list of spine switches.

                                                 The IPs defined here are the same IPs configured under the interface
                                                 defined as router_id in the section underlay for all the Spine switches.

================================================ ==========================================================================

overlay_db.yml
==============

In this file information about the overlay is stored.
Let's check this file gradually step-by-step.

ANYCAST GATEWAY's MAC  definition
-----------------------------

This section defines global L2VPN EVPN parameters.

.. code-block:: yaml
    
    anycastgateway_mac: '0000.2222.3333'
    
    <...snip...>

.. table::
   :widths: auto

================================================ ==========================================================================
**Parameter**                                                            **Comments**
================================================ ==========================================================================
**anycastgateway_mac** / :red:`mandatory`              This option defines the MAC address to be used by each DAG SVI.
================================================ ==========================================================================

VRF definition
--------------

This section defines vrf parameters. Lets review parameters for unicast first.

.. code-block:: yaml

    vrfs:
      test:
        afs:
          - ipv4
        id: '100'  
        vlan: '4000'
        description: 'L3VNI-VRF-TEST'

    <...snip...>

.. table::
   :widths: auto
   
=============================================== ========================================================================== 
**Parameter**                                                            **Comments**
=============================================== ==========================================================================
**vrfs** / :red:`mandatory`                     This option defines the vrf section.

**<vrf_name>** / :red:`mandatory`               This option defines the vrf name.

**afs** / :red:`mandatory`                      | This option defines the address families which will be activated for the vrf.

                                                Option **ipv4** defines ipv4 address family.

                                                | Option **ipv6** defines ipv6 address family.

                                                **Choices:**

                                                * ipv4

                                                * ipv6

**id** / :red:`mandatory`                       This option defines the unique **id** for each VRF.

                                                **id** is a user defined and unique nuber between 100 and 999 used to
                                                automatically generate Route Targets and VNIs.

**vlan** / :red:`mandatory`                     This option defines the **vlan** per VRF.
                                                
                                                This option defines the vlan used for L3VNI/Transit Vlan in each VRF

**description** / :orange:`optional`            This option defines the description used by both VRF and Transtit Vlan
=============================================== ==========================================================================

VLANs section
-------------

This section defines the VLANs and their stitching with EVIs (EVPN instance) and VNIs (VXLAN network identifier).

.. code-block:: yaml

    vlans:
      101:
        description: 'vlan_101'
        vrf: 'test'
        svi:
          ipv4: '10.10.101.1 255.255.255.0'
          status: 'enabled'
    
      102:
        description: 'vlan_102'
        vrf: 'test'
        svi:
          ipv4: '10.10.102.1 255.255.255.0'
          status: 'disabled'

      103:
        description: 'vlan_103'
        vrf: 'test'

      300:
        description: 'primary_pvlan_test'
        vrf: 'test'
        pvlan:
          type: 'primary'
        svi:
          ipv4: '10.10.30.1 255.255.255.0'
          status: 'enabled'

      301:
        description: 'primary_pvlan_test'
        vrf: 'test'
        pvlan:
          type: 'isolated'
          primary: '300'

      302:
        description: 'primary_pvlan_test'
        vrf: 'test'
        pvlan:
          type: 'community'
          primary: '300'

    <...snip...>

.. table::
   :widths: auto

================================================ ==========================================================================
**Parameter**                                                            **Comments**
================================================ ==========================================================================
**vlans** / :red:`mandatory`                     This option defines the VLAN section.

**<vlan_id>** / :red:`mandatory`                 This option defines the VLAN ID. 
   
                                                 In the example shown, VLAN IDs are **101**, **102**, **103**, etc.
   
**description** / :orange:`optional`             This option defines the VLAN description.

**vrf** / :red:`mandatory`                       This option defines the VRF to be used to generate the VNIs as well the
                                                 VRF used by the SVI, if enabled
                                                    
**svis** / :orange:`optional`                    This option defines if an SVI for the VLAN needs to be created

**ipv4** / :red:`mandatory`                      This option defines the IPv4 address configured on the SVI. 
   
**status** / :red:`mandatory`                    | This option tells whether the SVI will be shut or not.

                                                 **Choices:**

                                                  * enabled

                                                  * disabled

**pvlan** / :orange:`optional`                    This option defines if the vlan is a private vlan

**type** / :red:`mandatory`                      | This option defines what private vlan type the vlan is.

                                                 **Choices:**

                                                  * primary

                                                  * isolated

                                                  * community

**primary** / :red:`mandatory`                   The primary vlan associated to the secondary vlan.

                                                 This field applies only if the type is **isolated** or **community**
================================================ ==========================================================================
          
dhcp_vars.yml
============

In this file inforrmation about DHCP configuration is stored.

.. code-block:: yaml

   dhcp:
     dhcp_options:
       option_82_link_selection_standard: standard
       option_82_server_id_override: standard
    
     vrfs:
       all:                   
         helper_address: 
           - 10.1.1.1

.. table::
   :widths: auto

   ========================================================= ==========================================================================
     **Parameter**                                                            **Comments**
   ========================================================= ==========================================================================
   **dhcp** / :red:`mandatory`                               This option defines the DHCP section.

   **dhcp_options** / :orange:`optional`                     This option defines DHCP options.

   **option_82_link_selection_standard** / :red:`mandatory`  This option defines the if cisco dhcp option/suboption 82[150] --> 82[5]
       
   **option_82_server_id_override** / :red:`mandatory`       This option defines the if cisco dhcp option/suboption 82[151] --> 82[11]  
   
   **vrfs** / :red:`mandatory`                               This option defines the VRF section
   ========================================================= ==========================================================================

Examples
--------

Example 1
^^^^^^^^^

DHCP Server is in the Layer 3 Default VRF and the DHCP Client is in the Tenant VRF

.. code-block:: yaml

    vrfs:  
      all:                                             
        helper_address:                                
          - 10.1.1.1                       
        helper_vrf: global                             
        relay_src_intf: Loopback1                     

As a result on **ALL** L2 SVIs for **ALL** VRFs ``helper-address`` **10.1.1.1** which is reachible over ``global`` VRF with **source-interface** ``Loopback1` will be configured.

Example 2 
^^^^^^^^^ 

DHCP Server is in the Layer 3 Default VRF and the DHCP Client is in the Tenant VRF

.. code-block:: yaml

    vrfs:  
      all:                                             <--------- Applies configs to all except 'green' DAG 
        helper_address:                                <--------- configs 'ip helper-address global 10.1.1.1' for all SVIs except green's
          - 10.1.1.1   
        helper_vrf: global                     
        relay_src_intf: Loopback1                      <--------- configs 'Loopback1' as DHCP relay source for all SVIs except green's
  
      green:                                           <--------- Applies configs to 'green' DAG 
        helper_address:                                <--------- configs 'ip helper-address global 10.1.1.2' for all 'green' DAG SVIs
          - 10.1.1.2                       
        helper_vrf: global  
        relay_src_intf: Loopback1                      <--------- configs 'Loopback1' as DHCP relay source for 'green' SVIs

Example 3 
^^^^^^^^^

DHCP Client and DHCP Server are in Different Tenant VRFs

.. code-block:: yaml

    vrfs:
      all:
        helper_address: 
          - 10.1.1.1
        helper_vrf: green                               <--------- Specifies the server tenant location
        relay_src_intf: Loopback1


Example 4
^^^^^^^^^

DHCP Server and DHCP Client are in the Same Tenant VRF

.. code-block:: yaml

    vrfs:
      all:                                              <--------- Applies configs to all DAGs
        helper_address:                                 <--------- configs 'ip helper-address 10.1.1.1' and 'ip helper-address 10.1.1.2' ll SVIs
          - 10.1.1.1
          - 10.1.1.2


Example 5
^^^^^^^^^

Repective DAG's interface from the overlay_interface section of host_vars/<inventory>.yml file is set as DHCP relay source interface for SVIs

.. code-block:: yaml

    vrfs:
      green:                                            <--------- Applies configs to 'green' DAG 
        helper_address:                                 <--------- configs 'ip helper-address 10.1.1.1' and 'ip helper-address 10.1.1.2' ll 'green' SVIs
          - 10.1.1.1
          - 10.1.1.2
        helper_vrf: green
        relay_src_intf: Loopback1                       <--------- configs 'Loopback1' as DHCP relay source for all 'green' SVIs
      blue:                                             <--------- Applies configs to 'blue' DAG 
        helper_address:                                 <--------- configs 'ip helper-address 10.1.1.3' for 'blue' SVIs
          - 10.1.1.3 
        helper_vrf: blue 
        relay_src_intf: Loopback2                       <--------- configs 'Loopback2' as DHCP relay source for all 'blue' SVIs

Since ``relay_src_intf`` key is explicitly mentioned in this case, Loopback1 is set as DHCP relay source interface for all :green:`green` SVIs and
Loopback2 is set as DHCP relay source interface for all :blue:`blue` SVIs.

host_vars
*********

This directory contains configuration specific to a device.

node_vars/<node_name>.yml
=========================

The file ``<node_name>.yml`` contains configurations, usually the ones related to interface and underlay, specific to a node.

Let us review the configuration in ``<node_name>.yml``.

Hostname section
----------------

This section defines the hostname of a node.

.. code-block:: yaml

    hostname: 'Leaf-01'

    <...snip...>


.. table::
    :widths: auto

=============================================== ==========================================================================
**Parameter**                                                            **Comments**
=============================================== ==========================================================================
**hostname** / :orange:`optional`               This option defines the remote device's hostname.
=============================================== ==========================================================================

Underlay Interfaces section
---------------------------

In this section, the configurations of the underlay interfaces are defined.

.. code-block:: yaml

    underlay_interfaces:
      Loopback0:
        name: 'ROUTER-ID'
        type: 'loopback'
        ip_address: '192.168.210.11'
        subnet_mask: '255.255.255.255'

      Loopback1:
        name: 'VTEP'
        type: 'loopback'
        ip_address: '192.168.211.11'
        subnet_mask: '255.255.255.255'

      GigabitEthernet1/0/23:
        name: 'UNDERLAY-FABRIC'
        type: 'slave'
        etherchannel_number: '1'

      GigabitEthernet1/0/24:
        name: 'UNDERLAY-FABRIC'
        type: 'slave'
        etherchannel_number: '1'

      Port-channel1:
        name: 'UNDERLAY-FABRIC'
        type: 'master'

    <...snip...>


.. table::
    :widths: auto

=============================================== ==========================================================================
**Parameter**                                                            **Comments**
=============================================== ==========================================================================
**underlay_interfaces** / :red:`mandatory`      This option defines the interface section.

**<interface_name>** / :red:`mandatory`         This option defines the interface name. For example: ``Loopback0`` or
                                                ``GigabitEthernet1/0/1``

**name** / :orange:`optional`                   This option defines the interface description.

**type** / :orange:`optional`                   | This option defines what type of interface is being configured.

                                                | When not defined, it defaults to **physical**

                                                **Choices:**

                                                 * physical

                                                 * loopback

                                                 * master

                                                 * slave

**etherchannel_number** / :red:`mandatory`      This option defines what port-channel (master) the interface belongs to.

                                                This field applies only if the type is **slave**

**ip_address** / :red:`mandatory`               This option defines the IPv4 address on the interface.

                                                This field applies only if the type is **loopback**

**subnet_mask** / :red:`mandatory`              This option defines the subnet mask for the IPv4 address.

                                                This field applies only if the type is **loopback**
=============================================== ==========================================================================

Overlay Interfaces section
--------------------------

In this section, the configurations of the overlay interfaces are defined.

.. code-block:: yaml

    overlay_interfaces:
      Loopback100:
        description: 'UNIQUE-LOOPBACK-VRF-TEST'
        ip_address: '10.1.10.11'
        subnet_mask: '255.255.255.255'
        vrf: 'test'
        loopback: 'yes'

    <...snip...>


.. table::
    :widths: auto

=============================================== ==========================================================================
**Parameter**                                                            **Comments**
=============================================== ==========================================================================
**overlay_interfaces** / :red:`mandatory`       This option defines the overlay_interfaces section.

**<interface_name>** / :red:`mandatory`         This option defines the interface name. For example: ``Loopback0`` or
                                                ``GigabitEthernet1/0/1``

**name** / :orange:`optional`                   This option defines the interface description.

**ip_address** / :red:`mandatory`               This option defines the IPv4 address on the interface.

**subnet_mask** / :red:`mandatory`              This option defines the subnet mask for the IPv4 address.

**vrf** / :red:`mandatory`                      This option defines the vrf to be associated with the interface.

**loopback** / :red:`optional`                  This option defines interface is a loopback. Defaults to ``no``
=============================================== ==========================================================================

access_intf/<node_name>.yml
===========================

The file ``<node_name>.yml`` contains configurations, related to access and trunk ports, related to a node.

Let us review the configuration in ``<node_name>.yml``.

Trunk configuration
-------------------

Vlans to be assigned to an interace are taken from the following in increasing **order of priority (3 > 2 > 1).**

.. note::

    **Trunk configuration order of priority (3 > 2 > 1)**
 
1. ``vlans`` in ``group_vars/overlay_db.yml`` (for ``playbook_access_add_commit/preview.yml``) or ``access_intf_cli`` in ``host_vars/inc_vars/<hostname>.yml`` 

(for ``playbook_access_incremental_commit/preview.yml``)
 
.. code-block:: yaml
    
    access_interfaces:              
      trunks:                       
        - GigabitEthernet1/0/6     

    <...snip...>


2. ``trunk_vlan_list`` in ``access_interfaces`` dictionary

.. code-block:: yaml
    
    access_interfaces:                
      trunk_vlan_list: 101,102,201     
      trunks:                         
        - GigabitEthernet1/0/6       
    
    <...snip...>

3. ``trunk_vlan_list`` in specific interface dictionary

.. code-block:: yaml

    access_interfaces:                 
      trunks:                          
        - GigabitEthernet1/0/6:        
          trunk_vlan_list: 101,102   
    
    <...snip...>


Access configuration
--------------------

Vlan to be assigned to an interace are taken from the following in increasing **order of priority (2 > 1).**

.. note::

    **Access configuration order of priority (2 > 1)**

1. ``access_vlan`` in ``access_interfaces`` dictionary

.. code-block:: yaml

    access_interfaces:               
        access_vlan: 101 
        access:                        
            - GigabitEthernet1/0/6       
        
    <...snip...>
    

2. ``access_vlan`` in specific interface dictionary

.. code-block:: yaml

    access_interfaces:               
      access:                        
        - GigabitEthernet1/0/6:      
          access_vlan: 102         

    <...snip...>



Examples
--------

There is an assumption, that in ``group_vars/overlay_db.yml`` defined next vlans: :green:`101,102,201,202`

Example 1
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      trunks:
        - GigabitEthernet1/0/7
        - GigabitEthernet1/0/8

Vlans assigned after execution:

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

Example 2
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      access_vlan: 202
      access:
        - GigabitEthernet1/0/7
        - GigabitEthernet1/0/8

Vlans assigned after execution:

**GigabitEthernet1/0/7** - :green:`202`

**GigabitEthernet1/0/8** - :green:`202`

Example 3
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      trunks:
        - GigabitEthernet1/0/6
        - GigabitEthernet1/0/7:
          trunk_vlan_list: 101,102,201
      access:
        - GigabitEthernet1/0/8
        - GigabitEthernet1/0/9
      access_vlan: 202

Vlans assigned after execution:

**GigabitEthernet1/0/6** - :green:`101,102,201,202` (from ``all.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/7** - :green:`101,102,201`

**GigabitEthernet1/0/8** - :green:`202`

**GigabitEthernet1/0/9** - :green:`202`

Example 4
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      trunks:
        - GigabitEthernet1/0/6
        - GigabitEthernet1/0/7:
          trunk_vlan_list: 101,102,201
      trunk_vlan_list: 101,201
      access:
        - GigabitEthernet1/0/8
        - GigabitEthernet1/0/9:
          access_vlan: 102
      access_vlan: 202

Vlans assigned after execution:

**GigabitEthernet1/0/6** - :green:`101,201`

**GigabitEthernet1/0/7** - :green:`101,102,201`

**GigabitEthernet1/0/8** - :green:`202`

**GigabitEthernet1/0/9** - :green:`102`

Example 5
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      trunks:
        - GigabitEthernet1/0/5
        - GigabitEthernet1/0/6:
          trunk_vlan_list: 101,102,201
        - GigabitEthernet1/0/7
      access:
        - GigabitEthernet1/0/8:
          access_vlan: 201
        - GigabitEthernet1/0/9:
          access_vlan: 102
      access_vlan: 202

Vlans assigned after execution:

**GigabitEthernet1/0/5** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/6** - :green:`101,102,201`

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`201`

**GigabitEthernet1/0/9** - :green:`102`

Example 6
^^^^^^^^^

Content of ``host_vars/access_intf/<hostname>.yml``

.. code-block:: yaml

    access_interfaces:
      trunks:
        - GigabitEthernet1/0/7
    access:
        - GigabitEthernet1/0/8:
          access_vlan: 201

Vlans assigned after execution:

**GigabitEthernet1/0/7** - :green:`101,102,201,202` (from ``group_vars/overlay_db.yml`` or ``host_vars/inc_vars/<hostname>.yml``)

**GigabitEthernet1/0/8** - :green:`201`
