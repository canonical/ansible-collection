# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import random

from .errors import MaasError


class Multipart:
    SAFE_CHARS = "0123456789abcdefghijklmnoprstuvzABCDEFGHIJKLMNOPRSTUVZ"
    RN = "\r\n"

    @staticmethod
    def generate_boundary():
        boundary = ""
        for i in range(0, 32):
            boundary += random.choice(Multipart.SAFE_CHARS)
        return boundary

    @staticmethod
    def get_mulipart(data):
        rn = Multipart.RN
        boundary = Multipart.generate_boundary()
        if not isinstance(data, dict):
            raise MaasError("Data should be dict!")

        content = ""
        for k, v in data.items():
            content += f"--{boundary}{rn}"
            content += f'Content-Disposition: form-data; name="{k}"{rn}{rn}'
            content += str(v)
            content += rn
        content += f"--{boundary}--"
        return boundary, content.encode("utf-8")
