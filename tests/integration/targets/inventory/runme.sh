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

# Inject maas_inventory.yml with needed values before running tests
# Use examples/maas_inventory.yml as template.
# cat file to fail early if maas_inventory.yml is missing.
cat "$(dirname "$(realpath "$0")")/maas_inventory_status_ready.yml"


export ANSIBLE_PYTHON_INTERPRETER="$ANSIBLE_TEST_PYTHON_INTERPRETER"

function cleanup {
    unset ANSIBLE_CACHE_PLUGIN
    unset ANSIBLE_CACHE_PLUGIN_CONNECTION
}

trap 'cleanup "$@"' EXIT


ansible-playbook -e "@$vars_file" cleanup.yml
ansible-playbook -e "@$vars_file" prepare.yml

# Add more inventory files to test other possible machine status.
ansible-playbook -i localhost, -i maas_inventory_status_commissioning.yml -e "@$vars_file" run_status_commissioning_test.yml
ansible-playbook -i localhost, -i maas_inventory_status_ready.yml -e "@$vars_file" run_status_ready_test.yml
ansible-playbook -i localhost, -i maas_inventory_no_status.yml -e "@$vars_file" run_no_status_test.yml

ansible-playbook -e "@$vars_file" cleanup.yml
