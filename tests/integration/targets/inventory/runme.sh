#!/usr/bin/env bash

readonly vars_file=../../integration_config.yml

eval "$(cat <<EOF | python
import yaml
with open("$vars_file") as fd:
    data = yaml.safe_load(fd)
print("export MAAS_HOST='{}'".format(data["host"]))
print("export MAAS_TOKEN_KEY='{}'".format(data["token_key"]))
print("export MAAS_TOKEN_SECRET='{}'".format(data["token_secret"]))
print("export MAAS_CUSTOMER_KEY='{}'".format(data["customer_key"]))
EOF
)"

env | grep MAAS_

set -eux

export ANSIBLE_PYTHON_INTERPRETER="$ANSIBLE_TEST_PYTHON_INTERPRETER"

function cleanup {
    unset ANSIBLE_CACHE_PLUGIN
    unset ANSIBLE_CACHE_PLUGIN_CONNECTION
}

trap 'cleanup "$@"' EXIT


ansible-playbook -e "@$vars_file" common/cleanup.yml
ansible-playbook -e "@$vars_file" common/prepare.yml

# Add more inventory files to test other possible machine status.
ansible-playbook -i localhost, -i maas_inventory_no_status.yml -e "@$vars_file" common/run_no_status_test.yml

ansible-playbook -e "@$vars_file" common/cleanup.yml
