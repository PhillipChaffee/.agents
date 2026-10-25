# Repository setup rationale and sources

`setup-repository` installs maintained rule text word for word.
The [source record](rule-sources.md) identifies each payload, its source selection,
hash, and destination. A summary cannot preserve the questions, wording, and
read conditions that the user chose. Installation therefore copies literal bytes.

## Keep rule updates separate from installation

The TXT payloads are literal data with Markdown content for their destination
files. They retain the source grammar, wrapping, and paths. Writing review applies
to installer instructions and notes outside the payloads. Review any rule change
as a payload update with a new source record and independent expected hashes.

Preflight every destination before writing rules. Preserve existing project
configuration and require approval for conflicts. Exact block boundaries allow
byte comparisons without changing unrelated text. The existing domain guide
remains project-owned when present.

Source assumptions can conflict with another project's layout or language.
Report those conflicts instead of rewriting the payload during installation.
A source pin establishes identity, not suitability for every project.

## Reuse public setup dependencies

[full-lint][full-lint] owns language initializers and enforcement configuration.
The inspected revision is `4f982ea91585c6607bbba3a6a95da2555b88ded6`.
Read the selected initializer and templates together, and compare installed copies
with the recorded source. Earlier research identified source drift and the need
for separate execution evidence. Preserve sync failures and unresolved deviations.

[ADR-0002][language-decision] keeps language enforcement in the reference repo.
[ADR-0006][hygiene-decision] records this kit's hygiene baseline.
The rule payloads do not duplicate those tool configurations.

[Matt Pocock's skills][matt-skills] supply tracker/domain setup and domain modeling.
Reuse existing project configuration or request setup through those skills.
The literal evidence fragment supplies no tracker identity, consistent with
[ADR-0007][forge-decision].

## Separate fidelity from application evidence

Hash comparisons establish exact packaged and installed bytes.
They do not prove that an agent writes the correct target files, preserves
surrounding text, or handles conflicts. Those claims need actual target-install,
repeat-install, and conflict scenarios.

[obra/superpowers writing-skills][writing-skills], inspected at
`2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, supplies the behavioral testing method.
Earlier handoff-only simulations do not validate literal installation.
Record new application results separately from source inspection and kit-install
tests. Runtime readiness still requires checks in the target environment.

[full-lint]: https://github.com/PhillipChaffee/full-lint/tree/4f982ea91585c6607bbba3a6a95da2555b88ded6
[matt-skills]: https://github.com/mattpocock/skills
[writing-skills]: https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/writing-skills
[language-decision]: https://github.com/PhillipChaffee/.agents/blob/main/docs/adr/0002-no-language-rules.md
[hygiene-decision]: https://github.com/PhillipChaffee/.agents/blob/main/docs/adr/0006-hygiene-gates.md
[forge-decision]: https://github.com/PhillipChaffee/.agents/blob/main/docs/adr/0007-forge-agnostic.md
