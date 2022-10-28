# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import enum


class HostState(str, enum.Enum):
    ready = "ready"
    absent = "absent"
    deploy = "deploy"


class TaskState(str, enum.Enum):
    ready = "Ready"
    comissioning = "Commissioning"


class NicState(str, enum.Enum):
    present = "present"
    absent = "absent"


class MachineTaskState(str, enum.Enum):
    allocated = "Allocated"
    new = "New"
    broken = "Broken"
    deployed = "Deployed"
    ready = "Ready"
    comissioning = "Commissioning"
    failed = "Failed"
    deploying = "Deploying"
    allocating = "Allocating"
    testing = "Testing"
    failed_comissioning = "Failed Commissioning"
    failed_deployment = "Failed deployment"
