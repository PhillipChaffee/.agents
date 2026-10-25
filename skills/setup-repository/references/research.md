# Repository setup rationale and sources

`setup-repository` coordinates language initialization and working rules.
The [working-rules reference](working-rules.md) gives the adoption procedure.
This reference explains its source choices and evidence limits.

## Keep maintained sources authoritative

[full-lint][full-lint] owns the language initializers, templates, and enforcement
requirements. The inspected revision is
`4f982ea91585c6607bbba3a6a95da2555b88ded6`. It is a source snapshot, not a claim
about the latest branch or compatibility with a target environment.

The kit keeps language configuration in that reference repo, as recorded in
[ADR-0002][language-decision]. Its own hygiene checks follow
[ADR-0006][hygiene-decision]. Copying exact tool inventories into this skill
creates another configuration to maintain.

[Matt Pocock's skills][matt-skills] supply tracker/domain setup and domain
modeling. Read the dependency instructions available in the target environment.
Record their source revision or mark it unknown. The kit's
[ADR-0007][forge-decision] leaves tracker selection to each repository.

For placement and reuse, consult the kit's [code-organization][organization]
and [minimal-changes][minimal] rules. For source selection and work ownership,
consult [look-it-up][lookup] and [git-worktrees][worktrees]. These public links
also work when the skill directory is installed without the rest of this repo.

## Record provenance and execution separately

Provenance records where files came from and which revision supplied them.
Earlier research identified installed-source drift and the need to separate
source inspection from execution evidence. An installed skill name does not
identify its contents. A pinned revision does not prove that its templates agree
or that its commands work in another environment.

Before initialization, compare the initializer and templates at the same full
commit SHA. Compare any installed copy against that source. Preserve failed
sync checks and record an explicit resolution or accepted deviation.

When updating, compare the old source, new source, and adapted project files.
Keep justified project changes and rerun applicable checks. Record the new
revision alongside the commands, environment, results, and remaining gaps.

Execution records support only the environment and revision tested. A configured
workflow does not establish a successful run. Coverage reporting and merge
protection require their own evidence. Failed requests and unavailable access
remain unresolved evidence, even when local checks pass.

## Adopt optional practices when needed

If a project uses external reference implementations, record origins, revisions,
licenses, and reading paths. Keep reference snapshots separate from executable
dependencies. A checksum proves file identity, not runtime compatibility.

If a project teaches concepts, define the audience and learning goal before
choosing presentation tools. Keep one authoritative computation for repeated
numerical outputs. Assess arithmetic, visual presentation, and learner
understanding separately. The conditional table in [working rules](working-rules.md#select-optional-research-and-teaching-rules)
names the corresponding artifacts without prescribing a renderer or model.

## Test behavior and packaging separately

[obra/superpowers writing-skills][writing-skills], inspected at
`2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, supplies the behavioral testing method.
It compares fresh-agent responses without and with the skill, then tests varied
application scenarios. Planning simulations measure proposed actions. They do
not prove repository creation, command execution, or host discovery.

The public kit adds metadata and this portable reference to the tested procedure.
The original behavioral results describe the earlier package. Packaging checks
must separately establish metadata validity and installation of every reference.
Repeat behavioral cases after instruction changes, and test host discovery before
claiming that the intended installation is active.

[full-lint]: https://github.com/PhillipChaffee/full-lint/tree/4f982ea91585c6607bbba3a6a95da2555b88ded6
[matt-skills]: https://github.com/mattpocock/skills
[writing-skills]: https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/writing-skills
[language-decision]: https://github.com/PhillipChaffee/.agents/blob/main/docs/adr/0002-no-language-rules.md
[hygiene-decision]: https://github.com/PhillipChaffee/.agents/blob/main/docs/adr/0006-hygiene-gates.md
[forge-decision]: https://github.com/PhillipChaffee/.agents/blob/main/docs/adr/0007-forge-agnostic.md
[organization]: https://github.com/PhillipChaffee/.agents/blob/main/rules/code-organization.md
[minimal]: https://github.com/PhillipChaffee/.agents/blob/main/rules/minimal-changes.md
[lookup]: https://github.com/PhillipChaffee/.agents/blob/main/rules/look-it-up.md
[worktrees]: https://github.com/PhillipChaffee/.agents/blob/main/rules/git-worktrees.md
