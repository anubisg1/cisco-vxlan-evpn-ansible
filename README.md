# Cisco VXLAN-EVPN Ansible Playbooks #

## Disclaimer ##

This project is based on <https://github.com/Cat9kEVPN/cat9k-evpn-ansible>
but with the goal to provide a much simpler abstraction for the end user

## Prerequisites ##

To run those ansibles playbook, you will require:  

**Hardware**:

* A linux server (Fedora, Ubuntu, RedHat, etc)
* Catalayst 9000 (Tested with 9300 and 9500 series)
  * network-advantage license
  * IOS-XE version >= 17.03 for leafs or >= 17.11 for the spines ( required by the dynamic peering configuration )
* Nexus 9k Switches supporting EVPN
  * Network LAN1-k9 or Essential
  * NX-OS >= 9.3

**Network-Expertise**:

* Basic network knowledge (network design, bring up of cat9k switches)  
* Basic understanding of YAML  
* Basic understanding of Python  
* Basic linux command line use  

## General description ##

<img width="1192" alt="ansible" src="https://user-images.githubusercontent.com/107021162/175528526-5d8b59ea-7f39-4d78-ac95-b08fed9ebbf6.png">

## Installation ##

It is recommended to run the project in the virtual environment.

Below you can find installation steps for Linux (ubuntu) server

* Install python3

```text
    sudo apt install python3 python3.10-venv
```

* Create the python virtual environment. In this example the virtual environment will be created in the folder ``virtual-env/ansible``

```text
    python3 -m venv ansible
```

More details could be found [here](https://docs.python.org/3/library/venv.html)

* Activate virtual environment.

```text
    source ansible/bin/activate
```

* Clone the repository

```text
    git clone https://github.com/anubisg1/cisco-vxlan-evpn-ansible.git
```

* Go to project directory

```text
    cd cisco-vxlan-evpn-ansible
```

* Install ``pip`` if it is not already installed

```text
    sudo apt install pip
```

* Install all necessary packages

```text
    pip install -r requirements.txt
```

* Next step ...

```text
    cd cat9k-playbooks
    ansible-playbook -i ../inventory playbook_xxx.yaml
```
