# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: file_copy_manifest
  short_description: Describe the controller files a file_copy item would push
  description:
    - Takes the items of C(win_workman_file_copy_items) and returns, for each
      one, what C(win_copy) will put on the host - every file with its path
      relative to the destination, size and SHA1 - plus the top-level names a
      C(remove) has to delete.
    - Every C(src) is resolved inside O(root). An absolute path, a C(..)
      segment, a path that resolves outside O(root) through a symbolic link,
      or a symbolic link inside a source directory fails the lookup, so a
      caller of the role cannot push arbitrary controller files such as vault
      files or private keys.
    - A C(src) ending in C(/) means the contents of the directory, as in
      C(win_copy).
  options:
    _terms:
      description: The file_copy items, dicts with at least C(src).
      type: list
      elements: dict
      required: true
    root:
      description: Controller directory every C(src) is relative to.
      type: str
      required: true
"""

EXAMPLES = r"""
- name: Describe the items to push
  ansible.builtin.set_fact:
    manifests: >-
      {{ query('lineadicomando.win_workman.file_copy_manifest',
               *win_workman_file_copy_items, root=win_workman_file_copy_root) }}
"""

RETURN = r"""
  _raw:
    description: One dict per item, in the order of the items.
    type: list
    elements: dict
    contains:
      src_path:
        description: Absolute controller path, with a trailing C(/) for contents.
      name:
        description: Base name of the source.
      kind:
        description: C(file) or C(dir).
      contents:
        description: True when only the contents of the directory are copied.
      entries:
        description: Files as C({rel, size, sha1}), C(rel) relative to the destination, backslash-separated.
      top:
        description: Names created directly in the destination, which C(remove) deletes.
      files:
        description: Number of files.
      bytes:
        description: Total size in bytes.
      index:
        description: Position of the item in the list.
      archive:
        description: True when the item is a directory to transfer as a zip.
"""

import hashlib
import os
import re

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.lookup import LookupBase

_WINDOWS_ABSOLUTE = re.compile(r"^([A-Za-z]:|[\\/])")


def _sha1(path):
    digest = hashlib.sha1()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(path, root):
    return path == root or path.startswith(root + os.sep)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        root = self.get_option("root")
        if not root:
            raise AnsibleLookupError("file_copy_manifest: root is required")
        root = os.path.realpath(os.path.expanduser(to_text(root)))
        if not os.path.isdir(root):
            raise AnsibleLookupError(
                "file_copy: the source root %s does not exist on the controller" % root
            )

        manifests = []
        for index, item in enumerate(terms):
            manifest = self._manifest(item, root)
            manifest["index"] = index
            manifest["archive"] = manifest["kind"] == "dir" and bool(item.get("archive", False))
            manifests.append(manifest)
        return manifests

    def _manifest(self, item, root):
        if not isinstance(item, dict) or not item.get("src"):
            raise AnsibleLookupError("file_copy: every item needs a src, got %r" % (item,))

        src = to_text(item["src"]).strip()
        contents = src.endswith("/")
        relative = src.rstrip("/")
        parts = re.split(r"[\\/]+", relative)

        if _WINDOWS_ABSOLUTE.match(src) or os.path.isabs(src):
            raise AnsibleLookupError(
                "file_copy: src %r must be relative to %s" % (src, root)
            )
        if ".." in parts or not relative or relative == ".":
            raise AnsibleLookupError(
                "file_copy: src %r must name a file or directory below %s" % (src, root)
            )

        path = os.path.realpath(os.path.join(root, relative))
        if not _inside(path, root) or path == root:
            raise AnsibleLookupError(
                "file_copy: src %r resolves to %s, outside %s" % (src, path, root)
            )
        if not os.path.exists(path):
            raise AnsibleLookupError("file_copy: src %r not found in %s" % (src, root))

        name = os.path.basename(path)
        if os.path.isfile(path):
            if contents:
                raise AnsibleLookupError(
                    "file_copy: src %r ends in / but is a file" % src
                )
            size = os.path.getsize(path)
            return {
                "src_path": path,
                "name": name,
                "kind": "file",
                "contents": False,
                "entries": [{"rel": name, "size": size, "sha1": _sha1(path)}],
                "top": [name],
                "files": 1,
                "bytes": size,
            }

        prefix = "" if contents else name + "\\"
        entries = []
        total = 0
        for current, dirs, files in os.walk(path):
            for entry in dirs + files:
                full = os.path.join(current, entry)
                if os.path.islink(full):
                    raise AnsibleLookupError(
                        "file_copy: %s is a symbolic link; links inside a pushed "
                        "directory are not supported" % full
                    )
            dirs.sort()
            for filename in sorted(files):
                full = os.path.join(current, filename)
                rel = os.path.relpath(full, path).replace(os.sep, "\\")
                size = os.path.getsize(full)
                total += size
                entries.append({"rel": prefix + rel, "size": size, "sha1": _sha1(full)})

        top = sorted(os.listdir(path)) if contents else [name]
        return {
            "src_path": path + ("/" if contents else ""),
            "name": name,
            "kind": "dir",
            "contents": contents,
            "entries": entries,
            "top": top,
            "files": len(entries),
            "bytes": total,
        }
