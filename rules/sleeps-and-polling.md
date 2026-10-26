# Sleeps and polling

Never hold a `sleep` longer than **30 seconds** in one tool call. When waiting
on CI, background jobs, or builds, poll in ≤30s increments (or use whatever
poll primitive the tool offers) and return control between polls so the user
can steer. Prefer announcing the check ("polling CI, back in a moment") over
blocking silently; only one long wait is ever justified — a final gate whose
output the next single step needs verbatim, and even then say so first.
