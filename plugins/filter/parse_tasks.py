# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os

from ansible.errors import AnsibleFilterError

_ROLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "roles")
# Reachable by name, but not meant to be dispatched to
_INTERNAL_ROLES = ("dispatcher", "pkg_utils")

DOCUMENTATION = r"""
  name: parse_tasks
  short_description: Parse win_workman task strings into structured objects
  description:
    - Converts a string or list of strings such as C(chrome-off) or
      C(veyon-on-master) into a list of dicts with keys
      C(task), C(schema), C(act), C(argc), C(argv).
    - A bare schema name like C(7zip) sets C(act) to an empty string; each
      schema role resolves its own default action via its schema vars.
    - Fails on a task whose first token is not a role of the collection, naming
      the task, instead of leaving it to a role-not-found error downstream.
  options:
    value:
      description: Task string or list of task strings.
      type: raw
      required: true
"""

EXAMPLES = r"""
- name: Parse task list
  ansible.builtin.set_fact:
    parsed: "{{ win_workman_tasks | lineadicomando.win_workman.parse_tasks }}"
"""

RETURN = r"""
  _value:
    description: >
      List of dicts, each with keys:
        task   (str):       original input string
        schema (str):       first token (before first dash)
        act    (str):       second token, or empty string if absent
        argc   (int):       number of dash-separated tokens
        argv   (list[str]): all tokens
    type: list
"""


def parse_tasks(value):
    if isinstance(value, str):
        raw = [value]
    elif hasattr(value, "__iter__"):
        raw = list(value)
    else:
        raw = [str(value)]

    result = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            continue
        item = item.strip()
        argv = item.split("-")
        argc = len(argv)
        schema = argv[0]
        if schema in _INTERNAL_ROLES or not os.path.isdir(os.path.join(_ROLES_DIR, schema)):
            raise AnsibleFilterError(
                "Unknown win_workman task '%s': there is no role named '%s'" % (item, schema)
            )
        act = argv[1] if argc > 1 else ""
        result.append(
            {
                "task": item,
                "schema": schema,
                "act": act,
                "argc": argc,
                "argv": argv,
            }
        )
    return result


class FilterModule(object):
    def filters(self):
        return {"parse_tasks": parse_tasks}
