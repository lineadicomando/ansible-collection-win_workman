# Documentation

Backlog entries of the collection, indexed in [`TODO.md`](../../TODO.md).

## Audit the catalog drafts

**Priority:** P2 — a wrong page reads as documentation; start from the roles in use in the labs  
**Status:** proposed

45 of the 59 files in `docs/roles/catalog/` still open with
`> **Work in progress** — preliminary draft.` (2026-11-15; `goldendict.md`,
added in `d563ed2`, and `nodejs26.md` carry it too). Seven pages outside the
catalog carry the same banner and belong to the audit:
`management/display_scale.md`, `management/optimize.md`,
`management/autologon.md`, `management/system-tools.md`,
`management/ps_policy.md`, `core/dispatcher.md` and `core/pkg_utils.md`.
`docs/index.md`, `docs/architecture.md` and the `docs/roles/TEMPLATE-*.md` files
carry it as well.
The banner says nothing about whether the content is right, and both cases
exist:

- `sketchup2026.md` is accurate and current, `license` and `unlicense` included
   — the banner is simply stale.
- `autocadlt2026_en.md` and `autocadlt2026_it.md` documented two roles that had
  never existed under those names, with the wrong provider and the wrong
  installer filename. Deleted and replaced in `9304d43`.

A wrong draft is worse than no page, because it reads as documentation. Go
through them against the roles, fix what is wrong, and drop the banner from the
ones that earn it.

## Roles with no documentation at all

**Priority:** P3 — four pages, no wrong information in the meantime  
**Status:** proposed

Four roles have no page in `docs/roles/`: `googledrive`, `tinycad`, `winmerge`,
`winrar` (re-checked 2026-11-15 on 90 roles; `winmerge` is only named in passing
in `docs/roles/core/pkg_utils.md`). The roles added since 2026-10-01
(`autoshutdown`, `goldendict`, `domain`, `file_copy`, `nodejs26`, `openssh`,
`ps_policy`, `scoobe`, `visual_effects`, `win_iso`) all have a page.
`secure_ssh` has none on purpose: a deprecated alias, described in
`management/openssh.md`. `chkdsk`,
`logoff`, `ms_account`, `oobe`, `ping`, `sfc`, `shutdown`,
`widgets`, `wim` and `wol` are covered collectively by
`docs/roles/management/system-tools.md`; that page still carries the draft
banner, so it is checked under *Audit the catalog drafts*.

Unrelated slip found on the way: `docs/index.md` links `restart` to
`system-tools.md#restart` and lists it under system-tools, while the role has its
own page, `docs/roles/management/restart.md`; `system-tools.md` still has a
`## restart` section, a duplicate to merge or drop.
