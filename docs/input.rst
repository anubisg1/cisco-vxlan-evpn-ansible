DAG (Distributed Anycast Gateway)
#################################

Distributed anycast gateway feature for EVPN VXLAN is a default gateway addressing mechanism that enables the use of the same gateway IP addresses 
across all the leaf switches that are part of a VXLAN network.

.. warning::

    The same subnet mask and IP address must be configured on all the switch virtual interfaces (SVIs) that act as a distributed anycast gateway (DAG).

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

``Leaf-1`` , ``Spine-01`` are the hostnames (nodes). Keep in mind that the names should be with the name of the configuration files 
in the directory ``host_vars``.

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

overlay_db.yml
==============

In this file information about the overlay is stored.
Let's check this file gradually step-by-step.

ANYCAST GATEWAY's MAC  definition
-----------------------------

This section defines global L2VPN EVPN parameters.

.. code-block:: yaml
    
    anycastgateway_mac: '0000.2222.3333'
    
    <...skip...>

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
    <...skip...>

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

   **description** / :orange:`optional`         This option defines the description used by both VRF and Transtit Vlan
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
                                                    
   ================================================ ==========================================================================
          
host_vars
*********

This directory contains configuration specific to a device.

<node_name>.yml
===============

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

Global routing section
----------------------

In this section, IPv4/IPv6 related parameters for global routing table are defined.


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **routing** / :red:`mandatory`                  This option defines the global routing section.

    **ipv4_uni** / :red:`mandatory`                 This option enables the global IPv4 unicast routing on the device.

    **ipv6_uni** / :red:`mandatory`                 This option enables the global IPv6 unicast routing on the device.

    **ipv6_multi** / :red:`mandatory`               This option enables the global IPv4 multicast routing on the device.

    =============================================== ==========================================================================

Interface section
-----------------

In this section, the configurations of the interfaces are defined.

.. code-block:: yaml

    interfaces:

      Loopback0:
        name: 'Routing Loopback'
        ip_address: '172.16.255.3'
        subnet_mask: '255.255.255.255'
        loopback: 'yes'
        pim_enable: 'no'

      Loopback1:
        name: 'NVE Loopback'
        ip_address: '172.16.254.3'
        subnet_mask: '255.255.255.255'
        loopback: 'yes'
        pim_enable: 'yes'

      GigabitEthernet1/0/1:
        name: 'Backbone interface to Spine-01'
        ip_address: '172.16.13.3'
        subnet_mask: '255.255.255.0'
        loopback: 'no'
        pim_enable: 'yes'

      GigabitEthernet1/0/2:
        name: 'Backbone interface to Spine-02'
        ip_address: '172.16.23.3'
        subnet_mask: '255.255.255.0'
        loopback: 'no'
        pim_enable: 'yes' 

    <...snip...>


.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **interfaces** / :red:`mandatory`               This option defines the interface section.

    **<interface_name>** / :red:`mandatory`         This option defines the interface name. For example: ``Loopback0`` or
                                                    ``GigabitEthernet1/0/1``

    **name** / :orange:`optional`                   This option defines the interface description.

    **ip_address** / :red:`mandatory`               This option defines the IPv4 address on the interface.

    **subnet_mask** / :red:`mandatory`              This option defines the subnet mask for the IPv4 address.

    **loopback** / :red:`mandatory`                 | This option tells whether the interface is loopback or not.

                                                    **Choices:**

                                                    * yes

                                                    * no

    **pim_enable** / :red:`mandatory`               | This option tells whether PIM must be enabled on the interface.

                                                    **Choices:**

                                                    * yes

                                                    * no
    =============================================== ==========================================================================

OSPF section
------------

This section defines the OSPF parameters.

By default, next OSPF configurations are applied:

* Interface network type - **point-to-point**

* OSPF process ID - **1**

* OSPF area number - **0**

OSPF **router-id** is a configurable parameter.

.. code-block:: yaml

    ospf:
      router_id: '172.16.255.3'

    <...snip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **ospf** / :red:`mandatory`                     This option defines the OSPF section.
    
    **router_id** / :red:`mandatory`                This option defines the OSPF router-id.
    =============================================== ==========================================================================

PIM section
-----------

This section defines global PIM parameters. This section is optional if Ingress-Replication in the core is used.


.. code-block:: yaml

    pim:
      rp_address: '172.16.255.255'
    
    <...skip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **pim** / :red:`mandatory`                      This option defines the PIM section.
    
    **rp_address** / :red:`mandatory`               This option defines the RP address.
    =============================================== ==========================================================================

MSDP section
------------

This section defines the MSDP parameters. Usually, MSDP is used for configuration RP redundancy in the underlay.

This section is optional.

.. code-block:: yaml
    
    msdp:
      '1':
        peer_ip: '172.16.254.2'
        source_interface: 'Loopback1'
        remote_as: '65001'

    <...skip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **msdp** / :red:`mandatory`                     This option defines the MSDP section.
    
    **<msdp_neighbor_id>** / :red:`mandatory`       This option defines ID for the MSDP peer. This number is not used in the 

                                                    switch configuration, just index number.

    **peer_ip** / :red: `mandatory`                 This option defines the MSDP peer's IPv4 address.

    **source_interface** / :red: `mandatory`        This option defines the IP address of the source interface which will be 
                                                    used as a source IP for the MSDP session.

    **remote_as** / :red: `mandatory`               This option is used for defining the BGP AS number of the MSDP
                                                    peer.                               
    =============================================== ==========================================================================

BGP section
-----------

This section defines BGP parameters. 

By default next design assumption are made:

* Leafs are Route-Reflector clients

* Two present Spines in the topology are Route-Reflectors


.. code-block:: yaml

    bgp:
      as_number: '65001'
      router_id: 'Loopback0'
      neighbors:
        '172.16.255.1':
          peer_as_number: '65001'
          source_interface: 'Loopback0'

        '172.16.255.2':
          peer_as_number: '65001'
          source_interface: 'Loopback0'

        '172.16.255.3':
          peer_as_number: '65001'
          source_interface: 'Loopback0'
          rrc: 'yes'
    
    <...snip...>

.. table::
    :widths: auto

    =============================================== ==========================================================================
    **Parameter**                                                            **Comments**
    =============================================== ==========================================================================
    **bgp** / :red:`mandatory`                      This option defines BGP section globally.
    
    **as_number** / :red:`mandatory`                This option defines BGP AS number.

    **router_id** / :red:`mandatory`                This option defines interface which ip address will be used like BGP router ID.

    **neighbors** / :red:`mandatory`                This option defines neighbors section.

    **neigbor_ip_address** / :red:`mandatory`       This option defines BGP neighbor ip address

    **peer_as_number** / :red:`mandatory`           This option defines BGP neighbor AS number

    **source_interface** / :red:`mandatory`         This option defines source interface which ip address will be used like a SRC IP

                                                    for BGP session.

    **rrc** / :orange:`optional`                    This option defines the peer like a BGP route-reflector client.
    =============================================== ==========================================================================

Access interface configuration
==============================

This section defines configuration for the customer-facing access interfaces.

By default all access interfaces will be configured like trunks with all L2VNI vlans that are mentioned in ``group_vars/overlay_db.yml``

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
