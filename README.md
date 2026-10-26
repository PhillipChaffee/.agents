# .agents

[![validate](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml/badge.svg)](https://github.com/PhillipChaffee/.agents/actions/workflows/validate.yml) [![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

My public agent setup, synced from `~/.agents`. Home additions, edits, and
deletions define the published agent content. Repository documentation,
installation, validation, and CI live alongside that content.

## Contents

- **One active skill:** `writing-skills`, copied from
  [Superpowers](https://github.com/obra/superpowers). Its companion plugin skills
  and runtime guides remain external dependencies.
- **Five research agents:** `researcher-lite`, `researcher-mid`, `researcher-deep`,
  `research-planner`, and `research-synthesizer`.
- **Four rules:** `look-it-up`, `new-repo-setup`, `opencode-config-profiles`, and
  `sleeps-and-polling`. Profile names and paths describe my setup, not required
  consumer configuration.
- **37 disabled skills:** the dated Matt Pocock archive in `skills-disabled/`.
  These are preserved as source, not installed or activated.

`agents.kit.md` mirrors the home instruction file and installs as
`~/.agents/agents.md`. The repository's own `agents.md` is separate.
The lockfiles record public upstream provenance; `.kit-stamp` is generated
installation state and is not published. Home `scripts/` are not published.

Third-party directories retain their source bytes. Their formatting and
example links are excluded from cosmetic lint, but not from secret scanning.
See [third-party notices](THIRD-PARTY-NOTICES.md) for licenses and pinned sources.
Historical design decisions are retained in [docs/adr/](docs/adr/).

## Install

```sh
git clone https://github.com/PhillipChaffee/.agents.git
cd .agents
./scripts/install.sh --target agents
```

The installer copies active skills and their assets, agents, rules, the home
instruction file, and license notices into `~/.agents`. It does not install
the disabled archive, source lockfiles, or repository-only scripts.

Unstamped files that differ are skipped unless `--force` is supplied. Managed
files can be overwritten: preserve local edits before reinstalling. `--dry-run`
previews changes; `--prune` removes obsolete managed files; `--uninstall` removes
managed files while preserving unmanaged files. `--pull` updates existing
mapped source files only; it does not import new paths or deletions.

Configure models and MCP servers in your harness. Never commit provider keys,
tokens, or private configuration.

## Checks

```sh
./scripts/validate.sh
python3 -m unittest discover -s tests
```

CI also checks spelling, Markdown, links, secrets, duplicated code, shell
scripts, and workflow configuration.
