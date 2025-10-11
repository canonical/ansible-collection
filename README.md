# Ansible Collection - maas.maas

## Getting Started

To start using this collection, install `ansible` or `ansible-core` packages. On a Debian or Ubuntu machine this can be done using:
```
sudo apt-get update
sudo apt-get -y install ansible-core
```

Then issue the following commmand to install the collection:
```
ansible-galaxy collection install maas.maas
```

Alternatively, you can install the collection directly from Github:
```
ansible-galaxy collection install git+https://github.com/canonical/ansible-collection.git
```

To verify the installation, issue the following command:
```
ansible-galaxy collection list | grep maas
```

## Sample Playbook

The following example demonstrates a very simple playbook to read a machine information using `fqdn` from MAAS:

```yaml
---
- name: Read a machine info
  hosts: localhost
  tasks:
    - name: List machines
      maas.maas.machine_info:
        cluster_instance:
          host: http://maas.example.com:5240/MAAS
          token_key: RK3XxE598ubXqvPnyq
          token_secret: JspVhytBzxVtSwzhmMczJTvT5kAVkMFx
          customer_key: E3CAjFSXtQAvqufCTZ
        fqdn: example-node-1.maas
      register: machines
    - ansible.builtin.debug:
        var: machines
```

Required information for the above template:

* *host* is the MAAS endpoint.
* *token_key*, *token_secret* and *customer_key* can be obtained from MAAS CLI:
```
sudo maas apikey --username admin
```
Example output:
```
E3CAjFSXtQAvqufCTZ:RK3XxE598ubXqvPnyq:JspVhytBzxVtSwzhmMczJTvT5kAVkMFx
```
* *fqdn* is the FQDN for a target machine.

To execute the playbook, issue the following command:
```
ansible-playbook sample.yaml
```

## Published Documentation

Read the current documentation directly on [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/maas/maas/).
