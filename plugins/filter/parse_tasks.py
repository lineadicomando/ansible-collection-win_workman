# SPDX-License-Identifier: GPL-3.0-or-later
# Replicates the Jinja2 parsing logic from win_baseline/tasks/main.yaml.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: parse_tasks
  short_description: Parse win_workman task strings into structured objects
  description:
    - Converts a string or list of strings such as C(chrome-off) or
      C(veyon-on-master) into a list of dicts with keys
      C(task), C(schema), C(act), C(argc), C(argv).
    - A bare schema name like C(7zip) maps to C(act=on) (the default action).
  options:
    value:
      description: Task string or list of task strings.
      type: raw
      required: true
    action_default:
      description: Default action when none is specified.
      type: str
      required: false
      default: "on"
"""

EXAMPLES = r"""
- name: Parse task list
  ansible.builtin.set_fact:
    parsed: "{{ win_workman_tasks | lineadicomando.win_workman.parse_tasks }}"

- name: Parse with custom default action
  ansible.builtin.set_fact:
    parsed: "{{ win_workman_tasks | lineadicomando.win_workman.parse_tasks('off') }}"
"""

RETURN = r"""
  _value:
    description: >
      List of dicts, each with keys:
        task   (str):       original input string
        schema (str):       first token (before first dash)
        act    (str):       second token, or action_default if absent
        argc   (int):       number of dash-separated tokens
        argv   (list[str]): all tokens
    type: list
"""


def parse_tasks(value, action_default="on"):
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
        argv = item.split("-")
        argc = len(argv)
        schema = argv[0]
        act = argv[1] if argc > 1 else str(action_default)
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
