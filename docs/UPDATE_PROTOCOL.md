# Engineering update protocol

Established: 2026-11-04 17:03:41 PST (America/Los_Angeles).
Equivalent UTC: 2026-11-05T01:03:41Z.

## Record each update

Use sequential identifiers: UPDATE-001, UPDATE-002, and so on. Each entry records:

- Event timestamp and timezone, if captured by the actual run.
- Documentation timestamp, separately from the event timestamp.
- Objective, machine/server and working directory, with account identifiers redacted.
- Exact commands, source revision and relevant tool versions when available.
- Supplied output and original screenshots, including failures and warnings.
- Interpretation, evidence limitations and status: verified, reported, pending or blocked.
- Changes made, verification performed and next action.
- Evidence paths and the Git commit that publishes the record, when available.

Never invent an event time from a message time, file modification time or documentation time. If unavailable, write “Event timestamp not captured.” Preserve original evidence; corrections receive a new entry explaining what changed. Public records exclude credentials, student identifiers and confidential or unlicensed material.

## Publication and verification

Keep the engineering log in Google Docs and this repository aligned. Verify writes before reporting publication. If one destination fails, record which destination is current and which remains pending. A pasted terminal transcript is a supplied record, not an independently captured execution log. A screenshot is a point-in-time observation, not proof of persistent state.

## Efficient continuity

Maintain CURRENT_STATUS.md as the short restart checkpoint. Read that file first, then only the evidence relevant to the next task. Keep detailed output in evidence files rather than duplicating it in the checkpoint. Update the checkpoint after meaningful progress, failures or corrections. Pending commands must never be promoted to completed without results.
