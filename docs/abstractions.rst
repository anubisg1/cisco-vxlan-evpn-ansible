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
