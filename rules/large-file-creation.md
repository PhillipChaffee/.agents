---
alwaysApply: true
description: >-
  Write files larger than 1000 lines in chunks of 1000 lines or fewer and verify
  the final line count with wc -l.
---

# Large file creation

When creating files larger than ~1000 lines:

- Never emit the full content in one Write/heredoc call.
- Write the header/first section, then append successive sections
  with Edit or `cat >>` heredocs of <=1000 lines each.
- Verify with `wc -l` after the final append.
