# Coding rules

Apply the relevant sections to the affected code and its callers.
Summarize the decisions and evidence that affect the task.

## Before writing code

### Domain model and code placement

- What is the domain model? Is it right? Can I improve it?
- Where does each piece of functionality go in the codebase?
  - What folder/file? Do I need a new folder or file?
  - Does the functionality already exist?
  - Is it a reusable piece?
    - How widely can it be reused?
    - Does its location represent when and how it can be used?
- How should a single code file be organized?

If the change introduces or changes a domain concept, use `/domain-modeling`
with the existing [domain documentation rules](domain.md).
When deciding a module's interface, use `/codebase-design`.

Search for existing functionality and inspect its callers before adding code.
Put functionality in the module that owns its responsibility. Put shared code
where its actual consumers can reuse it. Keep entry points focused on wiring.
Follow the repository's existing conventions for organizing the file and its tests.

Complete this step when you can identify the existing implementation to reuse
or the owning file for new functionality, and the affected callers and tests.

### Frameworks and dependencies

- Am I using the existing frameworks already used correctly?
- Do I need to build this? Is there an off-the-shelf open source solution that
  is trustworthy?
- Should I introduce a new open source framework that would solve a lot of problems?

Check the documentation for the installed version before writing a workaround.
Look for a solution in project code, the standard library, or installed
dependencies first. For a proposed dependency, check its fit, maintenance,
compatibility, and license against the concrete problem and repository policies.
Explain what it replaces and the complexity it adds.

Complete this step when the intended framework use has a source and any proposed
dependency has a concrete benefit that justifies its ongoing cost.

## Docstring process

When writing or revising a docstring, use this process:

1. Determine how big the docstring should be.
   - Is the method simple? One or two lines. No `Args` or `Returns` sections.
   - Is it complex and the arguments or return value need explaining? Use a full
     docstring.
   - Choose the length by what callers need to know, including side effects and errors.
2. Understand the purpose of the method.
   - Read it and see how it is used in the codebase.
   - What does it take as arguments and what does it return? What does the data look like?
   - How would you define in clear simple English its abstract purpose?
     Think about it as an abstraction you need to explain to someone. Explain:
     - When/why they would want to use it.
     - What it does when you use it.
     - What side effects it has or what the return value is and what you would
       use that for. When would I want that side effect to occur or when would
       I want the return value?
3. Use that understanding to write the docstring.
   - Use the docstring convention configured in `pyproject.toml`.
   - If you include an `Args` section, describe every parameter.
   - Explain non-obvious data shapes, constraints, side effects, and errors that
     callers need to know.

Complete this step when the docstring explains when to use the method and what
the caller gets, and its stated behavior agrees with the implementation and callers.

## Review and simplification

First check the change against the requested behavior and scope. Then review
its quality using these questions:

- Can I simplify?
  - Is there a better/easier way to write this?
    - Less code.
    - Clearer.
    - More performant.
    - Using correct data structures.
  - Do I have methods that are only used once and should just be code in their
    calling function?
  - Is there overlapping functionality across several functions that should be
    consolidated into a reusable method?

Keep single-use methods that give behavior a useful name or hide complexity.
Consolidate functions when they share a responsibility. Preserve error handling
and validation when moving or merging code. Measure a performance change before
claiming an improvement.

If behavior changes, update the affected docstrings, comments, and documentation
in the same change.

Complete this step when the change satisfies the request, each added abstraction
has a current purpose, and affected callers, tests, and descriptions match the change.

## Evidence

- Have I proved my observations/assumptions?
- Have I proved my fix works?

1. Identify the behavior or assumption the conclusion depends on. Inspect its
   implementation and callers.
2. If the conclusion depends on runtime behavior, run the smallest check that
   can disprove the assumption. Compare the result with an independently
   established expectation.
3. For a bug fix, run the same reproduction before and after the change.
   Use the existing testing workflow and agreed test interfaces for regression
   coverage.
4. Run the required repository checks. Report the commands, environment, and
   actual results, using the existing [evidence distinctions](issue-tracker.md#evidence-and-completion).
5. State what remains untested and limit the conclusion to what the evidence supports.

Complete this step when each conclusion has supporting evidence, the applicable
checks pass, and the remaining limits are explicit. If a required check cannot
run, report the blocker and the missing evidence with the result.
