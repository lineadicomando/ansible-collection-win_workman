#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

DOCUMENTATION = r'''
---
module: seb_config
short_description: Generate or remove a Safe Exam Browser .seb settings file
version_added: "0.1.0"
description:
  - Generates an unencrypted Safe Exam Browser client settings file (.seb) from a settings dictionary.
  - Can also remove a generated file.
options:
  dest:
    description:
      - Destination path of the .seb file on the managed node.
    type: path
    required: true
  settings:
    description:
      - Safe Exam Browser settings dictionary to serialize as XML plist.
      - Required when C(state=present).
    type: dict
    required: false
    default: {}
  state:
    description:
      - Whether the settings file should exist.
    type: str
    choices: [present, absent]
    default: present
author:
  - lineadicomando
'''

EXAMPLES = r'''
- name: Generate SebClientSettings.seb
  lineadicomando.win_workman.seb_config:
    dest: 'C:\\ProgramData\\SafeExamBrowser\\SebClientSettings.seb'
    state: present
    settings:
      startURL: 'https://moodle.example.test'
      allowQuit: false

- name: Remove SebClientSettings.seb
  lineadicomando.win_workman.seb_config:
    dest: 'C:\\ProgramData\\SafeExamBrowser\\SebClientSettings.seb'
    state: absent
'''

RETURN = r'''
dest:
  description: Destination file path.
  returned: always
  type: str
changed:
  description: Whether any change was made.
  returned: always
  type: bool
size:
  description: Generated file size in bytes when state=present.
  returned: when state=present
  type: int
state:
  description: Final state.
  returned: always
  type: str
config_key:
  description: >
    SHA-256 hex digest of the generated .seb file bytes.
    EXPERIMENTAL: intended as the SEB Config Key for Moodle, but the exact
    calculation used internally by SEB has not been independently verified.
    Cross-check with SEB Config Tool before registering in Moodle.
  returned: when state=present
  type: str
'''

import hashlib
import os
import plistlib
import gzip

from ansible.module_utils.basic import AnsibleModule


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def _build_payload(settings: dict) -> bytes:
    try:
        return plistlib.dumps(settings, fmt=plistlib.FMT_XML, sort_keys=True)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("Unable to serialize settings as plist XML: {0}".format(exc))


def _build_seb_file(settings: dict) -> bytes:
    # mtime=0 ensures deterministic output for idempotency
    xml_gz = gzip.compress(_build_payload(settings), mtime=0)
    return gzip.compress(b'plnd' + xml_gz, mtime=0)


def run_module() -> None:
    module_args = dict(
        dest=dict(type='path', required=True),
        settings=dict(type='dict', required=False, default={}),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    dest = module.params['dest']
    settings = module.params['settings']
    state = module.params['state']

    result = {
        'changed': False,
        'dest': dest,
        'state': state,
    }

    if state == 'absent':
        exists = os.path.exists(dest)
        if exists:
            if module.check_mode:
                result['changed'] = True
                module.exit_json(**result)
            try:
                os.remove(dest)
            except OSError as exc:
                module.fail_json(msg="Failed to remove file '{0}': {1}".format(dest, exc), **result)
            result['changed'] = True
        module.exit_json(**result)

    if not isinstance(settings, dict):
        module.fail_json(msg="'settings' must be a dictionary when state=present", **result)

    try:
        payload = _build_seb_file(settings)
    except ValueError as exc:
        module.fail_json(msg=str(exc), **result)

    current = None
    if os.path.exists(dest):
        try:
            with open(dest, 'rb') as existing_file:
                current = existing_file.read()
        except OSError as exc:
            module.fail_json(msg="Failed to read existing file '{0}': {1}".format(dest, exc), **result)

    if current != payload:
        result['changed'] = True
        if not module.check_mode:
            try:
                _ensure_parent(dest)
                with open(dest, 'wb') as out:
                    out.write(payload)
            except OSError as exc:
                module.fail_json(msg="Failed to write file '{0}': {1}".format(dest, exc), **result)

    result['size'] = len(payload)
    result['config_key'] = hashlib.sha256(payload).hexdigest()
    module.exit_json(**result)


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
