# Ready-to-use lower-power agent handoff

The primary agent researched two contrasting pilots and used the results to
write the workflow, schema and validators. The current queue contains 28 I2C
boards: two completed pilots and 26 pending. The analog ADXL335 is excluded from
this research batch. AliExpress remains deferred.

Project agent: `.codex/agents/i2c-part-researcher.toml`, named
`i2c_part_researcher`. This uses the documented standalone project-agent format:
[official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).
Its model setting is intentionally omitted so it inherits the parent model
selected at handoff. The initial pilots did not launch a lower-power bulk run.

After selecting the intended lower-power model, use this prompt:

> Use the project agent `i2c_part_researcher` to research all remaining pending
> or partial I2C peripheral boards in `research/i2c_breakouts/research_queue.yaml`.
> Read `research/i2c_breakouts/AGENT_WORKFLOW.md`, `RESEARCH_SCHEMA.md`, and
> `PILOT_LESSONS.md` before starting. Process one board at a time, use the in-app
> browser for discovery and review, archive each official default website and
> available chip datasheet, and collect dimensions, physical pin counts/names,
> electrical/I2C details, software and extra resources into
> `source_file/<exact_part_id>/working.yaml`. Use the existing helper commands,
> preserve IDs and source evidence, validate and update the queue after each
> board, and continue until the assigned queue is processed. Keep useful partial
> results for unavailable sources and report precise gaps. Do not modify the
> populate definitions, `parts_source`, `parts`, browser settings, or AliExpress
> candidates. Finish by reporting researched/partial/pending counts and important
> unresolved conflicts with file links.

Useful review commands:

```powershell
python tools/i2c_part_research.py queue
python tools/i2c_part_research.py validate
python -m unittest discover -s tests -p test_i2c_research.py -v
```

The validator provides structural/file-integrity checks, not proof of factual
accuracy. Review carrier identity, source conflicts, voltage restrictions and
pin semantics before promoting research into the authoritative populate file.
