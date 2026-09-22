# The kit covers the personal workflow only

**Superseded by ADR-0007** (the kit is forge-agnostic): the repo makes no statement about the owner's work setup, and issue tracking is per-repo configuration.

This kit packages the owner's personal workflow: GitHub issues and PRs, the Matt Pocock main flow, research and review skills, and language-agnostic conventions. Work-stack support — GitLab MRs, Linear tickets, Django process rules, Cursor-specific integrations — is explicitly out of scope and lives in work-side configuration. The kit previously straddled both: `mr-review`, `linear-tickets`, `github-vs-gitlab-mcp`, `mr-review-chat-title`, `django-migrations`, and `engineering` carried the work forge and stack inside a kit published under the owner's personal GitHub. A personal kit that half-supports a work stack misleads consumers and drags work concerns into every session; the owner keeps a separate setup for work.
