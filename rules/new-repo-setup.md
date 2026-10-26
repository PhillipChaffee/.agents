# New Repository Setup

Every new repository starts from the strictest-setups reference repo at
https://github.com/PhillipChaffee/67-sus-95-clean: one folder per language
carrying the canonical lint, type-check, docstring/comment, formatter,
coverage-gate, and hygiene/supply-chain gate config — coverage ≥ 95%, enforced by the machine, not by
aspiration. The hygiene and supply-chain set is machine-enforced everywhere:
spell check, secret scan, copy-paste detection, markdown lint, link check,
dependency advisories and licenses, artifact linting, plus the language's own
unused-dependency, import-layer, lockfile-integrity, and TODO-marker gates,
with nightly mutation testing where the pinned tools can tell the truth.
Never hand-roll lint, type, doc, formatter, coverage, or hygiene config for a
new repo from memory; the reference repo is the baseline.

This applies whenever a new repository is being created, scaffolded, or
bootstrapped — a new project, greenfield service, or fresh package with its
own git tree. It does not rewire enforcement inside an existing repo.

1. **Language has a folder in the repo** (`<lang>/` at the repo root):
   bootstrap with the matching `init-<lang>-repo` skill (`init-python-repo`,
   `init-go-repo`, `init-rust-repo`, `init-typescript-repo`, …) and follow it
   exactly — it copies the canonical templates and runs every gate before
   the first commit. Where the skill is not loaded in this harness, read and
   follow it — installed at `~/.config/opencode/skills/init-<lang>-repo/SKILL.md`, or
   in the repo at `<lang>/init-<lang>-repo/SKILL.md` — and copy its
   `templates/`.
2. **Language has no folder yet**: do not invent a setup. First extend the
   reference repo — clone https://github.com/PhillipChaffee/67-sus-95-clean
   and run the `add-language` skill (`~/.config/opencode/skills/add-language/SKILL.md`,
   or `add-language/SKILL.md` in the repo) on the clone: research from
   official sources, author the folder, and prove the coverage gate fails a
   build under 95% — then bootstrap the new repo per rule 1.
3. **The reference repo itself is the only exception**: it is extended with
   `add-language`, never initialized from its own templates.

Canonical copy. Mirrored into: `~/.config/opencode/AGENTS.md` (section
`new-repo-setup`), `~/.claude/rules/new-repo-setup.md`, `~/.codex/AGENTS.md`,
`~/.cursor/rules/new-repo-setup.mdc`, and `~/.config/goose/.goosehints`
(condensed).