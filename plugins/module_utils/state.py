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
