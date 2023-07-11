Abstracted Configurations
#################################

DAG (Distributed Anycast Gateway)
*********************************

Distributed anycast gateway feature for EVPN VXLAN is a default gateway addressing mechanism that enables the use of the same gateway IP addresses 
across all the leaf switches that are part of a VXLAN network.

.. warning::

    The same subnet mask and IP address must be configured on all the switch virtual interfaces (SVIs) that act as a distributed anycast gateway (DAG).

BUM (Broadcast, Unicast, Multicast) Replication
***********************************************

Ingress Replication is used without requiring any input from the user

VNI definition
**************

VNI are automatically generated from the VRF's ID:

**L3VNI** is the VRF ID with 0000 appended.
For example if the VRF ID is 100, the L3VNI will be 1000000

**L2VNI** is the VRF ID with the vlan numnber appended (0s are prepended to the vlan id so that we always have 4 digits)
For example if the VRF ID is 100 and the vlan id is 20, the L2VNI will be 1000020

RD definition
*************

Route Distinguishers are defined as **Loopback0_IP:VRF_Transit_vlan**

RT definition
*************

For the VRFs, Route Targets are defined as **BGP_ASN:L3VNI**
For Vlans, the Route Targets are left to **auto** and therefore equal to **BGP_ASN:L2VNI**

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

    <...snip...>

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

Interface section
-----------------

In this section, the configurations of the interfaces are defined.

.. code-block:: yaml

    interfaces:

      Loopback0:
        name: 'ROUTER-ID'
        ip_address: '192.168.210.11'
        subnet_mask: '255.255.255.255'
        type: 'loopback'

      Loopback1:
        name: 'VTEP'
        ip_address: '192.168.211.11'
        subnet_mask: '255.255.255.255'
        type: 'loopback'

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
    **interfaces** / :red:`mandatory`               This option defines the interface section.

    **<interface_name>** / :red:`mandatory`         This option defines the interface name. For example: ``Loopback0`` or
                                                    ``GigabitEthernet1/0/1``

    **name** / :orange:`optional`                   This option defines the interface description.

    **ip_address** / :red:`mandatory`               This option defines the IPv4 address on the interface.

    **subnet_mask** / :red:`mandatory`              This option defines the subnet mask for the IPv4 address.
    =============================================== ==========================================================================
    