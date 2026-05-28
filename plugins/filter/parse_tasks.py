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
    - A bare schema name like C(7zip) sets C(act) to an empty string; each
      schema role resolves its own default action via its schema vars.
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
        argv = item.split("-")
        argc = len(argv)
        schema = argv[0]
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
