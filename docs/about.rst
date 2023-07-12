About
=====

The main goal of this project is the automation of VXLAN EVPN networks with Catalyst 9000 or Nexus 9000

Custom Jinja templates and Python modules are used to build an initial config and modify the network configuration.

Project has a modular structure which gives an ability to introduce new features/services gradually step-by-step.

* `Usage Documentation <https://cisco-vxlan-evpn-ansible.readthedocs.io/en/latest/input.html>`_

Discalimer:
**************

This project is based on <https://github.com/Cat9kEVPN/cat9k-evpn-ansible>
but with the goal to provide a much simpler abstraction for the end user

Prerequisites:
**************

To run Cisco cat9k EVPN ansible playbook, you will require:  

**Hardware**:

* A linux server (Fedora, Ubuntu, RedHat, etc)
* Supported hardware:
 * Catalayst 9000 (Tested with 9300 and 9500 series)
 * Nexus 9300 (Playbooks for Nexus 9300 are not yet available)

**Licensing and Software Versions**:

* Catalayst 9000
 * network-advantage license
 * IOS-XE version >= 17.03 for leafs or >= 17.11 for the spines ( required by the dynamic peering configuration )
* Nexus 9300
 * Essential or LAN1K9 licenses
 * NX-OS >= 9.0
 
**Network-Expertise**:

* Basic network knowledge (network design, bring up of cat9k switches)  
* Basic understanding of YAML  
* Basic understanding of Python  
* Basic linux command line use  

